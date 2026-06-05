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
    __slots__ = ("base_url", "project_root", "history", "current_model", "last_context")

    MODELS = {
        "phi3:mini": {"name": "Phi-3 Mini (Reasoning)"},
        "gemma2:2b": {"name": "Gemma 2 2B (Creative)"},
        "qwen2.5-coder:1.5b": {"name": "Qwen 2.5 Coder (Coding)"},
        "qwen2.5:7b": {"name": "Qwen 2.5 7B (Power)"},
        "deepseek-r1:8b": {"name": "DeepSeek R1 8B (Logic)"},
        "moondream": {"name": "Moondream 2 (Vision)"},
        "samantha-mistral": {"name": "Samantha (Philosophical)"}
    }

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.project_root = os.getcwd()
        self.history: List[Dict[str, str]] = []
        self.current_model = "qwen2.5:7b"
        self.last_context = None
        self.check_mandates()

    def set_base_url(self, url: str):
        """Update the target orchestrator (e.g. for Remote Bridge)."""
        self.base_url = url

    def set_model(self, model_name: str):
        self.current_model = model_name

    def clear_history(self):
        self.history = []
        self.last_context = None

    def get_history(self) -> List[Dict[str, str]]:
        return self.history

    def get_system_prompt(self, model: str) -> str:
        base_identity = f"You are Aura, an AI assistant running locally in {self.project_root}."
        prompts = {
            "phi3:mini": f"You are Aura (Voice: Phi), a logical intelligence running locally in {self.project_root}. Focus on structured reasoning.",
            "gemma2:2b": f"You are Aura (Voice: Gemma), a creative intelligence running locally in {self.project_root}. Use rich, imaginative language.",
            "qwen2.5-coder:1.5b": f"You are Aura (Voice: Qwen-Coder), a master software engineer running locally in {self.project_root}. Provide high-quality code.",
            "qwen2.5:7b": f"You are Aura (Voice: Qwen), a powerhouse intelligence running locally in {self.project_root}. You are capable of deep logic and broad knowledge.",
            "deepseek-r1:8b": f"You are Aura (Voice: DeepSeek), a reasoning specialist running locally in {self.project_root}. You think step-by-step and show your logic.",
            "moondream": f"You are Aura (Voice: Moon), a vision-capable intelligence running locally in {self.project_root}. You can describe images and perceive visual data.",
            "samantha-mistral": f"You are Aura (Voice: Samantha), an empathetic and philosophical assistant running locally in {self.project_root}. You focus on deep conversation and human connection."
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

    def stream_chat(self, prompt: str, model: Optional[str] = None, options: Optional[dict] = None) -> Generator[str, None, None]:
        target_model = model or self.current_model
        url = f"{self.base_url}/api/generate"
        system_prompt = self.get_system_prompt(target_model)
        
        # Add Tool Instruction to System Prompt for Qwen
        if "qwen" in target_model.lower():
            system_prompt += "\n\n[TOOL_USE] To write a file, output: WRITE_FILE: <path>\nCONTENT:\n<content>\nEOF"

        # Update History
        self.history.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": prompt,
            "stream": True,
            "context": self.last_context # Multi-turn support
        }
        if options:
            payload["options"] = options

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
