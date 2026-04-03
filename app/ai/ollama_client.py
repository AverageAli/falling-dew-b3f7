import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings


class OllamaClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def generate(self, prompt: str) -> str:
        payload = {'model': self.model, 'prompt': prompt, 'stream': False}
        response = httpx.post(f'{self.base_url}/api/generate', json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get('response', '').strip()
