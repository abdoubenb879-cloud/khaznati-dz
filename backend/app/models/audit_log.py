"""
Khaznati DZ - Audit Log Model

Database model for tracking user activities.
"""

from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
import uuid

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base):
    """Audit log model for tracking user actions."""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # User who performed the action (nullable for system actions)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Action details
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    resource_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    # Additional context
    metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    
    # Client information
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", lazy="joined")
    
    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by {self.user_id}>"


# Action constants
class AuditAction:
    """Audit action type constants."""
    
    # Auth
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    
    # Files
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_DELETE = "file_delete"
    FILE_RESTORE = "file_restore"
    FILE_PERMANENT_DELETE = "file_permanent_delete"
    FILE_RENAME = "file_rename"
    FILE_MOVE = "file_move"
    
    # Folders
    FOLDER_CREATE = "folder_create"
    FOLDER_DELETE = "folder_delete"
    FOLDER_RENAME = "folder_rename"
    FOLDER_MOVE = "folder_move"
    
    # Sharing
    SHARE_CREATE = "share_create"
    SHARE_DELETE = "share_delete"
    SHARE_ACCESS = "share_access"
    SHARE_DOWNLOAD = "share_download"
    
    # Trash
    TRASH_EMPTY = "trash_empty"
    TRASH_RESTORE_ALL = "trash_restore_all"
