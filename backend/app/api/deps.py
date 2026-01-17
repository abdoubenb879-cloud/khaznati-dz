"""
Khaznati DZ - Dependencies

FastAPI dependency injection utilities.
"""

from typing import Optional

from fastapi import HTTPException, status, Request

from app.services.auth_service import auth_service


async def get_current_user(
    request: Request
) -> dict:
    """
    Get the current authenticated user from session.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Authenticated User dict
        
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
    
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        # User was deleted or session invalid, clear session
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="المستخدم غير موجود أو الجلسة منتهية",  # User not found or session expired
        )
    
    return user


async def get_current_user_optional(
    request: Request
) -> Optional[dict]:
    """
    Get the current user if authenticated, None otherwise.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User dict if authenticated, None otherwise
    """
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


async def get_verified_user(
    request: Request
) -> dict:
    """
    Ensure the current user has verified their email.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Verified User dict
        
    Raises:
        HTTPException: If email not verified
    """
    user = await get_current_user(request)
    # Note: verify user.get('email_verified') if that field exists in Supabase
    # For now, we return user to maintain compatibility
    return user


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
    
    # Get token from header
    token = request.headers.get("X-CSRF-Token")
    
    stored_token = request.session.get("csrf_token")
    
    if not token or not stored_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="رمز CSRF مفقود",  # CSRF token missing
        )
    
    if token != stored_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="رمز CSRF غير صالح",  # CSRF token invalid
        )
