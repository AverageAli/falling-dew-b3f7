from datetime import datetime
import structlog
from telegram import Bot

from app.config import get_settings
from app.database.models import JobRun, Post
from app.database.session import SessionLocal
from app.services.content_service import ContentService

logger = structlog.get_logger(__name__)
settings = get_settings()


def generate_daily_drafts() -> None:
    with SessionLocal() as db:
        svc = ContentService(db)
        svc.create_content_calendar(days=14)
        posts = svc.generate_variants(topic='daily growth strategy', count=2)
        db.add(JobRun(job_name='generate_daily_drafts', status='success', details=f'generated={len(posts)}'))
        db.commit()


def publish_scheduled_posts() -> None:
    now = datetime.utcnow()
    bot = Bot(token=settings.telegram_bot_token)
    with SessionLocal() as db:
        posts = (
            db.query(Post)
            .filter(Post.status.in_(['approved', 'scheduled']), Post.scheduled_for.is_not(None), Post.scheduled_for <= now)
            .all()
        )
        for post in posts:
            try:
                bot.send_message(chat_id=settings.telegram_channel_id, text=f"{post.hook}\n\n{post.body}\n\n{post.hashtags}\n{post.cta}")
                post.status = 'published'
                post.published_at = now
            except Exception as exc:  # noqa: BLE001
                logger.error('publish_failed', post_id=post.id, error=str(exc))
        db.add(JobRun(job_name='publish_scheduled_posts', status='success', details=f'published={len(posts)}'))
        db.commit()
