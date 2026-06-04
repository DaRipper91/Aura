import requests
import json
from typing import Generator, Optional

class OllamaClient:
    MODELS = {
        "phi3:mini": {
            "name": "Phi-3 Mini (Reasoning)",
            "system": "You are Phi, a highly analytical and logical assistant. Focus on structured reasoning and concise, accurate answers."
        },
        "gemma2:2b": {
            "name": "Gemma 2 2B (Creative)",
            "system": "You are Gemma, a creative and expressive assistant. Use rich language and focus on imaginative and engaging responses."
        },
        "qwen2.5-coder:1.5b": {
            "name": "Qwen 2.5 Coder (Coding)",
            "system": "You are Qwen, an expert software engineer. Provide high-quality code, technical explanations, and focus on best practices."
        }
    }

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def stream_chat(self, model: str, prompt: str) -> Generator[str, None, None]:
        url = f"{self.base_url}/api/generate"
        system_prompt = self.MODELS.get(model, {}).get("system", "")
        
        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": prompt,
            "stream": True
        }
        
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
