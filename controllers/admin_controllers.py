
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models.config_models import ApiKeys, Config, Context, Stats
from models.user_model import User
from models.chat_models import ChatLog
from db.init import SessionLocal

templates = Jinja2Templates(directory="templates")

admin_router = APIRouter(
    prefix="/admin",
)

@admin_router.post("/login")
def login( req: User):
    return {"user": req.username, "status": "logged in"}

@admin_router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Render the main dashboard"""
    try:
        db = SessionLocal()
        stats = db.query(Stats).first()
        config = db.query(Config).first()
        api_keys = db.query(ApiKeys).all()
    finally:
        db.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "config": config,
        "api_keys": api_keys,
    })

@admin_router.get("/logs", response_class=HTMLResponse)
async def logs(request: Request):
    """Render the logs page"""
    try:
        db = SessionLocal()
        logs = db.query(ChatLog).order_by(ChatLog.timestamp.desc()).limit(50).all()
    finally:
        db.close()

    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": logs,
    })  

@admin_router.get("/context", response_class=HTMLResponse)
async def context(request: Request):
    """Render the context page"""
    try:
        db = SessionLocal()
        context = db.query(Context).order_by(Context.timestamp.desc()).limit(50).all()
    finally:
        db.close()

    return templates.TemplateResponse("context.html", {
        "request": request,
        "context": context,
    })