from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import whiteboard as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    caps = await svc.list_captures(db)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Whiteboard Digitizer", "captures": caps})

@router.post("/ui/captures")
async def ui_cap(title: str = Form(...), hint_text: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.create_capture(db, title, hint_text)
    return RedirectResponse("/", status_code=303)
