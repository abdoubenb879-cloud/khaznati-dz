"""
Khaznati DZ - API Routes

All API route modules.
"""

from fastapi import APIRouter
from app.api.routes import auth, files, folders, trash

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(files.router)
api_router.include_router(folders.router)
api_router.include_router(trash.router)
# api_router.include_router(share.router)
