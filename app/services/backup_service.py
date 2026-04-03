import json
from pathlib import Path
from sqlalchemy.orm import Session

from app.database.models import Post, PromptTemplate, Setting


class BackupService:
    def __init__(self, db: Session):
        self.db = db

    def export_json(self, path: str) -> str:
        data = {
            'posts': [
                {'id': p.id, 'title': p.title, 'body': p.body, 'status': p.status, 'version': p.version}
                for p in self.db.query(Post).all()
            ],
            'prompts': [{'key': p.key, 'body': p.body} for p in self.db.query(PromptTemplate).all()],
            'settings': [{'key': s.key, 'value': s.value} for s in self.db.query(Setting).all()],
        }
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return path

    def import_json(self, path: str) -> None:
        payload = json.loads(Path(path).read_text(encoding='utf-8'))
        for prompt in payload.get('prompts', []):
            existing = self.db.query(PromptTemplate).filter_by(key=prompt['key']).first()
            if existing:
                existing.body = prompt['body']
        self.db.commit()
