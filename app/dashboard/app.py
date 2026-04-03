from datetime import datetime
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.init_db import init_db
from app.database.models import AppLog, JobRun, Message, Post, PromptTemplate
from app.database.session import get_db
from app.services.ai_service import AIService
from app.services.auth_service import AuthService
from app.services.backup_service import BackupService
from app.services.content_service import ContentService
from app.services.safety_service import medical_disclaimer

settings = get_settings()
app = FastAPI(title=settings.app_name)
security = HTTPBasic()
templates = Jinja2Templates(directory='app/dashboard/templates')
app.mount('/static', StaticFiles(directory='app/dashboard/static'), name='static')


@app.on_event('startup')
def startup() -> None:
    init_db()


def require_admin(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = AuthService(db).verify_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return user


@app.get('/health')
def health(db: Session = Depends(get_db)) -> dict:
    return {
        'status': 'ok',
        'time': datetime.utcnow().isoformat(),
        'database': 'ok' if db.execute(text('SELECT 1')).scalar() == 1 else 'down',
    }


@app.get('/', response_class=HTMLResponse)
def dashboard(request: Request, _: str = Depends(require_admin), db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(10).all()
    jobs = db.query(JobRun).order_by(JobRun.ran_at.desc()).limit(10).all()
    logs = db.query(AppLog).order_by(AppLog.created_at.desc()).limit(15).all()
    messages = db.query(Message).order_by(Message.created_at.desc()).limit(10).all()
    return templates.TemplateResponse('dashboard.html', {'request': request, 'posts': posts, 'jobs': jobs, 'logs': logs, 'messages': messages})


@app.post('/posts/generate')
def generate_post(topic: str = Form(...), db: Session = Depends(get_db), user=Depends(require_admin)):
    content_service = ContentService(db)
    content_service.generate_variants(topic=topic, count=2)
    return RedirectResponse('/', status_code=303)


@app.post('/posts/{post_id}/approve')
def approve_post(post_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    ContentService(db).approve_post(post_id)
    return RedirectResponse('/', status_code=303)


@app.get('/prompts', response_class=HTMLResponse)
def prompt_editor(request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    prompts = db.query(PromptTemplate).all()
    return templates.TemplateResponse('prompts.html', {'request': request, 'prompts': prompts})


@app.post('/prompts/{prompt_id}')
def update_prompt(prompt_id: int, body: str = Form(...), db: Session = Depends(get_db), user=Depends(require_admin)):
    prompt = db.query(PromptTemplate).filter_by(id=prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail='Prompt not found')
    prompt.body = body
    db.commit()
    return RedirectResponse('/prompts', status_code=303)


@app.get('/sandbox', response_class=HTMLResponse)
def prompt_sandbox(request: Request, key: str = 'assistant_reply', message: str = 'hello', db: Session = Depends(get_db), _: str = Depends(require_admin)):
    result = AIService(db).prompt_sandbox(key, {'message': message, 'topic': message, 'voice': 'professional', 'question': message, 'text': message, 'style': 'clear'})
    return templates.TemplateResponse('sandbox.html', {'request': request, 'result': result, 'disclaimer': medical_disclaimer('en')})


@app.get('/backup')
def backup(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    path = BackupService(db).export_json('backups/latest_backup.json')
    return {'backup_path': path}
