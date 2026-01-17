"""
Khaznati DZ - File Model

Database model for file metadata storage.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import uuid

from sqlalchemy import String, BigInteger, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.folder import Folder
    from app.models.share_link import ShareLink


class File(Base):
    """File metadata model."""
    
    __tablename__ = "files"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Owner
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Location (null folder_id = root level)
    folder_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # File details
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Storage reference (S3 key / path)
    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True
    )
    
    # Checksum for integrity verification
    checksum: Mapped[Optional[str]] = mapped_column(
        String(64),  # SHA-256 hex
        nullable=True
    )
    
    # Trash functionality
    is_trashed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    trashed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Original location before trash (for restore)
    original_folder_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
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
    
    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="files"
    )
    folder: Mapped[Optional["Folder"]] = relationship(
        "Folder",
        back_populates="files"
    )
    share_links: Mapped[List["ShareLink"]] = relationship(
        "ShareLink",
        back_populates="file",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<File {self.name}>"
    
    @property
    def extension(self) -> Optional[str]:
        """Get file extension."""
        if "." in self.name:
            return self.name.rsplit(".", 1)[1].lower()
        return None
    
    @property
    def size_display(self) -> str:
        """Human-readable file size."""
        size = self.size_bytes
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    @property
    def is_image(self) -> bool:
        """Check if file is an image."""
        return self.mime_type is not None and self.mime_type.startswith("image/")
    
    @property
    def is_video(self) -> bool:
        """Check if file is a video."""
        return self.mime_type is not None and self.mime_type.startswith("video/")
    
    @property
    def is_audio(self) -> bool:
        """Check if file is an audio file."""
        return self.mime_type is not None and self.mime_type.startswith("audio/")
    
    @property
    def is_document(self) -> bool:
        """Check if file is a document (PDF, Word, etc.)."""
        doc_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument",
            "text/plain",
        ]
        return self.mime_type is not None and any(
            self.mime_type.startswith(t) for t in doc_types
        )
