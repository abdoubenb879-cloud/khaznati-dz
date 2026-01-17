"""
Khaznati DZ - Main Application

FastAPI application entry point.
خزنتي - تطبيق التخزين السحابي الجزائري
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.api import api_router
from app.services.telegram_service import telegram_storage


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Khaznati DZ...")
    
    # Initialize and start Telegram Storage
    try:
        print("🤖 Initializing Telegram Storage...")
        telegram_storage.connect()
        print("✅ Telegram Storage ready")
    except Exception as e:
        print(f"❌ Failed to start Telegram Storage: {e}")
        # We don't exit, maybe it's a temporary connection issue
    
    print("✅ Application started and ready")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Khaznati DZ...")
    try:
        telegram_storage.stop()
        print("✅ Telegram Storage stopped")
    except:
        pass


# Create FastAPI application
app = FastAPI(
    title="Khaznati DZ",
    description="خزنتي - تطبيق التخزين السحابي الجزائري | Your Algerian-Friendly Cloud Drive",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)


# =============================================================================
# Middleware
# =============================================================================

# Session middleware for auth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    session_cookie="khaznati_session",
    max_age=settings.session_expire_minutes * 60,
    same_site="lax",
    https_only=settings.is_production,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    # Log the error (in production, send to monitoring)
    print(f"Unhandled error: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "حدث خطأ غير متوقع",  # An unexpected error occurred
            "success": False,
        }
    )


# =============================================================================
# Routes
# =============================================================================

# API routes
app.include_router(api_router, prefix="/api")


# =============================================================================
# Frontend Serving (Single Service Mode)
# =============================================================================

# Path to the frontend build directory
# Since we start in 'backend', frontend is in '../frontend/dist'
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.exists(frontend_path):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    # Mount assets (js, css, etc.)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    # Catch-all route to serve index.html for SPA (React)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Exclude /api routes
        if full_path.startswith("api/"):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Not Found"}
            )
        
        # Check if requested path is a file in the frontend dir
        file_request = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_request):
            return FileResponse(file_request)
            
        # Otherwise serve index.html (SPA routing)
        return FileResponse(os.path.join(frontend_path, "index.html"))

else:
    # Fallback for API-only mode
    @app.get("/", tags=["System"])
    async def root():
        """Root endpoint - API info."""
        return {
            "name": "Khaznati DZ API",
            "name_ar": "خزنتي",
            "version": "1.0.0",
            "docs": "/api/docs" if settings.debug else None,
            "message": "Front-end distribution not found. API is running.",
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
