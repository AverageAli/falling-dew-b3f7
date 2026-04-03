from sqlalchemy.orm import Session

from app.database.models import ConversationSession, Message
from app.services.ai_service import AIService


class AssistantService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService(db)

    def get_or_create_session(self, telegram_user_id: int, language: str = 'en') -> ConversationSession:
        session = self.db.query(ConversationSession).filter_by(telegram_user_id=telegram_user_id).first()
        if not session:
            session = ConversationSession(telegram_user_id=telegram_user_id, language=language)
            self.db.add(session)
            self.db.commit()
        return session

    def reply(self, telegram_user_id: int, text: str, medical: bool = False, language: str = 'en') -> str:
        session = self.get_or_create_session(telegram_user_id, language)
        self.db.add(Message(session_id=session.id, role='user', content=text, mode='medical' if medical else 'assistant'))

        if medical:
            response = self.ai.medical_qa(text, lang=language).text
        else:
            response = self.ai.route('assistant_reply', message=text).text

        self.db.add(Message(session_id=session.id, role='assistant', content=response, mode='medical' if medical else 'assistant'))
        session.summary = self.ai.route('summarize', text=f'{session.summary}\n{text}\n{response}').text[:1500]
        self.db.commit()
        return response
