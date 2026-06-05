import json
from typing import Generator

class AuraEngine:
    """
    Pure Python Core Engine.
    Stripped of all UI/Terminal logic. Agnostic design ready for Ollama, Gemini, Claude, or Codex.
    """
    def __init__(self, use_local=True):
        self.use_local = use_local
        self.history = []
        
    def stream_chat(self, prompt: str, model: str = "default") -> Generator[str, None, None]:
        self.history.append({"role": "user", "content": prompt})
        
        # In full implementation, this connects to Ollama/APIs.
        # For structural demonstration of the bridge, we yield a simulated stream.
        simulated_response = [f"Simulated ", f"response ", f"from ", f"{model}..."]
        
        full_response = ""
        for chunk in simulated_response:
            full_response += chunk
            yield chunk
            
        self.history.append({"role": "assistant", "content": full_response})
