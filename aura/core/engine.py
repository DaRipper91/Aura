import requests
import json
import os
from typing import Generator, Optional

from aura.core.mandates import aura_component

@aura_component
class OllamaClient:
    __slots__ = ("base_url", "project_root")
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.project_root = os.getcwd()
        self.check_mandates()

    MODELS = {
        "phi3:mini": {"name": "Phi-3 Mini (Reasoning)"},
        "gemma2:2b": {"name": "Gemma 2 2B (Creative)"},
        "qwen2.5-coder:1.5b": {"name": "Qwen 2.5 Coder (Coding)"},
        "qwen2.5:7b": {"name": "Qwen 2.5 7B (Power)"},
        "deepseek-r1:8b": {"name": "DeepSeek R1 8B (Logic)"},
        "moondream": {"name": "Moondream 2 (Vision)"},
        "samantha-mistral": {"name": "Samantha (Philosophical)"}
    }

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

    def stream_chat(self, model: str, prompt: str, options: Optional[dict] = None) -> Generator[str, None, None]:
        url = f"{self.base_url}/api/generate"
        system_prompt = self.get_system_prompt(model)
        
        # Add Tool Instruction to System Prompt for Qwen
        if "qwen" in model:
            system_prompt += "\n\n[TOOL_USE] You can modify files. To write or update a file, output exactly: \nWRITE_FILE: <path>\nCONTENT:\n<content>\nEOF\n\nEnsure the path is relative to the project root."

        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": prompt,
            "stream": True
        }

        if options:
            payload["options"] = options
        
        try:
            response = requests.post(url, json=payload, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        yield chunk["response"]
                    if chunk.get("done"):
                        break
        except Exception as e:
            yield f"\n[Error connecting to Ollama: {str(e)}]"
