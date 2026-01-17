"""
Khaznati DZ - Folder Model

Database model for folder organization.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import uuid

from sqlalchemy import String, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.file import File


class Folder(Base):
    """Folder model for organizing files."""
    
    __tablename__ = "folders"
    
    # Ensure unique folder names within the same parent directory per user
    __table_args__ = (
        UniqueConstraint("user_id", "parent_id", "name", name="uq_folder_path"),
    )
    
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
    
    # Parent folder (null = root level)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Folder details
    name: Mapped[str] = mapped_column(
        String(255),
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
    
    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="folders"
    )
    parent: Mapped[Optional["Folder"]] = relationship(
        "Folder",
        remote_side=[id],
        back_populates="children"
    )
    children: Mapped[List["Folder"]] = relationship(
        "Folder",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="folder",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Folder {self.name}>"
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root-level folder."""
        return self.parent_id is None
    
    def get_path(self) -> str:
        """
        Get the full path of this folder.
        Note: This requires eager loading of parent relationships.
        """
        parts = [self.name]
        current = self.parent
        while current is not None:
            parts.insert(0, current.name)
            current = current.parent
        return "/" + "/".join(parts)
