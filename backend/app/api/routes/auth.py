"""
Khaznati DZ - Authentication API Routes

Endpoints for user registration, login, logout.
Uses Supabase for user storage.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
import secrets

from app.core.config import settings
from app.services.auth_service import auth_service
from app.core.security import create_csrf_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user_id(request: Request) -> str:
    """Get the current user ID from session."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="غير مسموح - يرجى تسجيل الدخول"  # Unauthorized - please login
        )
    return user_id


def get_current_user(request: Request) -> dict:
    """Get the current user from session."""
    user_id = get_current_user_id(request)
    user = auth_service.get_user_by_id(user_id)
    if not user:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="جلسة غير صالحة"  # Invalid session
        )
    return user


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(request: Request):
    """
    Register a new user account.
    
    Body:
    - **email**: Valid email address (must be unique)
    - **password**: At least 8 characters
    - **display_name**: Optional display name
    - **language**: Preferred language (ar, fr, en)
    """
    body = await request.json()
    
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    display_name = body.get("display_name", "")
    language = body.get("language", "ar")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="البريد الإلكتروني وكلمة المرور مطلوبان"
        )
    
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="كلمة المرور يجب أن تكون 8 أحرف على الأقل"
        )
    
    user = auth_service.create_user(
        email=email,
        password=password,
        display_name=display_name,
        language=language
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="البريد الإلكتروني مستخدم بالفعل"  # Email already in use
        )
    
    # Set session
    user_id = user.get("telegram_id")
    request.session["user_id"] = user_id
    request.session["csrf_token"] = create_csrf_token()
    
    return {
        "message": "تم إنشاء الحساب بنجاح",  # Account created successfully
        "user": {
            "id": user_id,
            "email": user.get("email"),
            "name": user.get("name") or user.get("username"),
        }
    }


@router.post(
    "/login",
    summary="Login to existing account"
)
async def login(request: Request):
    """
    Authenticate with email and password.
    """
    body = await request.json()
    
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="البريد الإلكتروني وكلمة المرور مطلوبان"
        )
    
    user = auth_service.authenticate(email, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة"  # Invalid credentials
        )
    
    # Set session
    user_id = user.get("telegram_id")
    request.session["user_id"] = user_id
    request.session["csrf_token"] = create_csrf_token()
    
    return {
        "message": "تم تسجيل الدخول بنجاح",  # Logged in successfully
        "user": {
            "id": user_id,
            "email": user.get("email"),
            "name": user.get("name") or user.get("username"),
        }
    }


@router.post(
    "/logout",
    summary="Logout current user"
)
async def logout(request: Request):
    """End the current session and logout."""
    request.session.clear()
    
    return {
        "message": "تم تسجيل الخروج بنجاح",  # Logged out successfully
        "success": True
    }


@router.get(
    "/me",
    summary="Get current user info"
)
async def get_me(request: Request):
    """Get the currently authenticated user's information."""
    user = get_current_user(request)
    
    return {
        "id": user.get("telegram_id"),
        "email": user.get("email"),
        "name": user.get("name") or user.get("username"),
        "is_premium": user.get("is_premium", False),
    }


@router.post(
    "/change-password",
    summary="Change password"
)
async def change_password(request: Request):
    """Change the current user's password."""
    user = get_current_user(request)
    body = await request.json()
    
    current_password = body.get("current_password", "")
    new_password = body.get("new_password", "")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="كلمة المرور الحالية والجديدة مطلوبتان"
        )
    
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="كلمة المرور الجديدة يجب أن تكون 8 أحرف على الأقل"
        )
    
    user_id = user.get("telegram_id")
    success = auth_service.change_password(user_id, current_password, new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="كلمة المرور الحالية غير صحيحة"  # Current password incorrect
        )
    
    return {"message": "تم تغيير كلمة المرور بنجاح", "success": True}


@router.get(
    "/csrf-token",
    summary="Get CSRF token for forms"
)
async def get_csrf_token(request: Request):
    """Get a CSRF token for form submissions."""
    csrf_token = request.session.get("csrf_token")
    
    if not csrf_token:
        csrf_token = create_csrf_token()
        request.session["csrf_token"] = csrf_token
    
    return {"csrf_token": csrf_token}
