from sqlalchemy.orm import Session

from app.database.models import PromptTemplate


class PromptService:
    def __init__(self, db: Session):
        self.db = db

    def render(self, key: str, **kwargs: str) -> str:
        template = self.db.query(PromptTemplate).filter_by(key=key).first()
        if not template:
            raise ValueError(f'Missing prompt template: {key}')
        return template.body.format(**kwargs)
