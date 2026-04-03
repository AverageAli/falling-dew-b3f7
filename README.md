# Telegram Bot Platform (FastAPI + Telegram + Ollama)

Production-oriented Python platform for:
- Daily Telegram channel content automation
- Private AI assistant in DMs
- Safe medical Q&A mode with disclaimers and red-flag escalation
- Admin dashboard for operations, prompt editing, analytics, and backups

## Project Structure

```text
app/
  ai/
    ollama_client.py
  bot/
    telegram_bot.py
  dashboard/
    app.py
    templates/
      dashboard.html
      prompts.html
      sandbox.html
  database/
    base.py
    init_db.py
    models.py
    session.py
  scheduler/
    jobs.py
    scheduler.py
  schemas/
    common.py
  services/
    ai_service.py
    assistant_service.py
    auth_service.py
    audit_service.py
    backup_service.py
    content_service.py
    prompt_service.py
    rate_limit_service.py
    safety_service.py
  utils/
    logging.py
  config.py
  main.py
prompts/
  assistant_reply.txt
  medical_qa.txt
  post_generation.txt
scripts/
  start.py
tests/
  test_content.py
  test_safety.py
requirements.txt
.env.example
```

## Features Implemented

- Channel automation: draft variants, approval, scheduling, duplicate prevention, A/B variant tagging, engagement scoring.
- Assistant: session memory, bilingual behavior via prompting, summarization updates.
- Medical safety: disclaimer injection, red-flag detection, uncertainty-oriented prompt.
- Dashboard: basic-auth authentication, post generation/approval, prompt editor, prompt sandbox, backup endpoint, recent jobs/messages/logs view.
- Scheduler: persistent APScheduler jobs backed by SQLAlchemy job store.
- Reliability: structured JSON logging, retries for Ollama calls, health endpoint, rate limiting.
- Migration-ready ORM and default SQLite support; PostgreSQL ready by changing `DATABASE_URL`.

## Setup

1. Create virtualenv and install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure env:
   ```bash
   cp .env.example .env
   ```
3. Ensure Ollama is running and model exists:
   ```bash
   ollama pull qwen2.5:7b
   ollama serve
   ```
4. Initialize DB:
   ```bash
   python -m app.database.init_db
   ```

## Run (One Command)

```bash
python scripts/start.py
```

This starts:
- FastAPI dashboard on `http://localhost:8000`
- Telegram bot polling
- APScheduler background jobs

## Health Check

```bash
curl http://localhost:8000/health
```

## Backup / Restore

- Export backup: `GET /backup` (creates `backups/latest_backup.json`)
- Restore example usage in Python:

```python
from app.database.session import SessionLocal
from app.services.backup_service import BackupService

with SessionLocal() as db:
    BackupService(db).import_json('backups/latest_backup.json')
```

## Testing

```bash
pytest -q
```
