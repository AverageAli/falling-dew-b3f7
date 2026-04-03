import asyncio
import structlog
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config import get_settings
from app.database.session import SessionLocal
from app.services.assistant_service import AssistantService
from app.services.rate_limit_service import InMemoryRateLimiter

logger = structlog.get_logger(__name__)
settings = get_settings()
rate_limiter = InMemoryRateLimiter(settings.rate_limit_per_minute)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! I am your AI assistant. Use /medical for safe medical Q&A mode.')


async def medical_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['medical_mode'] = True
    await update.message.reply_text('Medical mode enabled for this chat. Ask your question.')


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not rate_limiter.allowed(user_id):
        await update.message.reply_text('Rate limit exceeded. Please try in a minute.')
        return

    medical = context.user_data.get('medical_mode', False)
    text = update.message.text

    with SessionLocal() as db:
        service = AssistantService(db)
        reply = service.reply(user_id, text, medical=medical)

    await update.message.reply_text(reply[:4000])


async def run_bot() -> None:
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('medical', medical_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    logger.info('telegram_bot_starting')
    await app.run_polling(drop_pending_updates=True)


def run_bot_sync() -> None:
    asyncio.run(run_bot())
