from datetime import datetime
from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    topic: str
    language: str = 'en'
    variant_count: int = Field(default=2, ge=1, le=5)


class AIResponse(BaseModel):
    text: str
    score: float = 0.0
    safe: bool = True


class HealthStatus(BaseModel):
    status: str
    timestamp: datetime
    components: dict[str, str]
