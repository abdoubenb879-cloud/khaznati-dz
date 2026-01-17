"""
Khaznati DZ - User Model

Database model for user accounts.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import uuid

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.file import File
    from app.models.folder import Folder


class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Email verification
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    email_verification_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Profile
    display_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Preferences
    language: Mapped[str] = mapped_column(
        String(5),
        default="ar",
        nullable=False
    )
    
    # Storage quota (in bytes, -1 = unlimited)
    storage_quota: Mapped[int] = mapped_column(
        default=5 * 1024 * 1024 * 1024,  # 5 GB default
        nullable=False
    )
    storage_used: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    folders: Mapped[List["Folder"]] = relationship(
        "Folder",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
    
    @property
    def storage_remaining(self) -> int:
        """Calculate remaining storage in bytes."""
        if self.storage_quota == -1:
            return -1  # Unlimited
        return max(0, self.storage_quota - self.storage_used)
    
    @property
    def storage_percentage(self) -> float:
        """Calculate storage usage percentage."""
        if self.storage_quota == -1:
            return 0.0
        if self.storage_quota == 0:
            return 100.0
        return (self.storage_used / self.storage_quota) * 100
