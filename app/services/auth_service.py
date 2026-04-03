from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database.models import User

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def verify_user(self, username: str, password: str) -> User | None:
        user = self.db.query(User).filter_by(username=username).first()
        if not user:
            return None
        return user if pwd_context.verify(password, user.password_hash) else None
