from __future__ import annotations
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import BoardCapture, TextBlock
from backend.repositories import audit
from backend.utils.ids import short_id
from backend.vision.stubs import mock_ocr_lines

async def create_capture(session: AsyncSession, title: str, hint_text: str, image_ref: str = "file://local.jpg") -> BoardCapture:
    cap = BoardCapture(id=short_id(), title=title[:160], image_ref=image_ref[:240], status="queued")
    session.add(cap)
    await session.commit()
    await session.refresh(cap)
    audit.record("capture_created", cap.id)
    if hint_text.strip():
        await run_ocr(session, cap.id, hint_text)
    return cap

async def run_ocr(session: AsyncSession, capture_id: str, raw_text: str) -> BoardCapture:
    cap = await session.get(BoardCapture, capture_id)
    if not cap:
        raise ValueError("capture not found")
    cap.status = "processing"
    await session.commit()
    ocr_rows = mock_ocr_lines(raw_text)
    y = 0.0
    lines: list[str] = []
    for i, row in enumerate(ocr_rows):
        text = row["text"] if isinstance(row, dict) else str(row)
        conf = float(row.get("confidence", 0.8)) if isinstance(row, dict) else 0.8
        lines.append(text)
        session.add(
            TextBlock(
                id=short_id(),
                capture_id=capture_id,
                x=float(i % 3) * 0.2,
                y=y,
                text=text[:500],
                confidence=conf,
            )
        )
        y += 0.12
    cap.status = "done"
    cap.export_md = export_markdown(lines)
    await session.commit()
    await session.refresh(cap)
    return cap

def export_markdown(lines: list[str]) -> str:
    body = "\n".join(f"- {ln}" for ln in lines)
    return f"# Whiteboard notes\n\n{body}\n"

async def list_captures(session: AsyncSession) -> list[BoardCapture]:
    return list((await session.execute(select(BoardCapture).order_by(BoardCapture.created_at.desc()))).scalars())

async def list_blocks(session: AsyncSession, capture_id: str) -> list[TextBlock]:
    stmt = select(TextBlock).where(TextBlock.capture_id == capture_id).order_by(TextBlock.y)
    return list((await session.execute(stmt)).scalars())

async def export_structured(session: AsyncSession, capture_id: str) -> dict:
    cap = await session.get(BoardCapture, capture_id)
    if not cap:
        raise ValueError("capture not found")
    blocks = await list_blocks(session, capture_id)
    return {
        "capture_id": capture_id,
        "title": cap.title,
        "markdown": cap.export_md,
        "blocks": [
            {"id": b.id, "text": b.text, "x": b.x, "y": b.y, "confidence": b.confidence}
            for b in blocks
        ],
    }
