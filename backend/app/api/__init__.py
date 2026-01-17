"""
Khaznati DZ - API Routes

All API route modules.
"""

from fastapi import APIRouter
from app.api.routes import auth, files, folders, trash

from app.services.telegram_service import telegram_storage
from app.core.config import settings

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
        "storage": "connected" if telegram_storage._connected else "disconnected"
    }

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(files.router)
api_router.include_router(folders.router)
api_router.include_router(trash.router)
# api_router.include_router(share.router)
