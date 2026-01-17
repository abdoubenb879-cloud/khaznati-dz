"""
Khaznati DZ - Session Model

Database model for user session management.
"""

from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Session(Base):
    """User session model for authentication."""
    
    __tablename__ = "sessions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # User reference
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Session token (stored as SHA-256 hash)
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Client information
    ip_address: Mapped[str] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True
    )
    user_agent: Mapped[str] = mapped_column(
        String(512),
        nullable=True
    )
    
    # Expiration
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", lazy="joined")
    
    def __repr__(self) -> str:
        return f"<Session {self.id}>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        from datetime import timezone
        return datetime.now(timezone.utc) > self.expires_at
