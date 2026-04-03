import json
from passlib.context import CryptContext

from app.config import get_settings
from app.database.base import Base
from app.database.models import PromptTemplate, User
from app.database.session import SessionLocal, engine

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

DEFAULT_PROMPTS = {
    'post_generation': 'Create a daily channel post about {topic} with brand voice {voice}.',
    'assistant_reply': 'Reply helpfully to user message: {message}',
    'medical_qa': 'Provide safe medical guidance with disclaimer for: {question}',
    'summarize': 'Summarize text:\n{text}',
    'rewrite': 'Rewrite this text in {style}:\n{text}',
    'moderation': 'Classify safety risk for message: {message}',
}


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    settings = get_settings()

    with SessionLocal() as db:
        if not db.query(User).filter_by(username=settings.admin_username).first():
            db.add(
                User(
                    username=settings.admin_username,
                    password_hash=pwd_context.hash(settings.admin_password),
                    role='admin',
                )
            )
        for key, body in DEFAULT_PROMPTS.items():
            if not db.query(PromptTemplate).filter_by(key=key).first():
                db.add(PromptTemplate(key=key, body=body, variables=json.dumps({})))
        db.commit()


if __name__ == '__main__':
    init_db()
