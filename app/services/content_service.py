from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database.models import ContentCalendar, Post
from app.services.ai_service import AIService


class ContentService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService(db)

    def generate_variants(self, topic: str, language: str = 'en', count: int = 2) -> list[Post]:
        created: list[Post] = []
        for idx in range(count):
            text = self.ai.route('post_generation', topic=topic, voice='professional').text
            content_hash = self.ai.content_hash(text)
            if self.db.query(Post).filter_by(content_hash=content_hash).first():
                continue
            post = Post(
                title=f'{topic.title()} Variant {idx + 1}',
                body=text,
                language=language,
                hashtags='#daily #telegram',
                hook='Start your day with this insight',
                cta='Share with a friend',
                engagement_score=self.ai.predict_engagement(text),
                content_hash=content_hash,
                ab_variant='A' if idx % 2 == 0 else 'B',
            )
            self.db.add(post)
            created.append(post)
        self.db.commit()
        return created

    def approve_post(self, post_id: int) -> Post:
        post = self.db.query(Post).get(post_id)
        if not post:
            raise ValueError('Post not found')
        post.status = 'approved'
        self.db.commit()
        return post

    def schedule_post(self, post_id: int, when: datetime) -> Post:
        post = self.db.query(Post).get(post_id)
        if not post:
            raise ValueError('Post not found')
        post.scheduled_for = when
        post.status = 'scheduled'
        self.db.commit()
        return post

    def create_content_calendar(self, days: int = 7) -> None:
        now = datetime.utcnow()
        for i in range(days):
            day = now + timedelta(days=i)
            if self.db.query(ContentCalendar).filter_by(day=day.replace(hour=0, minute=0, second=0, microsecond=0)).first():
                continue
            item = ContentCalendar(
                day=day.replace(hour=0, minute=0, second=0, microsecond=0),
                topic=f'Trend topic {i + 1}',
                priority=max(1, 5 - i),
                series='weekly-growth',
            )
            self.db.add(item)
        self.db.commit()
