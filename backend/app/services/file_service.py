"""
Khaznati DZ - File Service

Business logic for file operations.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, func, or_, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.services.storage_service import storage_service
from app.core.config import settings


class FileService:
    """Service class for file operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = storage_service
    
    async def get_file_by_id(
        self,
        file_id: UUID,
        user_id: UUID,
        include_trashed: bool = False
    ) -> Optional[File]:
        """
        Get a file by ID for a specific user.
        
        Args:
            file_id: File UUID
            user_id: Owner's UUID
            include_trashed: Include files in trash
            
        Returns:
            File if found and owned by user, None otherwise
        """
        query = select(File).where(
            File.id == file_id,
            File.user_id == user_id
        )
        
        if not include_trashed:
            query = query.where(File.is_trashed == False)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_files(
        self,
        user_id: UUID,
        folder_id: Optional[UUID] = None,
        search: Optional[str] = None,
        mime_type: Optional[str] = None,
        include_trashed: bool = False,
        page: int = 1,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[File], int]:
        """
        List files for a user with filtering and pagination.
        
        Returns:
            Tuple of (files list, total count)
        """
        # Base query
        query = select(File).where(File.user_id == user_id)
        count_query = select(func.count(File.id)).where(File.user_id == user_id)
        
        # Folder filter
        if folder_id is not None:
            query = query.where(File.folder_id == folder_id)
            count_query = count_query.where(File.folder_id == folder_id)
        else:
            # Root level files (no folder)
            query = query.where(File.folder_id.is_(None))
            count_query = count_query.where(File.folder_id.is_(None))
        
        # Trash filter
        if not include_trashed:
            query = query.where(File.is_trashed == False)
            count_query = count_query.where(File.is_trashed == False)
        else:
            # Only trashed files
            query = query.where(File.is_trashed == True)
            count_query = count_query.where(File.is_trashed == True)
        
        # Search filter
        if search:
            search_filter = File.name.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # MIME type filter
        if mime_type:
            mime_filter = File.mime_type.startswith(mime_type)
            query = query.where(mime_filter)
            count_query = count_query.where(mime_filter)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Sorting
        sort_column = getattr(File, sort_by, File.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        files = list(result.scalars().all())
        
        return files, total
    
    async def init_upload(
        self,
        user: User,
        name: str,
        size_bytes: int,
        folder_id: Optional[UUID] = None,
        mime_type: Optional[str] = None,
        checksum: Optional[str] = None
    ) -> dict:
        """
        Initialize a file upload.
        
        Args:
            user: Owner user
            name: File name
            size_bytes: File size
            folder_id: Target folder
            mime_type: MIME type
            checksum: SHA-256 checksum
            
        Returns:
            Upload initialization data with presigned URL(s)
        """
        # Check quota
        if user.storage_quota >= 0:
            if user.storage_used + size_bytes > user.storage_quota:
                raise ValueError("تجاوزت سعة التخزين المتاحة")  # Storage quota exceeded
        
        # Validate folder if provided
        if folder_id:
            folder = await self.db.execute(
                select(Folder).where(
                    Folder.id == folder_id,
                    Folder.user_id == user.id
                )
            )
            if not folder.scalar_one_or_none():
                raise ValueError("المجلد غير موجود")  # Folder not found
        
        # Create file record
        file_id = uuid4()
        storage_key = self.storage.generate_storage_key(user.id, file_id, name)
        
        file = File(
            id=file_id,
            user_id=user.id,
            folder_id=folder_id,
            name=name,
            size_bytes=size_bytes,
            mime_type=mime_type or "application/octet-stream",
            storage_key=storage_key,
            checksum=checksum,
            is_trashed=False,
        )
        
        self.db.add(file)
        await self.db.flush()
        
        # Determine upload strategy based on size
        chunk_size = settings.chunk_size_bytes
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        if size_bytes <= chunk_size:
            # Simple upload for small files
            presigned_url = await self.storage.generate_upload_url(
                storage_key,
                content_type=mime_type or "application/octet-stream",
                expires_in=3600
            )
            
            return {
                "file_id": file_id,
                "upload_id": None,
                "presigned_url": presigned_url,
                "parts": None,
                "expires_at": expires_at
            }
        else:
            # Multipart upload for large files
            upload_id = await self.storage.initiate_multipart_upload(
                storage_key,
                content_type=mime_type or "application/octet-stream"
            )
            
            parts = await self.storage.generate_part_upload_urls(
                storage_key,
                upload_id,
                size_bytes,
                part_size=chunk_size,
                expires_in=3600
            )
            
            return {
                "file_id": file_id,
                "upload_id": upload_id,
                "presigned_url": None,
                "parts": parts,
                "expires_at": expires_at
            }
    
    async def complete_upload(
        self,
        file_id: UUID,
        user_id: UUID,
        upload_id: Optional[str] = None,
        parts: Optional[List[dict]] = None
    ) -> File:
        """
        Mark an upload as complete.
        
        Args:
            file_id: File UUID
            user_id: Owner UUID
            upload_id: Multipart upload ID (if applicable)
            parts: Completed parts with ETags (if multipart)
            
        Returns:
            Updated File
        """
        file = await self.get_file_by_id(file_id, user_id)
        if not file:
            raise ValueError("الملف غير موجود")  # File not found
        
        # Complete multipart upload if applicable
        if upload_id and parts:
            await self.storage.complete_multipart_upload(
                file.storage_key,
                upload_id,
                parts
            )
        
        # Update user storage
        user = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user.scalar_one()
        user.storage_used += file.size_bytes
        
        await self.db.flush()
        await self.db.refresh(file)
        
        return file
    
    async def get_download_url(
        self,
        file_id: UUID,
        user_id: UUID
    ) -> dict:
        """
        Generate a download URL for a file.
        
        Returns:
            Dict with download_url, expires_at, filename
        """
        file = await self.get_file_by_id(file_id, user_id)
        if not file:
            raise ValueError("الملف غير موجود")  # File not found
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        download_url = await self.storage.generate_download_url(
            file.storage_key,
            file.name,
            expires_in=3600
        )
        
        return {
            "download_url": download_url,
            "expires_at": expires_at,
            "filename": file.name
        }
    
    async def rename_file(
        self,
        file_id: UUID,
        user_id: UUID,
        new_name: str
    ) -> File:
        """Rename a file."""
        file = await self.get_file_by_id(file_id, user_id)
        if not file:
            raise ValueError("الملف غير موجود")
        
        file.name = new_name
        await self.db.flush()
        await self.db.refresh(file)
        
        return file
    
    async def move_file(
        self,
        file_id: UUID,
        user_id: UUID,
        target_folder_id: Optional[UUID]
    ) -> File:
        """Move a file to a different folder."""
        file = await self.get_file_by_id(file_id, user_id)
        if not file:
            raise ValueError("الملف غير موجود")
        
        # Validate target folder
        if target_folder_id:
            folder = await self.db.execute(
                select(Folder).where(
                    Folder.id == target_folder_id,
                    Folder.user_id == user_id
                )
            )
            if not folder.scalar_one_or_none():
                raise ValueError("المجلد الهدف غير موجود")
        
        file.folder_id = target_folder_id
        await self.db.flush()
        await self.db.refresh(file)
        
        return file
    
    async def trash_file(self, file_id: UUID, user_id: UUID) -> File:
        """Move a file to trash (soft delete)."""
        file = await self.get_file_by_id(file_id, user_id)
        if not file:
            raise ValueError("الملف غير موجود")
        
        file.is_trashed = True
        file.trashed_at = datetime.now(timezone.utc)
        file.original_folder_id = file.folder_id
        file.folder_id = None
        
        await self.db.flush()
        await self.db.refresh(file)
        
        return file
    
    async def restore_file(self, file_id: UUID, user_id: UUID) -> File:
        """Restore a file from trash."""
        file = await self.get_file_by_id(file_id, user_id, include_trashed=True)
        if not file or not file.is_trashed:
            raise ValueError("الملف غير موجود في سلة المحذوفات")
        
        file.is_trashed = False
        file.trashed_at = None
        file.folder_id = file.original_folder_id
        file.original_folder_id = None
        
        await self.db.flush()
        await self.db.refresh(file)
        
        return file
    
    async def delete_file_permanently(
        self,
        file_id: UUID,
        user_id: UUID
    ) -> None:
        """Permanently delete a file from storage and database."""
        file = await self.get_file_by_id(file_id, user_id, include_trashed=True)
        if not file:
            raise ValueError("الملف غير موجود")
        
        # Delete from storage
        await self.storage.delete_object(file.storage_key)
        
        # Update user storage
        user = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user.scalar_one()
        user.storage_used = max(0, user.storage_used - file.size_bytes)
        
        # Delete from database
        await self.db.delete(file)
        await self.db.flush()
    
    async def empty_trash(self, user_id: UUID) -> int:
        """
        Permanently delete all files in trash.
        
        Returns:
            Number of files deleted
        """
        # Get all trashed files
        result = await self.db.execute(
            select(File).where(
                File.user_id == user_id,
                File.is_trashed == True
            )
        )
        files = list(result.scalars().all())
        
        if not files:
            return 0
        
        # Delete from storage
        storage_keys = [f.storage_key for f in files]
        await self.storage.delete_objects(storage_keys)
        
        # Calculate total size
        total_size = sum(f.size_bytes for f in files)
        
        # Update user storage
        user = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user.scalar_one()
        user.storage_used = max(0, user.storage_used - total_size)
        
        # Delete from database
        await self.db.execute(
            delete(File).where(
                File.user_id == user_id,
                File.is_trashed == True
            )
        )
        await self.db.flush()
        
        return len(files)
