from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import whiteboard as svc

class CaptureIn(BaseModel):
    title: str = Field(min_length=2)
    hint_text: str = Field(min_length=3, description="Simulated OCR source text")
    image_ref: str = "file://local.jpg"

router = APIRouter()

@router.post("/captures")
async def create_capture(payload: CaptureIn, db: AsyncSession = Depends(get_db)):
    cap = await svc.create_capture(db, payload.title, payload.hint_text, payload.image_ref)
    return {"id": cap.id, "status": cap.status}

@router.get("/captures")
async def list_captures(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_captures(db)
    return {"captures": [{"id": c.id, "title": c.title, "status": c.status} for c in rows]}

@router.post("/captures/{capture_id}/ocr")
async def ocr(capture_id: str, payload: CaptureIn, db: AsyncSession = Depends(get_db)):
    try:
        cap = await svc.run_ocr(db, capture_id, payload.hint_text)
        return {"id": cap.id, "status": cap.status}
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.get("/captures/{capture_id}/blocks")
async def blocks(capture_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_blocks(db, capture_id)
    return {"blocks": [{"id": b.id, "text": b.text, "confidence": b.confidence} for b in rows]}

@router.get("/captures/{capture_id}/export")
async def export_notes(capture_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await svc.export_structured(db, capture_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
