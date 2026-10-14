from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class BoardCapture(Base):
    __tablename__ = "board_captures"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    image_ref: Mapped[str] = mapped_column(String(240), default="file://local.jpg")
    status: Mapped[str] = mapped_column(String(24), default="queued", index=True)
    export_md: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class TextBlock(Base):
    __tablename__ = "text_blocks"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    capture_id: Mapped[str] = mapped_column(String(32), index=True)
    x: Mapped[float] = mapped_column(Float, default=0.0)
    y: Mapped[float] = mapped_column(Float, default=0.0)
    text: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.85)
