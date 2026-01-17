"""
Khaznati DZ - Authentication Schemas

Pydantic models for authentication endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=128, description="Password")
    display_name: Optional[str] = Field(default=None, max_length=100, description="Display name")
    language: str = Field(default="ar", pattern="^(ar|fr|en)$", description="Preferred language")
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="Password")
    remember_me: bool = Field(default=False, description="Extend session duration")


class LoginResponse(BaseModel):
    """Login response with user info and CSRF token."""
    user: "UserPublic"
    csrf_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr = Field(description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation with token."""
    token: str = Field(description="Password reset token")
    new_password: str = Field(min_length=8, max_length=128, description="New password")
    
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordChangeRequest(BaseModel):
    """Password change request for authenticated users."""
    current_password: str = Field(description="Current password")
    new_password: str = Field(min_length=8, max_length=128, description="New password")
    
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserPublic(BaseModel):
    """Public user information (safe to expose)."""
    id: UUID
    email: str
    display_name: Optional[str]
    language: str
    email_verified: bool
    storage_used: int
    storage_quota: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserSettings(BaseModel):
    """User settings update request."""
    display_name: Optional[str] = Field(default=None, max_length=100)
    language: Optional[str] = Field(default=None, pattern="^(ar|fr|en)$")


class SessionInfo(BaseModel):
    """Session information."""
    id: UUID
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    last_activity_at: datetime
    is_current: bool = False
    
    class Config:
        from_attributes = True


# Rebuild model to handle forward reference
LoginResponse.model_rebuild()
