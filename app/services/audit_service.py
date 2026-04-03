from sqlalchemy.orm import Session
from app.database.models import AuditLog


def record_audit(db: Session, actor: str, action: str, target: str, details: str = '') -> None:
    db.add(AuditLog(actor=actor, action=action, target=target, details=details))
    db.commit()
