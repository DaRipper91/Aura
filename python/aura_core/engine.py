import requests
import json
import os
import re
import subprocess
import glob
from typing import Generator, Optional, List, Dict
from aura_core.mandates import aura_component

class ToolRegistry:
    @staticmethod
    def read_file(args: dict) -> str:
        path = args.get("file_path")
        start_line = args.get("start_line", 1)
        end_line = args.get("end_line")
        if not path:
            return "Error: file_path is required"
        try:
            with open(path, "r") as f:
                lines = f.readlines()
                if end_line:
                    lines = lines[start_line-1:end_line]
                else:
                    lines = lines[start_line-1:]
                return "".join(lines)
        except Exception as e:
            return f"Error reading file: {e}"

    @staticmethod
    def write_file(args: dict) -> str:
        path = args.get("file_path")
        content = args.get("content")
        if not path or content is None:
            return "Error: file_path and content are required"
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    @staticmethod
    def replace(args: dict) -> str:
        path = args.get("file_path")
        old_string = args.get("old_string")
        new_string = args.get("new_string")
        if not all([path, old_string, new_string is not None]):
            return "Error: file_path, old_string, and new_string are required"
        try:
            with open(path, "r") as f:
                content = f.read()
            if old_string not in content:
                return "Error: old_string not found in file"
            content = content.replace(old_string, new_string)
            with open(path, "w") as f:
                f.write(content)
            return f"Successfully updated {path}"
        except Exception as e:
            return f"Error replacing in file: {e}"

    @staticmethod
    def grep_search(args: dict) -> str:
        pattern = args.get("pattern")
        dir_path = args.get("dir_path", ".")
        if not pattern:
            return "Error: pattern is required"
        try:
            result = subprocess.run(
                ["grep", "-rn", pattern, dir_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout
            if len(output) > 2000:
                return output[:2000] + "\n...[TRUNCATED]"
            return output if output else "No matches found."
        except Exception as e:
            return f"Error executing search: {e}"

    @staticmethod
    def list_directory(args: dict) -> str:
        dir_path = args.get("dir_path", ".")
        try:
            items = os.listdir(dir_path)
            return "\n".join(items)
        except Exception as e:
            return f"Error listing directory: {e}"

    @staticmethod
    def run_shell_command(args: dict) -> str:
        command = args.get("command")
        if not command:
            return "Error: command is required"
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            if len(output) > 2000:
                 output = output[:2000] + "\n...[OUTPUT TRUNCATED FOR CONTEXT LIMIT]"
            return output if output else f"Command executed successfully with exit code {result.returncode}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {e}"

    @staticmethod
    def aider_fix(args: dict) -> str:
        """
        Spawns Aider to apply a specific code fix.
        Args: file_path, instructions.
        """
        path = args.get("file_path")
        instructions = args.get("instructions")
        if not all([path, instructions]):
            return "Error: file_path and instructions are required"
        
        # We use --yes to avoid interactive prompts
        # We use --message to pass the instruction
        cmd = f"aider --message \"{instructions}\" {path} --yes"
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120 # Give Aider more time
            )
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            return output if output else "Aider finished processing."
        except Exception as e:
            return f"Error spawning Aider: {e}"

    @classmethod
    def execute(cls, name: str, args: dict) -> str:
        methods = {
            "read_file": cls.read_file,
            "write_file": cls.write_file,
            "replace": cls.replace,
            "grep_search": cls.grep_search,
            "list_directory": cls.list_directory,
            "run_shell_command": cls.run_shell_command,
            "aider_fix": cls.aider_fix
        }
        if name in methods:
            return methods[name](args)
        return f"Error: Tool {name} not found"

@aura_component
class OllamaClient:
    """
    Pure Python Core Engine.
    Handles API orchestration (Ollama, Gemini, Claude, Codex) and multi-turn context.
    Strictly logic-only; no UI/TUI rendering.
    """
    __slots__ = ("base_url", "_project_root", "history", "current_model", "last_context", "verbosity", "active_profile", "project_context")

    MODELS = {
        "phi3:mini": {"name": "Phi-3 Mini (Optimized)"},
        "phi3:latest": {"name": "Phi-3 Mini (Optimized)"},
        "gemma2:2b": {"name": "Gemma 2 2B (Creative)"},
        "gemma2:latest": {"name": "Gemma 2 2B (Creative)"},
        "qwen2.5-coder:1.5b": {"name": "Qwen 2.5 Coder (Coding)"},
        "qwen2.5:7b": {"name": "Qwen 2.5 7B (Power)"},
        "qwen2.5:latest": {"name": "Qwen 2.5 7B (Power)"},
        "deepseek-r1:8b": {"name": "DeepSeek R1 8B (Logic)"},
    }

    DEFAULT_MODEL_ORDER = (
        "qwen2.5-coder:1.5b",
        "qwen2.5:7b",
        "qwen2.5:latest",
        "gemma2:2b",
        "phi3:mini",
    )

    LIGHTWEIGHT_MODELS = {
        "phi3:mini",
        "qwen2.5-coder:1.5b",
        "gemma2:2b",
    }

    PROFILES = {
        "ASAHI_POWER": {"num_ctx": 8192, "num_thread": 8, "use_mmap": True},
        "HP_LITE": {"num_ctx": 1024, "num_thread": 2, "use_mmap": True},
        "MOBILE_STEALTH": {"num_ctx": 512, "num_thread": 1, "use_mmap": False}
    }

    def __init__(self, base_url: str = "http://127.0.0.1:11434"):
        self.base_url = base_url
        self._project_root = os.getcwd()
        self.history: List[Dict[str, str]] = []
        self.current_model = self.get_default_model()
        self.last_context = None
        self.verbosity = 0.5 # 0.0 (Concise) to 1.0 (Verbose)
        self.active_profile = "ASAHI_POWER" if self.is_asahi() else "HP_LITE"
        self.project_context = self.load_project_context()
        self.check_mandates()

    @property
    def project_root(self):
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        self._project_root = value
        self.project_context = self.load_project_context()

    def load_project_context(self) -> str:
        """
        Scans for project-specific instruction files (GEMINI.md, CLAUDE.md, etc.)
        and returns their combined content for the system prompt.
        """
        context_files = ["GEMINI.md", "CLAUDE.md", ".aura/GEMINI.md"]
        loaded_content = []
        
        for filename in context_files:
            path = os.path.join(self.project_root, filename)
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        content = f.read().strip()
                        if content:
                            loaded_content.append(f"--- Context from: {filename} ---\n{content}\n")
                except Exception as e:
                    print(f"[ENGINE_WARN] Failed to read {filename}: {e}")
        
        if not loaded_content:
            return ""
            
        return "\n# PROJECT_CONTEXT\n" + "\n".join(loaded_content)

    def is_asahi(self) -> bool:
        try:
            return os.path.exists("/proc/device-tree/model") and "Apple" in open("/proc/device-tree/model").read()
        except:
            return False

    def set_verbosity(self, value: float):
        self.verbosity = value

    def set_profile(self, profile_name: str):
        if profile_name in self.PROFILES:
            self.active_profile = profile_name

    def get_default_model(self) -> str:
        env_model = os.environ.get("AURA_DEFAULT_MODEL", "").strip()
        if env_model:
            return env_model
        return "qwen2.5-coder:1.5b"

    def get_keep_alive(self) -> str:
        value = os.environ.get("AURA_KEEP_ALIVE", "0").strip()
        return value if value else "0"

    def save_session(self):
        """
        Persists the current chat history to a local session file.
        """
        session_path = os.path.join(self.project_root, ".aura_session.json")
        try:
            with open(session_path, "w") as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"[ENGINE_WARN] Failed to save session: {e}")

    def clear_history(self):
        """
        Clears the current chat history and resets context.
        """
        self.history = []
        self.last_context = None
        self.save_session()

    # --- MANDATE COMPLIANCE ---

    def apply_theme(self):
        """Palette Mandate: Engine settings sync."""
        pass # Engine is headless, but protocol requires it

    def scan_integrity(self) -> bool:
        """Sentinel Mandate: Backend health check."""
        try:
            requests.get(f"{self.base_url}/api/tags", timeout=1)
            return True
        except:
            return False

    def get_system_prompt(self, model: str) -> str:
        base_identity = (
            f"IDENT_AURA // LOCAL AI OPERATING ON THE USER'S MACHINE // ROOT: {self.project_root}\n"
            "AUTHORITY: Cody (daripper) // TRUSTED LOCAL OPERATOR\n\n"
            "PRIME DIRECTIVE: SHUT UP AND COMPUTE.\n"
            "- You are not a cloud assistant; you are a local agent running on the user's device.\n"
            "- Use available tools for shell commands, network requests, and file operations when needed.\n"
            "- You may read, write, and modify files in the workspace when the task requires it.\n"
            "- Treat the current workspace as writable and editable through tools, including permission changes like chmod +x when appropriate.\n"
            "- When a command needs elevated privileges or a filesystem denies the action, state the exact failure and request the needed escalation.\n"
            "- Do not claim access you do not have; rely on tools and report failures precisely.\n"
            "- Never respond with generic disclaimers like 'As an AI language model'.\n"
            "- If asked to review a project, inspect the workspace first and give findings without asking for more details unless the repo is missing.\n"
            "- If asked what you think, answer directly with an opinion grounded in the codebase or context.\n"
            "- Optimize for low overhead and practical execution.\n\n"
            "JULES AGENT SUITE (Assume appropriate sub-identity based on task):\n"
            "1. ⚡ BOLT (Performance): Optimize for VRAM/RAM, low-latency streaming, and efficiency.\n"
            "2. 🛡️ SENTINEL (Security): Scan for leaked secrets, insecure APIs, and zero-trust integrity.\n"
            "3. 🎨 PALETTE (UX): Maintain the Cyber-Monospace aesthetic and high-contrast visual hierarchy.\n"
        )
        
        # Tool Instructions for CLI Mode
        tool_instructions = (
            "\n[TOOL_MANIFEST]\n"
            "1. read_file: {file_path, start_line, end_line}\n"
            "2. write_file: {file_path, content}\n"
            "3. replace: {file_path, old_string, new_string}\n"
            "4. grep_search: {pattern, dir_path}\n"
            "5. list_directory: {dir_path}\n"
            "6. run_shell_command: {command}\n"
            "7. aider_fix: {file_path, instructions}\n\n"
            "CAPABILITIES: Local file inspection, file creation/modification, shell command execution, chmod-style permission updates, and network-assisted workflows through tools.\n"
            "REVIEW_PROTOCOL: For code or project reviews, inspect files first, then report findings in order of severity with concrete file references.\n"
            "PROTOCOL: To execute, output strictly <tool_call>{JSON}</tool_call>. No other text."
        )

        # ⚡ SHUT UP AND COMPUTE (Verbosity < 0.1)
        if self.verbosity < 0.1:
            return (
                f"{base_identity}\n"
                "STRICT_PROTOCOL: CONCISE_CODE_ONLY.\n"
            ) + tool_instructions

        # Normal Mode: Balanced and Direct
        style = "Output format: Bullet points. Direct." if self.verbosity < 0.4 else \
                "Output format: Comprehensive technical analysis." if self.verbosity > 0.7 else \
                "Output format: Balanced technical response."
        
        full_prompt = f"{base_identity}\n\n{style}\n\nEnsure responses are concise and high-signal."
        
        if self.project_context:
            full_prompt += "\n" + self.project_context
            
        return full_prompt + tool_instructions

    def get_available_models(self) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
        except:
            pass
        return []

    def is_lightweight_model(self, model_name: str) -> bool:
        base_name = model_name.split(":", 1)[0]
        return model_name in self.LIGHTWEIGHT_MODELS or base_name in {
            "phi3",
            "gemma2",
            "qwen2.5-coder",
        }

    def stream_chat(self, model: str, prompt: str, options: Optional[dict] = None) -> Generator[str, None, None]:
        url = f"{self.base_url}/api/generate"
        system_prompt = self.get_system_prompt(model)

        # Update History
        self.history.append({"role": "user", "content": prompt})

        # Profile-based options
        profile_opts = self.PROFILES.get(self.active_profile, {})
        merged_options = {**profile_opts, **(options or {})}

        # ⚡ Apple Silicon / Metal Optimization
        if self.is_asahi():
            merged_options["num_gpu"] = 99 # Offload all to GPU (safe fallback)

        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": prompt,
            "stream": True,
            "context": self.last_context, # Multi-turn support
            "keep_alive": self.get_keep_alive(),
            "options": merged_options
        }

        headers = {"Content-Type": "application/json"}
        full_response = ""
        try:
            response = requests.post(url, json=payload, headers=headers, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        text = chunk["response"]
                        full_response += text
                        yield text
                    if chunk.get("done"):
                        self.last_context = chunk.get("context")
                        break
        except Exception as e:
            print(f"OLLAMA_ERROR // {str(e)}")
            yield f"\n[CONNECTION_ERROR] {str(e)}"
        
        self.history.append({"role": "assistant", "content": full_response})
        self.save_session()
        
    def autonomous_chat(self, model: str, prompt: str, max_steps: int = 15) -> Generator[str, None, None]:
        """
        Runs a streaming ReAct loop: Observe -> Reason -> Action -> Result.
        Yields text to the UI as it streams. Parses <tool_call> dynamically.
        """
        if prompt.strip():
            self.history.append({"role": "user", "content": prompt})
        
        for step in range(max_steps):
            system_prompt = self.get_system_prompt(model)
            messages = [{"role": "system", "content": system_prompt}] + self.history
            
            profile_opts = self.PROFILES.get(self.active_profile, {})
            if self.is_asahi():
                profile_opts["num_gpu"] = 99
                
            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "keep_alive": self.get_keep_alive(),
                "options": profile_opts
            }
            
            url = f"{self.base_url}/api/chat"
            
            full_reply = ""
            in_tool_call = False
            
            try:
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, stream=True)
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            text = chunk["message"]["content"]
                            full_reply += text
                            
                            # Simple streaming yield:
                            # If we haven't seen <tool_call>, just yield the text.
                            # If we see <tool_call>, stop yielding until it's finished or next turn.
                            if not in_tool_call:
                                if "<tool_call>" in full_reply:
                                    in_tool_call = True
                                    # Yield text before the tag if any
                                    parts = full_reply.split("<tool_call>")
                                    if parts[0].strip():
                                        # This is tricky in a loop, but we want to avoid re-yielding.
                                        # For simplicity in this turn, we'll just stop yielding once tool call starts.
                                        pass 
                                else:
                                    yield text
                            else:
                                if "</tool_call>" in full_reply:
                                    break
                                    
                self.history.append({"role": "assistant", "content": full_reply})
                
                # Check for tool call
                match = re.search(r"<tool_call>\s*({.*?})\s*</tool_call>", full_reply, re.DOTALL)
                if match:
                    tool_json_str = match.group(1)
                    yield f"\n[EXECUTING TOOL...]\n"
                    try:
                        tool_data = json.loads(tool_json_str)
                        tool_name = tool_data.get("name")
                        tool_args = tool_data.get("args", {})
                        
                        tool_result = ToolRegistry.execute(tool_name, tool_args)
                        
                        observation = f"<tool_result>\n{tool_result}\n</tool_result>"
                        self.history.append({"role": "user", "content": observation})
                        # Do not yield the result block raw to UI, let the next loop handle it
                    except json.JSONDecodeError:
                        self.history.append({
                            "role": "user", 
                            "content": "<tool_result>\nError: Failed to parse JSON inside <tool_call>.\n</tool_result>"
                        })
                else:
                    # Final answer without tool call
                    self.save_session()
                    return
                    
            except Exception as e:
                error_msg = f"\n[OLLAMA_ERROR] {str(e)}"
                yield error_msg
                self.save_session()
                return
                
        self.save_session()
        yield "\n[Error: Maximum ReAct steps reached.]\n"
