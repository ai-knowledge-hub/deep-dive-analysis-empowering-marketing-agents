import os, json, asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import httpx

load_dotenv()

class LLMClient:
    def __init__(self, provider: str, config: Dict[str, Any]):
        self.provider = provider
        self.config = config

    @classmethod
    def from_env(cls, llm_config: Dict[str, Any] = None):
        provider = os.getenv("LLM_PROVIDER", "dummy").lower()
        return cls(provider, llm_config or {})

    async def generate(self, prompt: str) -> str:
        if self.provider == "dummy":
            # Deterministic, JSON-friendly fallback
            # Returns a very simple structured response when the prompt asks for JSON.
            if "Return JSON" in prompt or "Return JSON with keys" in prompt:
                return json.dumps({
                    "message": "Here's a helpful next step based on your request.",
                    "actions": [{"type": "next_step", "details": "Start with a 25-minute focused session today."}],
                    "goal_updates": [],
                    "personalization_learned": {}
                })
            return "Helpful suggestion: break your goal into small daily steps."
        if self.provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                return "OpenAI API key not set."
            # Minimal call using openai-compatible endpoint (no SDK to keep deps light)
            url = "https://api.openai.com/v1/chat/completions"
            model = (self.config or {}).get("model", "gpt-4o-mini")
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    r = await client.post(
                        url,
                        headers={"Authorization": f"Bearer {key}"},
                        json={
                            "model": model,
                            "messages": [{"role":"user","content": prompt}],
                            "temperature": (self.config or {}).get("temperature", 0.3),
                        }
                    )
                data = r.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                return f"OpenAI error: {e}"
        if self.provider == "ollama":
            base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            model = os.getenv("OLLAMA_MODEL", "llama3")
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    r = await client.post(
                        f"{base}/api/generate",
                        json={"model": model, "prompt": prompt}
                    )
                # Ollama returns a streaming-like JSONL; but /api/generate returns a JSON object with 'response'
                try:
                    data = r.json()
                    if "response" in data:
                        return data["response"]
                except Exception:
                    return r.text
            except Exception as e:
                return f"Ollama error: {e}"
        return "Unsupported LLM provider."
