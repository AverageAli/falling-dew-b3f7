from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import get_settings
from app.scheduler.jobs import generate_daily_drafts, publish_scheduled_posts

settings = get_settings()


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(
        timezone=settings.timezone,
        jobstores={'default': SQLAlchemyJobStore(url=settings.database_url)},
        executors={'default': ThreadPoolExecutor(10)},
    )
    scheduler.add_job(generate_daily_drafts, 'cron', hour=8, minute=0, id='daily_generation', replace_existing=True)
    scheduler.add_job(publish_scheduled_posts, 'interval', minutes=5, id='scheduled_publish', replace_existing=True)
    return scheduler
