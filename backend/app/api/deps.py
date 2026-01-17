"""
Khaznati DZ - Dependencies

FastAPI dependency injection utilities.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_csrf_token
from app.models.user import User
from app.services.auth_service import AuthService


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from session.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Authenticated User
        
    Raises:
        HTTPException: If not authenticated
    """
    user_id = request.session.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="غير مسجل الدخول",  # Not logged in
            headers={"WWW-Authenticate": "Session"},
        )
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="جلسة غير صالحة",  # Invalid session
        )
    
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_uuid)
    
    if not user:
        # User was deleted, clear session
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="المستخدم غير موجود",  # User not found
        )
    
    return user


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, None otherwise.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        User if authenticated, None otherwise
    """
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None


async def get_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure the current user has verified their email.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Verified User
        
    Raises:
        HTTPException: If email not verified
    """
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="يرجى تأكيد بريدك الإلكتروني أولاً",  # Please verify email first
        )
    return current_user


async def verify_csrf(request: Request) -> None:
    """
    Verify CSRF token for state-changing requests.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If CSRF token invalid
    """
    # Skip for GET, HEAD, OPTIONS
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    
    # Get token from header or form
    token = request.headers.get("X-CSRF-Token")
    if not token:
        # Try form data
        form = await request.form()
        token = form.get("csrf_token")
    
    stored_token = request.session.get("csrf_token")
    
    if not token or not stored_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="رمز CSRF مفقود",  # CSRF token missing
        )
    
    if not verify_csrf_token(token, stored_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="رمز CSRF غير صالح",  # CSRF token invalid
        )
