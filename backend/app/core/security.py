"""
Khaznati DZ - Security Module

Password hashing, token generation, and security utilities.
Uses Argon2 for password hashing (recommended by OWASP).
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import secrets
import hashlib

from passlib.context import CryptContext
from jose import jwt, JWTError
from itsdangerous import URLSafeTimedSerializer

from app.core.config import settings


# Password hashing context using Argon2
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64MB
    argon2__time_cost=3,
    argon2__parallelism=4
)

# Token serializer for email verification, password reset, etc.
token_serializer = URLSafeTimedSerializer(settings.secret_key)


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to check
        hashed_password: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: Number of bytes (hex string will be 2x this length)
        
    Returns:
        Secure random hex string
    """
    return secrets.token_hex(length)


def generate_share_token() -> str:
    """
    Generate a URL-safe token for share links.
    
    Returns:
        URL-safe base64 token (22 characters)
    """
    return secrets.token_urlsafe(16)


def create_verification_token(email: str) -> str:
    """
    Create a signed token for email verification.
    
    Args:
        email: User's email address
        
    Returns:
        Signed token that expires in 24 hours
    """
    return token_serializer.dumps(email, salt="email-verification")


def verify_verification_token(token: str, max_age: int = 86400) -> Optional[str]:
    """
    Verify an email verification token.
    
    Args:
        token: The token to verify
        max_age: Maximum age in seconds (default 24 hours)
        
    Returns:
        Email address if valid, None otherwise
    """
    try:
        email = token_serializer.loads(token, salt="email-verification", max_age=max_age)
        return email
    except Exception:
        return None


def create_password_reset_token(user_id: str) -> str:
    """
    Create a signed token for password reset.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        Signed token that expires in 1 hour
    """
    return token_serializer.dumps(user_id, salt="password-reset")


def verify_password_reset_token(token: str, max_age: int = 3600) -> Optional[str]:
    """
    Verify a password reset token.
    
    Args:
        token: The token to verify
        max_age: Maximum age in seconds (default 1 hour)
        
    Returns:
        User ID if valid, None otherwise
    """
    try:
        user_id = token_serializer.loads(token, salt="password-reset", max_age=max_age)
        return user_id
    except Exception:
        return None


def create_csrf_token() -> str:
    """
    Generate a CSRF token.
    
    Returns:
        CSRF token string
    """
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, stored_token: str) -> bool:
    """
    Verify CSRF token using constant-time comparison.
    
    Args:
        token: Token from request
        stored_token: Token from session
        
    Returns:
        True if tokens match
    """
    return secrets.compare_digest(token, stored_token)


def hash_share_password(password: str) -> str:
    """
    Hash a share link password.
    Uses SHA-256 for lighter weight than Argon2 (share passwords are optional).
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_share_password(password: str, hashed: str) -> bool:
    """
    Verify a share link password.
    
    Args:
        password: Plain text password
        hashed: Stored hash
        
    Returns:
        True if password matches
    """
    return secrets.compare_digest(
        hashlib.sha256(password.encode()).hexdigest(),
        hashed
    )
