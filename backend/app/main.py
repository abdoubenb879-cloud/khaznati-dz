"""
Khaznati DZ - Main Application

FastAPI application entry point.
خزنتي - تطبيق التخزين السحابي الجزائري
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Khaznati DZ...")
    await create_tables()
    print("✅ Database tables ready")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Khaznati DZ...")


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


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
    }


# Root redirect (for API-only mode)
@app.get("/", tags=["System"])
async def root():
    """Root endpoint - API info."""
    return {
        "name": "Khaznati DZ API",
        "name_ar": "خزنتي",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else None,
        "message": "مرحباً بك في خزنتي!",  # Welcome to Khaznati!
    }


# =============================================================================
# Static Files (for frontend - will be mounted later)
# =============================================================================

# Uncomment when frontend is ready:
# app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
