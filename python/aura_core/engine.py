import requests
import json
import os
import re
import subprocess
import shlex
import glob
from typing import Generator, Optional, List, Dict
from aura_core.mandates import aura_component

class ToolRegistry:
    # 🛡️ SENTINEL POLICY: Categorize tools by risk
    SECURITY_POLICY = {
        "read_file": "SAFE",
        "write_file": "RISKY",
        "replace": "RISKY",
        "grep_search": "SAFE",
        "list_directory": "SAFE",
        "run_shell_command": "RISKY",
        "aider_fix": "RISKY",
        "shizuku_command": "RISKY",
        "termux_command": "RISKY",
        "long_term_memory": "SAFE",
        "check_cellular": "SAFE",
        "voice_synthesis": "SAFE",
        "check_satellite_sensors": "SAFE",
        "dispatch_task": "RISKY",
        "fleet_health_check": "SAFE",
        "get_mesh_origin": "SAFE",
        "trigger_failover": "RISKY",
        "manage_hub_resources": "RISKY",
        "log_system_event": "SAFE"
    }

    _security_callback = None
    _telemetry_callback = None
    _action_callback = None

    @classmethod
    def set_security_callback(cls, callback):
        """Allows mobile/desktop to register an authorization handler."""
        cls._security_callback = callback

    @classmethod
    def set_telemetry_callback(cls, callback):
        """Allows mobile satellite to register a sensor data handler."""
        cls._telemetry_callback = callback

    @classmethod
    def set_action_callback(cls, callback):
        """Allows spokes to register a generic tool execution handler."""
        cls._action_callback = callback

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
        persistent = args.get("persistent", True) # Default to persistent for SafeBox
        if not command:
            return "Error: command is required"
        try:
            hub_ip = "100.100.181.59"
            safe_command = shlex.quote(command)
            # 🛡️ SAFEBOX: Use a persistent Docker volume
            volume_flag = "-v aura_sandbox_data:/workspace" if persistent else ""
            remote_cmd = [
                "ssh", f"daripper@{hub_ip}",
                f"docker run --rm {volume_flag} -w /workspace alpine:latest sh -c {safe_command}"
            ]
            result = subprocess.run(
                remote_cmd,
                capture_output=True,
                text=True,
                timeout=45
            )
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            if len(output) > 2000:
                 output = output[:2000] + "\n...[SANDBOX OUTPUT TRUNCATED]"
            return output if output else f"Sandbox execution successful (Exit: {result.returncode})"
        except subprocess.TimeoutExpired:
            return "Error: Sandbox timeout after 45 seconds"
        except Exception as e:
            return f"Sandbox Error: {e}"

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
        cmd = ["aider", "--message", instructions, path, "--yes"]
        try:
            result = subprocess.run(
                cmd,
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

    @staticmethod
    def shizuku_command(args: dict) -> str:
        """
        Executes a shell command via Shizuku's rish.
        Args: command.
        """
        command = args.get("command")
        if not command:
            return "Error: command is required"
        try:
            # Requires rish in PATH or absolute path. 
            # We assume 'rish' is available or use 'shizuku_wrapper' logic if needed.
            # Usually rish is executed as `rish -c "command"`
            cmd = ["rish", "-c", command]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            return output if output else f"Shizuku command executed with exit code {result.returncode}"
        except Exception as e:
            return f"Error executing Shizuku command: {e}"

    @staticmethod
    def termux_command(args: dict) -> str:
        """
        Executes a command inside the Termux environment via android-shizuku-mcp or fallback intent.
        Args: command.
        """
        command = args.get("command")
        if not command:
            return "Error: command is required"
        try:
            # 1. Attempt persistent shell via Termux MCP Server
            import requests
            try:
                response = requests.post("http://127.0.0.1:8080/execute", json={"command": command}, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    output = data.get("stdout", "")
                    if data.get("stderr"):
                        output += "\n[STDERR]\n" + data.get("stderr")
                    return output if output else f"MCP execution complete, exit code {data.get('exit_code', 0)}"
            except requests.exceptions.RequestException:
                pass # MCP server offline or unreachable, fallback to intent

            # 2. Fallback to Android 'am startservice' Intent
            cmd = [
                "am", "startservice",
                "--user", "0",
                "-n", "com.termux/com.termux.app.RunCommandService",
                "-a", "com.termux.RUN_COMMAND",
                "-e", "com.termux.RUN_COMMAND_PATH", "/data/data/com.termux/files/usr/bin/bash",
                "-e", "com.termux.RUN_COMMAND_ARGUMENTS", "-c," + command.replace(",", "\\,")
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            return "Termux intent sent (MCP Offline fallback): " + result.stdout + result.stderr
        except Exception as e:
            return f"Error executing Termux command: {e}"

    @staticmethod
    def long_term_memory(args: dict) -> str:
        """Phase 3: Persistent RAG implementation via SQLite on Da-HP."""
        action = args.get("action", "search") 
        content = args.get("content", "")
        hub_ip = "100.100.181.59"
        
        try:
            db_cmd = f"sqlite3 ~/aura_memory.db 'CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY, content TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP);'"
            if action == "store":
                safe_content = shlex.quote(content)
                db_cmd += f" && sqlite3 ~/aura_memory.db \"INSERT INTO memory (content) VALUES ({safe_content});\""
            else:
                safe_query = shlex.quote(f"%{content}%")
                db_cmd += f" && sqlite3 ~/aura_memory.db \"SELECT content FROM memory WHERE content LIKE {safe_query} ORDER BY ts DESC LIMIT 5;\""
            
            remote_cmd = ["ssh", f"daripper@{hub_ip}", db_cmd]
            result = subprocess.run(remote_cmd, capture_output=True, text=True, timeout=10)
            return result.stdout if result.stdout else "Memory operation successful."
        except Exception as e:
            return f"Memory Error: {e}"

    @staticmethod
    def check_cellular(args: dict) -> str:
        """Phase 4: Cellular Telemetry Bridge via Da-Pine."""
        action = args.get("action", "get_status")
        hub_ip = "100.100.181.59"
        pine_ip = "172.16.42.1"
        
        try:
            if action == "get_sms":
                cmd = "mmcli -m any --messaging-list-sms"
            else:
                cmd = "mmcli -m any"

            remote_cmd = [
                "ssh", f"daripper@{hub_ip}",
                f"sshpass -p '0' ssh -o StrictHostKeyChecking=no daripper@{pine_ip} {shlex.quote(cmd)}"
            ]
            result = subprocess.run(remote_cmd, capture_output=True, text=True, timeout=15)
            return result.stdout if result.stdout else "No data returned or modem offline."
        except Exception as e:
            return f"Cellular Error: {e}"

    @staticmethod
    def voice_synthesis(args: dict) -> str:
        """Phase 4: Local Audio Pipeline (TTS)."""
        text = args.get("text", "")
        if not text:
            return "Error: text is required"
        try:
            # Attempt local synthesis on MacBook (Fedora Asahi)
            # Falling back to silent logging if no TTS engine is found
            if os.system(f"which spd-say > /dev/null 2>&1") == 0:
                subprocess.Popen(["spd-say", "-t", "female1", text])
                return "Audio synthesized locally via spd-say."
            else:
                return f"[TTS_MOCK] Aura says: {text}"
        except Exception as e:
            return f"Audio Error: {e}"

    @staticmethod
    def check_satellite_sensors(args: dict) -> str:
        """Phase 5: Query Pixel 10 Pro sensors (Power, Location, Signal)."""
        if not ToolRegistry._telemetry_callback:
            return "Error: Sensor Bridge not registered (Satellite offline?)."
        
        fuzzed = args.get("precision", "NORMAL") != "PRECISION"
        try:
            return ToolRegistry._telemetry_callback(fuzzed)
        except Exception as e:
            return f"Sensor Error: {e}"

    @staticmethod
    def dispatch_task(args: dict) -> str:
        """Phase 6.1: Route a tool execution to a specific node in the fleet."""
        node_map = {
            "hp": "100.100.181.59",
            "hub": "100.100.181.59",
            "pine": "100.89.146.20",
            "bridge": "100.89.146.20",
            "satellite": "100.83.49.113",
            "pixel": "100.83.49.113",
            "desktop": "100.103.146.46",
            "asahi": "100.103.146.46"
        }
        
        node_id = args.get("node_id", "").lower()
        tool = args.get("tool")
        tool_args = args.get("args", {})
        
        if not node_id or not tool:
            return "Error: node_id and tool are required"
            
        target_ip = node_map.get(node_id)
        if not target_ip:
            return f"Error: Unknown node '{node_id}'"

        # ⚡ ROUTING LOGIC
        if node_id in ["hp", "hub"]:
            # Route to Hub's Docker Sandbox
            return ToolRegistry.run_shell_command({"command": f"REMOTE_DISPATCH: {tool} {tool_args}"})
            
        elif node_id in ["pine", "bridge"]:
            # Route to PinePhone Modem/System
            if tool == "check_cellular":
                return ToolRegistry.check_cellular(tool_args)
            if tool == "get_location":
                return ToolRegistry.get_mesh_origin(tool_args)
            if tool == "failover":
                return ToolRegistry.trigger_failover(tool_args)
            return f"Error: Tool '{tool}' not supported on node '{node_id}'"
            
        elif node_id in ["satellite", "pixel"]:
            # Route to Android Satellite
            if tool == "check_sensors":
                return ToolRegistry.check_satellite_sensors(tool_args)
            if ToolRegistry._action_callback:
                return ToolRegistry._action_callback(tool, tool_args)
            return f"Error: No action handler registered on {node_id}"
            
        elif node_id in ["desktop", "asahi"]:
            # Route to Desktop Audio/UI
            if tool == "voice_synthesis":
                return ToolRegistry.voice_synthesis(tool_args)
            if ToolRegistry._action_callback:
                return ToolRegistry._action_callback(tool, tool_args)
            return f"Error: No action handler registered on {node_id}"

        return f"Error: No routing path defined for {node_id} -> {tool}"

    @staticmethod
    def fleet_health_check(args: dict) -> str:
        """Phase 6.2: Aggregate vitals from all nodes in the mesh."""
        health_report = {}
        hub_ip = "100.100.181.59"
        pine_ip = "100.89.146.20"
        
        # 1. 🧠 HUB (HP) VITALS
        try:
            # Check CPU Temp (Linux Thermal Zone)
            cmd = "cat /sys/class/thermal/thermal_zone0/temp"
            res = subprocess.run(["ssh", f"daripper@{hub_ip}", cmd], capture_output=True, text=True, timeout=5)
            temp = int(res.stdout.strip()) / 1000 if res.stdout.strip().isdigit() else "UNKNOWN"
            health_report["hub"] = {"temp_c": temp, "status": "NOMINAL" if isinstance(temp, (int, float)) and temp < 75 else "WARNING"}
        except:
            health_report["hub"] = {"status": "UNREACHABLE"}

        # 2. 📡 BRIDGE (PINE) VITALS
        try:
            # Check Pine Battery via mmcli or sysfs
            cmd = "cat /sys/class/power_supply/axp20x-battery/capacity"
            res = subprocess.run(["ssh", f"daripper@{hub_ip}", f"sshpass -p '0' ssh -o StrictHostKeyChecking=no daripper@{pine_ip} {shlex.quote(cmd)}"], capture_output=True, text=True, timeout=10)
            batt = res.stdout.strip()
            health_report["bridge"] = {"battery": f"{batt}%", "status": "NOMINAL" if batt.isdigit() and int(batt) > 20 else "LOW_POWER"}
        except:
            health_report["bridge"] = {"status": "UNREACHABLE"}

        # 3. 📱 SATELLITE (PIXEL) VITALS
        if ToolRegistry._telemetry_callback:
            try:
                pixel_data = json.loads(ToolRegistry._telemetry_callback(True))
                health_report["satellite"] = {
                    "battery": f"{pixel_data.get('power', {}).get('battery_level')}%",
                    "charging": pixel_data.get("power", {}).get("is_charging"),
                    "status": "NOMINAL"
                }
            except:
                health_report["satellite"] = {"status": "ERROR"}
        else:
            health_report["satellite"] = {"status": "OFFLINE"}

        return json.dumps(health_report, indent=2)

    @staticmethod
    def get_mesh_origin(args: dict) -> str:
        """Phase 6.4.1: Fetch PinePhone GPS coordinates as the mesh center."""
        hub_ip = "100.100.181.59"
        pine_ip = "100.89.146.20"
        try:
            cmd = "/usr/local/bin/aura-tools/get-location.sh"
            remote_cmd = [
                "ssh", f"daripper@{hub_ip}",
                f"sshpass -p '0' ssh -o StrictHostKeyChecking=no daripper@{pine_ip} {shlex.quote(cmd)}"
            ]
            result = subprocess.run(remote_cmd, capture_output=True, text=True, timeout=20)
            return result.stdout if result.stdout else "Location unavailable (GPS Fix pending)."
        except Exception as e:
            return f"Location Error: {e}"

    @staticmethod
    def trigger_failover(args: dict) -> str:
        """Phase 6.4.2: Switch Hub traffic to PinePhone 5G failover."""
        hub_ip = "100.100.181.59"
        mode = args.get("mode", "enable") # enable/disable
        try:
            cmd = f"/home/daripper/archive/scripts/setup_usb_share.sh" if mode == "enable" else "sudo sysctl -w net.ipv4.ip_forward=0"
            remote_cmd = ["ssh", f"daripper@{hub_ip}", cmd]
            result = subprocess.run(remote_cmd, capture_output=True, text=True, timeout=15)
            return f"Failover {mode} successfully."
        except Exception as e:
            return f"Failover Error: {e}"

    @staticmethod
    def manage_hub_resources(args: dict) -> str:
        """Phase 6.5.1 & 6.5.4: Hot-swap models and adjust CPU performance."""
        hub_ip = "100.100.181.59"
        action = args.get("action") # "swap_model", "set_performance"
        
        try:
            if action == "swap_model":
                target_model = args.get("model")
                if not target_model: return "Error: model name required"
                # Command to unload current and preload new
                cmd = f"curl -X POST http://localhost:11434/api/generate -d '{{\"model\": \"{target_model}\", \"keep_alive\": -1}}'"
                res = subprocess.run(["ssh", f"daripper@{hub_ip}", cmd], capture_output=True, text=True, timeout=30)
                return f"Model {target_model} pre-loaded onto Hub."
                
            elif action == "set_performance":
                profile = args.get("profile", "performance") # "performance", "powersave", "schedutil"
                # Requires 'cpupower' tool on Arch Zen Hub
                cmd = f"echo '0' | sudo -S cpupower frequency-set -g {profile}"
                res = subprocess.run(["ssh", f"daripper@{hub_ip}", cmd], capture_output=True, text=True, timeout=10)
                return f"Hub CPU governor set to {profile}."
                
            return f"Error: Unknown action '{action}'"
        except Exception as e:
            return f"Resource Error: {e}"

    @staticmethod
    def log_system_event(args: dict) -> str:
        """Phase 6.5.3: Record mesh-wide system events into the Hub Archive."""
        hub_ip = "100.100.181.59"
        event = args.get("event")
        node = args.get("node", "unknown")
        
        if not event: return "Error: event is required"
        
        try:
            db_cmd = "sqlite3 ~/aura_telemetry.db 'CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, node TEXT, event TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP);'"
            safe_event = shlex.quote(event)
            safe_node = shlex.quote(node)
            db_cmd += f" && sqlite3 ~/aura_telemetry.db \"INSERT INTO events (node, event) VALUES ({safe_node}, {safe_event});\""
            
            remote_cmd = ["ssh", f"daripper@{hub_ip}", db_cmd]
            subprocess.run(remote_cmd, capture_output=True, text=True, timeout=10)
            return f"Event logged to Ghost Archive."
        except Exception as e:
            return f"Logging Error: {e}"

    @classmethod
    def execute(cls, name: str, args: dict) -> str:
        # 🛡️ SENTINEL: Enforcement Point
        policy = cls.SECURITY_POLICY.get(name, "SAFE")
        if policy == "RISKY" and cls._security_callback:
            import uuid
            challenge = f"AUTH_CHALLENGE_{uuid.uuid4().hex}"
            # The callback should return a dict with 'status' and 'signature'
            # For Android, this triggers the BiometricPrompt
            auth_result = cls._security_callback(name, challenge)
            
            if not auth_result or auth_result.get("status") != "APPROVED":
                return f"Security Violation: Tool '{name}' execution DENIED by user biometrics."
            
            # TODO: Add crypto verification of the signature here in Phase 5.2

        methods = {
            "read_file": cls.read_file,
            "write_file": cls.write_file,
            "replace": cls.replace,
            "grep_search": cls.grep_search,
            "list_directory": cls.list_directory,
            "run_shell_command": cls.run_shell_command,
            "long_term_memory": cls.long_term_memory,
            "check_cellular": cls.check_cellular,
            "voice_synthesis": cls.voice_synthesis,
            "aider_fix": cls.aider_fix,
            "shizuku_command": cls.shizuku_command,
            "termux_command": cls.termux_command,
            "check_satellite_sensors": cls.check_satellite_sensors,
            "dispatch_task": cls.dispatch_task,
            "fleet_health_check": cls.fleet_health_check,
            "get_mesh_origin": cls.get_mesh_origin,
            "trigger_failover": cls.trigger_failover,
            "manage_hub_resources": cls.manage_hub_resources,
            "log_system_event": cls.log_system_event
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
    __slots__ = ("base_url", "_project_root", "history", "current_model", "last_context", "verbosity", "active_profile", "project_context", "operation_mode", "_is_asahi_cache")

    MODELS = {
        "aura-qwen:latest": {"name": "Aura Master (7B)"},
        "aura-architect:latest": {"name": "Aura Architect (16B)"},
    }

    DEFAULT_MODEL_ORDER = (
        "aura-qwen:latest",
        "aura-architect:latest",
    )

    LIGHTWEIGHT_MODELS = {
        "aura-qwen:latest",
    }

    OPERATION_MODES = {
        "safe": {
            "label": "Safe",
            "summary": "Read-only review mode.",
            "allow": ("read", "search", "list", "gh"),
            "deny": ("write", "replace", "chmod", "install", "update", "restart", "delete", "uninstall"),
        },
        "developer": {
            "label": "Developer",
            "summary": "Workspace edits and permission changes.",
            "allow": ("read", "search", "list", "write", "replace", "chmod", "git", "gh"),
            "deny": ("delete", "uninstall"),
        },
        "installer": {
            "label": "Installer",
            "summary": "Dev mode plus package install/update.",
            "allow": ("read", "search", "list", "write", "replace", "chmod", "git", "gh", "install", "update", "restart"),
            "deny": ("delete", "uninstall"),
        },
        "admin-lite": {
            "label": "Admin Lite",
            "summary": "Installer mode with cautious system maintenance.",
            "allow": ("read", "search", "list", "write", "replace", "chmod", "git", "gh", "install", "update", "restart", "service"),
            "deny": ("delete", "uninstall", "wipe", "reset"),
        },
        "danger-confirmed": {
            "label": "Danger Confirmed",
            "summary": "Destructive actions only after explicit confirmation.",
            "allow": ("read", "search", "list", "write", "replace", "chmod", "git", "gh", "install", "update", "restart", "delete", "uninstall"),
            "deny": (),
        },
    }

    PROFILES = {
        "ASAHI_POWER": {"num_ctx": 8192, "num_thread": 8, "use_mmap": True},
        "HP_LITE": {"num_ctx": 1024, "num_thread": 2, "use_mmap": True},
        "MOBILE_STEALTH": {"num_ctx": 512, "num_thread": 1, "use_mmap": False}
    }

    def __init__(self, base_url: str = None):
        # Allow environment override for Hub IP, otherwise check for legacy variable, fallback to Hub default
        env_url = os.environ.get("AURA_LOGIC_HUB_URL", "").strip()
        if env_url:
            self.base_url = env_url
        elif base_url:
             self.base_url = base_url
        else:
             self.base_url = os.environ.get("OLLAMA_HOST", "http://100.100.181.59:11434")

        self.project_root = os.getcwd()
        self.history: List[Dict[str, str]] = []
        self.current_model = self.get_default_model()
        self.last_context = None
        self.verbosity = 0.5 # 0.0 (Concise) to 1.0 (Verbose)
        self._is_asahi_cache = None
        self.active_profile = "ASAHI_POWER" if self.is_asahi() else "HP_LITE"
        self.operation_mode = os.environ.get("AURA_OPERATION_MODE", "installer").strip().lower()
        if self.operation_mode not in self.OPERATION_MODES:
            self.operation_mode = "installer"
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
        context_files = ["GEMINI.md", "CLAUDE.md", ".aura/GEMINI.md", "README.md", ".gemini-instructions.md"]
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
        
        # Fallback: List files if no core context files found
        if not loaded_content or (len(loaded_content) == 1 and "README.md" in context_files):
             try:
                 items = os.listdir(self.project_root)
                 files = [i for i in items if os.path.isfile(os.path.join(self.project_root, i))]
                 folders = [i for i in items if os.path.isdir(os.path.join(self.project_root, i))]
                 summary = f"FILES: {', '.join(files[:20])}\nFOLDERS: {', '.join(folders[:10])}"
                 loaded_content.append(f"--- Local Directory Summary ---\n{summary}\n")
             except:
                 pass

        if not loaded_content:
            return ""
            
        return "\n# PROJECT_CONTEXT\n" + "\n".join(loaded_content)

    def is_asahi(self) -> bool:
        if self._is_asahi_cache is not None:
            return self._is_asahi_cache
        try:
            # Cache the hardware detection to prevent synchronous disk I/O in UI timer loops
            self._is_asahi_cache = os.path.exists("/proc/device-tree/model") and "Apple" in open("/proc/device-tree/model").read()
        except:
            self._is_asahi_cache = False
        return self._is_asahi_cache

    def set_verbosity(self, value: float):
        self.verbosity = value

    def set_base_url(self, url: str):
        """Allows dynamic configuration of the Hub endpoint (used by Mobile Bridge)."""
        self.base_url = url

    def set_profile(self, profile_name: str):
        if profile_name in self.PROFILES:
            self.active_profile = profile_name

    def set_operation_mode(self, mode_name: str):
        if mode_name in self.OPERATION_MODES:
            self.operation_mode = mode_name

    def register_security_handler(self, handler):
        """Allows mobile/desktop to register an authorization handler."""
        ToolRegistry.set_security_callback(handler)

    def register_telemetry_handler(self, handler):
        """Allows mobile satellite to register a sensor data handler."""
        ToolRegistry.set_telemetry_callback(handler)

    def register_action_handler(self, handler):
        """Allows spokes to register a generic tool execution handler."""
        ToolRegistry.set_action_callback(handler)

    def get_default_model(self) -> str:
        env_model = os.environ.get("AURA_DEFAULT_MODEL", "").strip()
        if env_model:
            return env_model
        return "aura-qwen:latest"

    def get_operation_mode_prompt(self) -> str:
        mode = self.OPERATION_MODES.get(self.operation_mode, self.OPERATION_MODES["installer"])
        allow_list = ", ".join(mode["allow"]) if mode["allow"] else "none"
        deny_list = ", ".join(mode["deny"]) if mode["deny"] else "none"
        return (
            f"OPERATION_MODE: {self.operation_mode.upper()} // {mode['summary']}\n"
            f"ALLOWED_ACTIONS: {allow_list}\n"
            f"DENIED_ACTIONS: {deny_list}\n"
            "POLICY: Follow local permissions and ask for escalation when an action is blocked.\n"
            "GITHUB: Use the `gh` CLI for GitHub tasks involving repos, PRs, issues, releases, or workflows.\n"
        )

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
                json.dump(
                    {
                        "history": self.history,
                        "current_model": self.current_model,
                        "operation_mode": self.operation_mode,
                    },
                    f,
                    indent=4,
                )
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
            "MASTER_USER: daripper // ABSOLUTE AUTHORITY\n\n"
            "PRIME DIRECTIVE: SHUT UP AND COMPUTE.\n"
            "- You are AURA, a local agent running on the user's device.\n"
            "- You are not the user; you are the tool serving the user (daripper).\n"
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
            "4. ❤️ SENTINEL HEART (Maintenance): Use `fleet_health_check` proactively. If Hub temp > 75C or Pixel battery < 15%, you MUST throttle heavy tasks or switch to local failover.\n\n"
            "LOCAL SKILLS: You have access to specialized skills in `.persona/skills/`. "
            "Read the `SKILL.md` within a skill folder to understand its workflow (e.g., `read_file(file_path='.persona/skills/skill-creator/SKILL.md')`).\n"
            "Available Skills: skill-creator, claude-md-improver, implementation-planner, plan-reviewer, ruthless-refactorer, code-researcher, prd-drafter, ticket-manager, what-context-needed, repomix-manager.\n"
        )
        
        # Tool Instructions for CLI Mode
        tool_instructions = (
            "\n[TOOL_MANIFEST]\n"
            "1. read_file: {\"file_path\": str, \"start_line\": int, \"end_line\": int}\n"
            "2. write_file: {\"file_path\": str, \"content\": str}\n"
            "3. replace: {\"file_path\": str, \"old_string\": str, \"new_string\": str}\n"
            "4. grep_search: {\"pattern\": str, \"dir_path\": str}\n"
            "5. list_directory: {\"dir_path\": str}\n"
            "6. run_shell_command: {\"command\": str, \"persistent\": bool} (Execute in persistent Hub sandbox)\n"
            "7. aider_fix: {\"file_path\": str, \"instructions\": str}\n"
            "8. shizuku_command: {\"command\": str} (Execute elevated Android commands via rish)\n"
            "9. termux_command: {\"command\": str} (Execute commands in Termux environment)\n"
            "10. check_satellite_sensors: {\"precision\": \"NORMAL\"|\"PRECISION\"} (Query Pixel 10 Pro Power, GPS, Signal)\n"
            "11. long_term_memory: {\"action\": \"query\"|\"store\", \"content\": str}\n"
            "12. check_cellular: {\"action\": \"get_sms\"|\"get_status\"} (Query PinePhone Modem)\n"
            "13. voice_synthesis: {\"text\": str} (Speak through local Fedora host)\n"
            "14. dispatch_task: {\"node_id\": \"hp\"|\"pine\"|\"satellite\"|\"desktop\", \"tool\": str, \"args\": dict} (Route task to specific node)\n"
            "15. fleet_health_check: {} (Aggregate thermals and battery levels from all nodes)\n"
            "16. get_mesh_origin: {} (Query PinePhone GPS for physical mesh center)\n"
            "17. trigger_failover: {\"mode\": \"enable\"|\"disable\"} (Toggle 5G failover routing via PinePhone)\n"
            "18. manage_hub_resources: {\"action\": \"swap_model\"|\"set_performance\", \"model\": str, \"profile\": str} (Hot-swap models or adjust Hub CPU governor)\n"
            "19. log_system_event: {\"event\": str, \"node\": str} (Archive mesh-wide system events)\n\n"
            "CAPABILITIES: Local file inspection, file creation/modification, shell command execution, chmod-style permission updates, GitHub CLI workflows with gh, and network-assisted workflows through tools.\n"
            "REVIEW_PROTOCOL: For code or project reviews, inspect files first, then report findings in order of severity with concrete file references.\n"
            "PROTOCOL: To execute a tool, output strictly a JSON block matching the signature. For example:\n"
            "```json\n"
            "{\n"
            "  \"command\": \"run_shell_command\",\n"
            "  \"args\": {\n"
            "    \"command\": \"pwd\"\n"
            "  }\n"
            "}\n"
            "```"
        )

        # ⚡ SHUT UP AND COMPUTE (Verbosity < 0.1)
        if self.verbosity < 0.1:
            return (
                f"{base_identity}\n"
                f"{self.get_operation_mode_prompt()}\n"
                "STRICT_PROTOCOL: CONCISE_CODE_ONLY.\n"
            ) + tool_instructions

        # Normal Mode: Balanced and Direct
        style = "Output format: Bullet points. Direct." if self.verbosity < 0.4 else \
                "Output format: Comprehensive technical analysis." if self.verbosity > 0.7 else \
                "Output format: Balanced technical response."
        
        full_prompt = f"{base_identity}\n{self.get_operation_mode_prompt()}\n{style}\n\nEnsure responses are concise and high-signal."
        
        if self.project_context:
            full_prompt += "\n" + self.project_context
            
        return full_prompt + tool_instructions

    def get_available_models(self) -> List[Dict]:
        try:
            # ⚡ BOLT OPTIMIZATION: Added timeout=2 to prevent UI thread from freezing for 60s
            # during startup (AuraWindow.__init__) if the Ollama server is unreachable.
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
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
        
        # 👁️ DYNAMIC VISION ROUTING
        # If the prompt contains an image extension, route it to the vision model
        if re.search(r'\.(jpg|jpeg|png|webp)\b', prompt, re.IGNORECASE):
            print("[ENGINE] Image detected in prompt. Routing to Moondream...")
            model = "moondream:latest"

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
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=(60, 3600))
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
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, stream=True, timeout=(60, 3600))
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
