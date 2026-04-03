import threading
import uvicorn

from app.bot.telegram_bot import run_bot_sync
from app.config import get_settings
from app.dashboard.app import app
from app.scheduler.scheduler import build_scheduler
from app.utils.logging import configure_logging


def start_services() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    scheduler = build_scheduler()
    scheduler.start()

    bot_thread = threading.Thread(target=run_bot_sync, daemon=True)
    bot_thread.start()

    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    start_services()
