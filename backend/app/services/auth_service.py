"""
Khaznati DZ - Authentication Service

Business logic for user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import (
    hash_password,
    verify_password,
    create_verification_token,
    verify_verification_token,
)


class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by email address.
        
        Args:
            email: User's email
            
        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Find a user by ID.
        
        Args:
            user_id: User's UUID
            
        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, data: UserRegister) -> User:
        """
        Create a new user account.
        
        Args:
            data: Registration data
            
        Returns:
            Created User instance
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email exists
        existing = await self.get_user_by_email(data.email)
        if existing:
            raise ValueError("البريد الإلكتروني مستخدم بالفعل")
        
        # Create verification token
        verification_token = create_verification_token(data.email)
        
        # Create user
        user = User(
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            display_name=data.display_name,
            language=data.language,
            email_verification_token=verification_token,
            email_verified=False,
        )
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email
            password: Plain text password
            
        Returns:
            User if credentials valid, None otherwise
        """
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await self.db.flush()
        
        return user
    
    async def verify_email(self, token: str) -> Optional[User]:
        """
        Verify user's email with token.
        
        Args:
            token: Verification token from email
            
        Returns:
            User if verified, None if invalid token
        """
        email = verify_verification_token(token)
        if not email:
            return None
        
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        user.email_verified = True
        user.email_verification_token = None
        await self.db.flush()
        
        return user
    
    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user's password.
        
        Args:
            user: User instance
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if successful, False if current password wrong
        """
        if not verify_password(current_password, user.password_hash):
            return False
        
        user.password_hash = hash_password(new_password)
        await self.db.flush()
        
        return True
    
    async def update_language(self, user: User, language: str) -> User:
        """
        Update user's preferred language.
        
        Args:
            user: User instance
            language: New language code
            
        Returns:
            Updated user
        """
        user.language = language
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
