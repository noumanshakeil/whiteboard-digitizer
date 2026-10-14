from fastapi import APIRouter
from backend.api import health, whiteboard, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(whiteboard.router, prefix="/api", tags=["whiteboard"])
api_router.include_router(ui.router, tags=["ui"])
