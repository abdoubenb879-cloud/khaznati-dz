"""
Khaznati DZ - Folder Service

Business logic for folder operations.
"""

from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.folder import Folder
from app.models.file import File


class FolderService:
    """Service class for folder operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_folder_by_id(
        self,
        folder_id: UUID,
        user_id: UUID
    ) -> Optional[Folder]:
        """Get a folder by ID for a specific user."""
        result = await self.db.execute(
            select(Folder).where(
                Folder.id == folder_id,
                Folder.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def list_folders(
        self,
        user_id: UUID,
        parent_id: Optional[UUID] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Folder], int]:
        """
        List folders for a user.
        
        Args:
            user_id: Owner UUID
            parent_id: Parent folder ID (None for root level)
            page: Page number
            limit: Items per page
            
        Returns:
            Tuple of (folders list, total count)
        """
        # Base query
        query = select(Folder).where(Folder.user_id == user_id)
        count_query = select(func.count(Folder.id)).where(Folder.user_id == user_id)
        
        # Parent filter
        if parent_id is None:
            query = query.where(Folder.parent_id.is_(None))
            count_query = count_query.where(Folder.parent_id.is_(None))
        else:
            query = query.where(Folder.parent_id == parent_id)
            count_query = count_query.where(Folder.parent_id == parent_id)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Sorting and pagination
        query = query.order_by(Folder.name.asc())
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        folders = list(result.scalars().all())
        
        return folders, total
    
    async def create_folder(
        self,
        user_id: UUID,
        name: str,
        parent_id: Optional[UUID] = None
    ) -> Folder:
        """
        Create a new folder.
        
        Args:
            user_id: Owner UUID
            name: Folder name
            parent_id: Parent folder ID
            
        Returns:
            Created folder
        """
        # Validate parent if provided
        if parent_id:
            parent = await self.get_folder_by_id(parent_id, user_id)
            if not parent:
                raise ValueError("المجلد الأصل غير موجود")  # Parent folder not found
        
        # Check for duplicate name in same location
        existing = await self.db.execute(
            select(Folder).where(
                Folder.user_id == user_id,
                Folder.parent_id == parent_id,
                Folder.name == name
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("يوجد مجلد بهذا الاسم بالفعل")  # Folder with this name exists
        
        folder = Folder(
            user_id=user_id,
            parent_id=parent_id,
            name=name
        )
        
        self.db.add(folder)
        await self.db.flush()
        await self.db.refresh(folder)
        
        return folder
    
    async def rename_folder(
        self,
        folder_id: UUID,
        user_id: UUID,
        new_name: str
    ) -> Folder:
        """Rename a folder."""
        folder = await self.get_folder_by_id(folder_id, user_id)
        if not folder:
            raise ValueError("المجلد غير موجود")  # Folder not found
        
        # Check for duplicate name
        existing = await self.db.execute(
            select(Folder).where(
                Folder.user_id == user_id,
                Folder.parent_id == folder.parent_id,
                Folder.name == new_name,
                Folder.id != folder_id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("يوجد مجلد بهذا الاسم بالفعل")
        
        folder.name = new_name
        await self.db.flush()
        await self.db.refresh(folder)
        
        return folder
    
    async def move_folder(
        self,
        folder_id: UUID,
        user_id: UUID,
        target_parent_id: Optional[UUID]
    ) -> Folder:
        """Move a folder to a different parent."""
        folder = await self.get_folder_by_id(folder_id, user_id)
        if not folder:
            raise ValueError("المجلد غير موجود")
        
        # Can't move to itself
        if target_parent_id == folder_id:
            raise ValueError("لا يمكن نقل المجلد إلى نفسه")
        
        # Validate target parent
        if target_parent_id:
            target = await self.get_folder_by_id(target_parent_id, user_id)
            if not target:
                raise ValueError("المجلد الهدف غير موجود")
            
            # Check for circular reference
            if await self._is_descendant(folder_id, target_parent_id, user_id):
                raise ValueError("لا يمكن نقل المجلد إلى مجلد فرعي منه")
        
        # Check for duplicate name in target
        existing = await self.db.execute(
            select(Folder).where(
                Folder.user_id == user_id,
                Folder.parent_id == target_parent_id,
                Folder.name == folder.name,
                Folder.id != folder_id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("يوجد مجلد بهذا الاسم في الوجهة")
        
        folder.parent_id = target_parent_id
        await self.db.flush()
        await self.db.refresh(folder)
        
        return folder
    
    async def _is_descendant(
        self,
        ancestor_id: UUID,
        folder_id: UUID,
        user_id: UUID
    ) -> bool:
        """Check if folder_id is a descendant of ancestor_id."""
        current_id = folder_id
        visited = set()
        
        while current_id and current_id not in visited:
            if current_id == ancestor_id:
                return True
            
            visited.add(current_id)
            folder = await self.get_folder_by_id(current_id, user_id)
            current_id = folder.parent_id if folder else None
        
        return False
    
    async def delete_folder(
        self,
        folder_id: UUID,
        user_id: UUID,
        recursive: bool = False
    ) -> None:
        """
        Delete a folder.
        
        Args:
            folder_id: Folder UUID
            user_id: Owner UUID
            recursive: If True, delete children. If False, fail if not empty.
        """
        folder = await self.get_folder_by_id(folder_id, user_id)
        if not folder:
            raise ValueError("المجلد غير موجود")
        
        # Check if folder has contents
        has_children = await self.db.execute(
            select(func.count()).select_from(Folder).where(
                Folder.parent_id == folder_id
            )
        )
        has_files = await self.db.execute(
            select(func.count()).select_from(File).where(
                File.folder_id == folder_id,
                File.is_trashed == False
            )
        )
        
        children_count = has_children.scalar() or 0
        files_count = has_files.scalar() or 0
        
        if (children_count > 0 or files_count > 0) and not recursive:
            raise ValueError("المجلد ليس فارغاً")  # Folder is not empty
        
        # Delete folder (cascade will handle children if recursive)
        await self.db.delete(folder)
        await self.db.flush()
    
    async def get_breadcrumbs(
        self,
        folder_id: UUID,
        user_id: UUID
    ) -> List[dict]:
        """
        Get breadcrumb path to a folder.
        
        Returns:
            List of {id, name} from root to folder
        """
        breadcrumbs = []
        current_id = folder_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            folder = await self.get_folder_by_id(current_id, user_id)
            if folder:
                breadcrumbs.insert(0, {
                    "id": folder.id,
                    "name": folder.name
                })
                current_id = folder.parent_id
            else:
                break
        
        return breadcrumbs
    
    async def get_folder_contents(
        self,
        folder_id: Optional[UUID],
        user_id: UUID
    ) -> dict:
        """
        Get full contents of a folder including files and subfolders.
        
        Returns:
            Dict with folders, files, and breadcrumbs
        """
        # Get folders
        folders, _ = await self.list_folders(user_id, folder_id, page=1, limit=1000)
        
        # Get files
        from app.services.file_service import FileService
        file_service = FileService(self.db)
        files, _ = await file_service.list_files(
            user_id,
            folder_id=folder_id,
            page=1,
            limit=1000
        )
        
        # Get breadcrumbs
        breadcrumbs = []
        if folder_id:
            breadcrumbs = await self.get_breadcrumbs(folder_id, user_id)
        
        return {
            "folders": folders,
            "files": files,
            "breadcrumbs": breadcrumbs,
            "current_folder_id": folder_id
        }
