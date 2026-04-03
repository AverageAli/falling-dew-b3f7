import hashlib
import json
from sqlalchemy.orm import Session

from app.ai.ollama_client import OllamaClient
from app.schemas.common import AIResponse
from app.services.prompt_service import PromptService
from app.services.safety_service import detect_red_flags, medical_disclaimer


class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OllamaClient()
        self.prompts = PromptService(db)

    def route(self, mode: str, **kwargs: str) -> AIResponse:
        prompt = self.prompts.render(mode, **kwargs)
        text = self.client.generate(prompt)
        score = min(1.0, len(text) / 1000)
        return AIResponse(text=text, score=score, safe=True)

    def medical_qa(self, question: str, lang: str = 'en') -> AIResponse:
        flags = detect_red_flags(question)
        reply = self.route('medical_qa', question=question).text
        if flags:
            reply += '\n\n🚨 Red flags detected: ' + ', '.join(flags) + '. Seek urgent care now.'
        reply += '\n\n' + medical_disclaimer(lang)
        return AIResponse(text=reply, score=0.95, safe=True)

    @staticmethod
    def content_hash(content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def predict_engagement(self, text: str) -> float:
        words = len(text.split())
        return round(min(100.0, 40 + words * 0.5), 2)

    def quality_score(self, text: str) -> float:
        return round(min(10.0, 3.0 + len(set(text.split())) / 20), 2)

    def prompt_sandbox(self, key: str, variables: dict[str, str]) -> dict[str, str]:
        prompt = self.prompts.render(key, **variables)
        return {'prompt': prompt, 'response': self.client.generate(prompt), 'variables': json.dumps(variables)}
