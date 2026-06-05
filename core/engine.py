import requests
import json
import os
from typing import Generator, Optional, List, Dict
from core.mandates import aura_component

@aura_component
class AuraEngine:
    """
    Pure Python Core Engine.
    Handles API orchestration (Ollama, Gemini, Claude, Codex) and multi-turn context.
    Strictly logic-only; no UI/TUI rendering.
    """
    __slots__ = ("base_url", "project_root", "history", "current_model")

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.project_root = os.getcwd()
        self.history: List[Dict[str, str]] = []
        self.current_model = "qwen2.5:7b"

    def set_model(self, model_name: str):
        self.current_model = model_name

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
        
        # Build System Prompt (Environmental Awareness)
        system_prompt = f"You are Aura, an AI assistant running in {self.project_root}. "
        if "qwen" in target_model.lower():
            system_prompt += "\n[TOOL_USE] To write a file, output: WRITE_FILE: <path>\nCONTENT:\n<content>\nEOF"

        # Update History
        self.history.append({"role": "user", "content": prompt})
        
        payload = {
            "model": target_model,
            "system": system_prompt,
            "prompt": prompt,
            "stream": True,
            "context": self._get_last_context() # Multi-turn support
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
                        # Save context for next turn
                        self.last_context = chunk.get("context")
                        break
        except Exception as e:
            yield f"\n[CONNECTION_ERROR] {str(e)}"
        
        self.history.append({"role": "assistant", "content": full_response})

    def _get_last_context(self):
        return getattr(self, 'last_context', None)
