"""
Khaznati DZ - Authentication Service

Business logic for user authentication using Supabase.
"""

from typing import Optional
from datetime import datetime
import hashlib
import secrets

from app.core.supabase_client import db
from app.core.config import settings
from app.core.security import hash_password, verify_password


def create_verification_token(email: str) -> str:
    """Create an email verification token."""
    return secrets.token_urlsafe(32)


class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Find a user by email address."""
        return self.db.get_user_by_email(email.lower())
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Find a user by ID."""
        return self.db.get_user_by_id(user_id)
    
    def create_user(self, email: str, password: str, display_name: str = None, language: str = "ar") -> Optional[dict]:
        """
        Create a new user account.
        
        Returns:
            User dict if created, None if email exists
        """
        # Check if email exists
        existing = self.get_user_by_email(email)
        if existing:
            return None
        
        # Create password hash
        password_hash = hash_password(password)
        
        # Create user
        name = display_name or email.split('@')[0]
        user_id = self.db.create_user(name, email.lower(), password_hash)
        
        if user_id:
            return self.get_user_by_id(user_id)
        return None
    
    def authenticate(self, email: str, password: str) -> Optional[dict]:
        """
        Authenticate a user with email and password.
        
        Returns:
            User dict if credentials valid, None otherwise
        """
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        stored_hash = user.get('password_hash', '')
        if not verify_password(password, stored_hash):
            return None
        
        return user
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change user's password.
        
        Returns:
            True if successful, False if current password wrong
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        if not verify_password(current_password, user.get('password_hash', '')):
            return False
        
        new_hash = hash_password(new_password)
        return self.db.update_password(user_id, new_hash)
    
    def request_password_reset(self, email: str) -> Optional[str]:
        """
        Request a password reset.
        
        Returns:
            Reset token if user exists, None otherwise
        """
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        token = secrets.token_urlsafe(32)
        user_id = user.get('telegram_id')
        self.db.set_reset_token(user_id, token)
        return token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using token.
        
        Returns:
            True if successful, False otherwise
        """
        user = self.db.get_user_by_reset_token(token)
        if not user:
            return False
        
        user_id = user.get('telegram_id')
        new_hash = hash_password(new_password)
        
        if self.db.update_password(user_id, new_hash):
            self.db.clear_reset_token(user_id)
            return True
        return False
    
    def update_profile(self, user_id: str, **kwargs) -> bool:
        """Update user profile fields."""
        return self.db.update_user(user_id, **kwargs)


# Convenience instance
auth_service = AuthService()
