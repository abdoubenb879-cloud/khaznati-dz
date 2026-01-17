"""
Khaznati DZ - Authentication API Routes

Endpoints for user registration, login, logout, and email verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_csrf_token
from app.core.config import settings
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    AuthResponse,
    MessageResponse,
)
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **password**: At least 8 characters with letters and numbers
    - **display_name**: Optional display name
    - **language**: Preferred language (ar, fr, en)
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.create_user(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Set session
    request.session["user_id"] = str(user.id)
    request.session["csrf_token"] = create_csrf_token()
    
    # TODO: Send verification email
    # await send_verification_email(user.email, user.email_verification_token)
    
    return AuthResponse(
        message="تم إنشاء الحساب بنجاح",  # Account created successfully
        user=UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            language=user.language,
            email_verified=user.email_verified,
            storage_quota=user.storage_quota,
            storage_used=user.storage_used,
            storage_remaining=user.storage_remaining,
            storage_percentage=user.storage_percentage,
            created_at=user.created_at,
        )
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login to existing account"
)
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate with email and password.
    
    - **email**: Registered email address
    - **password**: Account password
    - **remember_me**: Extend session to 30 days
    """
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate(data.email, data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة",  # Invalid email or password
        )
    
    # Set session
    request.session["user_id"] = str(user.id)
    request.session["csrf_token"] = create_csrf_token()
    
    # TODO: Handle remember_me with session expiry
    
    return AuthResponse(
        message="تم تسجيل الدخول بنجاح",  # Logged in successfully
        user=UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            language=user.language,
            email_verified=user.email_verified,
            storage_quota=user.storage_quota,
            storage_used=user.storage_used,
            storage_remaining=user.storage_remaining,
            storage_percentage=user.storage_percentage,
            created_at=user.created_at,
        )
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout current user"
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    End the current session and logout.
    """
    request.session.clear()
    
    return MessageResponse(
        message="تم تسجيل الخروج بنجاح",  # Logged out successfully
        success=True
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info"
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get the currently authenticated user's information.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        language=current_user.language,
        email_verified=current_user.email_verified,
        storage_quota=current_user.storage_quota,
        storage_used=current_user.storage_used,
        storage_remaining=current_user.storage_remaining,
        storage_percentage=current_user.storage_percentage,
        created_at=current_user.created_at,
    )


@router.post(
    "/verify-email/{token}",
    response_model=MessageResponse,
    summary="Verify email address"
)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email address using the token sent via email.
    """
    auth_service = AuthService(db)
    
    user = await auth_service.verify_email(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رابط التحقق غير صالح أو منتهي الصلاحية",  # Invalid or expired verification link
        )
    
    return MessageResponse(
        message="تم تأكيد البريد الإلكتروني بنجاح",  # Email verified successfully
        success=True
    )


@router.get(
    "/csrf-token",
    summary="Get CSRF token for forms"
)
async def get_csrf_token(request: Request):
    """
    Get a CSRF token for form submissions.
    Call this before making POST/PUT/DELETE requests.
    """
    csrf_token = request.session.get("csrf_token")
    
    if not csrf_token:
        csrf_token = create_csrf_token()
        request.session["csrf_token"] = csrf_token
    
    return {"csrf_token": csrf_token}
