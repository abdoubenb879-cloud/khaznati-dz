"""
Khaznati DZ - Share Link Model

Database model for file sharing functionality.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.file import File


class ShareLink(Base):
    """Share link model for public file access."""
    
    __tablename__ = "share_links"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Target file
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Unique share token (URL-safe)
    token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Optional password protection
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Expiration
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Usage tracking
    download_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    max_downloads: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True  # None = unlimited
    )
    
    # Active status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    file: Mapped["File"] = relationship(
        "File",
        back_populates="share_links"
    )
    
    def __repr__(self) -> str:
        return f"<ShareLink {self.token[:8]}...>"
    
    @property
    def is_expired(self) -> bool:
        """Check if link has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_download_limit_reached(self) -> bool:
        """Check if download limit has been reached."""
        if self.max_downloads is None:
            return False
        return self.download_count >= self.max_downloads
    
    @property
    def is_valid(self) -> bool:
        """Check if link is still valid (active, not expired, within limit)."""
        return (
            self.is_active
            and not self.is_expired
            and not self.is_download_limit_reached
        )
    
    @property
    def has_password(self) -> bool:
        """Check if link is password protected."""
        return self.password_hash is not None
    
    @property
    def public_url(self) -> str:
        """Generate the public share URL path."""
        return f"/s/{self.token}"
