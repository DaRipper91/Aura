import requests
import json
import os
from typing import Generator, Optional, List, Dict
from aura_core.mandates import aura_component

@aura_component
class OllamaClient:
    """
    Pure Python Core Engine.
    Handles API orchestration (Ollama, Gemini, Claude, Codex) and multi-turn context.
    Strictly logic-only; no UI/TUI rendering.
    """
    __slots__ = ("base_url", "project_root", "history", "current_model", "last_context", "verbosity", "active_profile")

    MODELS = {
        "phi3:mini": {"name": "Phi-3 Mini (Optimized)"},
        "gemma2:2b": {"name": "Gemma 2 2B (Creative)"},
        "qwen2.5-coder:1.5b": {"name": "Qwen 2.5 Coder (Coding)"},
        "qwen2.5:7b": {"name": "Qwen 2.5 7B (Power)"},
        "deepseek-r1:8b": {"name": "DeepSeek R1 8B (Logic)"},
        "moondream": {"name": "Moondream 2 (Vision)"},
        "samantha-mistral": {"name": "Samantha (Heavy/Philosophical)"}
    }

    PROFILES = {
        "ASAHI_POWER": {"num_ctx": 8192, "num_thread": 8, "f16_kv": True, "use_mmap": True, "use_mlock": True},
        "HP_LITE": {"num_ctx": 2048, "num_thread": 4, "f16_kv": False, "use_mmap": True, "use_mlock": False},
        "MOBILE_STEALTH": {"num_ctx": 1024, "num_thread": 2, "f16_kv": False, "use_mmap": False, "use_mlock": False}
    }

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.project_root = os.getcwd()
        self.history: List[Dict[str, str]] = []
        self.current_model = "phi3:mini"
        self.last_context = None
        self.verbosity = 0.5 # 0.0 (Concise) to 1.0 (Verbose)
        self.active_profile = "ASAHI_POWER" if self.is_asahi() else "HP_LITE"
        self.check_mandates()

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

    def get_system_prompt(self, model: str) -> str:
        base_identity = f"You are Aura, an AI assistant running locally in {self.project_root}."
        
        # Verbosity-aware identity
        style = "Be extremely concise. Use bullet points." if self.verbosity < 0.3 else \
                "Be thorough and explanatory." if self.verbosity > 0.7 else \
                "Be balanced and direct."
        
        prompts = {
            "phi3:mini": f"You are Aura (Voice: Phi), a logical intelligence. {style}",
            "gemma2:2b": f"You are Aura (Voice: Gemma), a creative intelligence. {style}",
            "qwen2.5-coder:1.5b": f"You are Aura (Voice: Qwen-Coder), a master software engineer. {style}",
            "qwen2.5:7b": f"You are Aura (Voice: Qwen), a powerhouse intelligence. {style}",
            "deepseek-r1:8b": f"You are Aura (Voice: DeepSeek), a reasoning specialist. {style}",
            "moondream": f"You are Aura (Voice: Moon), a vision-capable intelligence. {style}",
            "samantha-mistral": f"You are Aura (Voice: Samantha), an empathetic assistant. {style}"
        }
        return prompts.get(model, base_identity)

    def get_available_models(self) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
        except:
            pass
        return []

    def stream_chat(self, model: str, prompt: str, options: Optional[dict] = None) -> Generator[str, None, None]:
        url = f"{self.base_url}/api/generate"
        system_prompt = self.get_system_prompt(model)

        # Add Tool Instruction to System Prompt for Qwen
        if "qwen" in model.lower():
            system_prompt += "\n\n[TOOL_USE] To write a file, output: WRITE_FILE: <path>\nCONTENT:\n<content>\nEOF"

        # Update History
        self.history.append({"role": "user", "content": prompt})

        # Profile-based options
        profile_opts = self.PROFILES.get(self.active_profile, {})
        merged_options = {**profile_opts, **(options or {})}

        # ⚡ Apple Silicon / Metal Optimization
        if self.is_asahi():
            merged_options["num_gpu"] = 99 # Offload all to GPU
            merged_options["main_gpu"] = 0

        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": prompt,
            "stream": True,
            "context": self.last_context, # Multi-turn support
            "options": merged_options
        }

        full_response = ""
        try:
            response = requests.post(url, json=payload, stream=True)
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
            yield f"\n[CONNECTION_ERROR] {str(e)}"
        
        self.history.append({"role": "assistant", "content": full_response})
