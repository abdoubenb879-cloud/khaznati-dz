"""
Khaznati DZ - User Schemas

Pydantic schemas for user-related API operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# =============================================================================
# Request Schemas
# =============================================================================

class UserRegister(BaseModel):
    """Schema for user registration."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8-128 characters)"
    )
    display_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional display name"
    )
    language: str = Field(
        "ar",
        pattern="^(ar|fr|en)$",
        description="Preferred language (ar, fr, en)"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets minimum security requirements."""
        if len(v) < 8:
            raise ValueError("يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل")
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("يجب أن تحتوي كلمة المرور على حرف واحد على الأقل")
        if not re.search(r"\d", v):
            raise ValueError("يجب أن تحتوي كلمة المرور على رقم واحد على الأقل")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    remember_me: bool = Field(
        False,
        description="Extend session to 30 days"
    )


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    
    display_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Display name"
    )
    language: Optional[str] = Field(
        None,
        pattern="^(ar|fr|en)$",
        description="Preferred language"
    )


class PasswordChange(BaseModel):
    """Schema for changing password."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password"
    )
    
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure new password meets minimum security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    
    email: EmailStr = Field(..., description="User's email address")


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""
    
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password"
    )


# =============================================================================
# Response Schemas
# =============================================================================

class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    
    id: UUID
    email: EmailStr
    display_name: Optional[str]
    language: str
    email_verified: bool
    storage_quota: int
    storage_used: int
    storage_remaining: int
    storage_percentage: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Minimal public user info (for sharing, etc.)."""
    
    id: UUID
    display_name: Optional[str]
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for authentication responses."""
    
    message: str
    user: UserResponse


class MessageResponse(BaseModel):
    """Generic message response."""
    
    message: str
    success: bool = True
