"""
Khaznati DZ - Folder API Routes

Endpoints for folder management and navigation.
"""

from typing import List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user, verify_csrf
from app.models.user import User
from app.models.folder import Folder
from app.schemas.file import FilePublic
from app.schemas.common import PaginatedResponse, MessageResponse, PaginationMeta
from app.services.folder_service import FolderService


router = APIRouter(prefix="/folders", tags=["Folders"])


class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[UUID] = None


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None


class FolderPublic(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: Any
    
    class Config:
        from_attributes = True


class FolderContentResponse(BaseModel):
    folders: List[FolderPublic]
    files: List[FilePublic]
    breadcrumbs: List[dict]
    current_folder_id: Optional[UUID]


@router.get(
    "",
    response_model=PaginatedResponse[FolderPublic],
    summary="List folders"
)
async def list_folders(
    parent_id: Optional[UUID] = Query(None, description="Parent folder ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List folders within a parent folder."""
    folder_service = FolderService(db)
    
    folders, total = await folder_service.list_folders(
        user_id=current_user.id,
        parent_id=parent_id,
        page=page,
        limit=limit
    )
    
    return PaginatedResponse(
        data=folders,
        pagination=PaginationMeta.create(page, limit, total)
    )


@router.get(
    "/content",
    response_model=FolderContentResponse,
    summary="Get folder contents (browse)"
)
async def get_folder_content(
    folder_id: Optional[UUID] = Query(None, description="Folder ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get full contents of a folder (folders + files) and breadcrumbs.
    This is the main endpoint for the file explorer UI.
    """
    folder_service = FolderService(db)
    
    # Check folder existence if provided
    if folder_id:
        folder = await folder_service.get_folder_by_id(folder_id, current_user.id)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="المجلد غير موجود"
            )
            
    content = await folder_service.get_folder_contents(folder_id, current_user.id)
    
    # Convert files to schema
    files_public = [FilePublic.from_model(f) for f in content["files"]]
    
    return {
        "folders": content["folders"],
        "files": files_public,
        "breadcrumbs": content["breadcrumbs"],
        "current_folder_id": content["current_folder_id"]
    }


@router.post(
    "",
    response_model=FolderPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf)],
    summary="Create folder"
)
async def create_folder(
    data: FolderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new folder."""
    folder_service = FolderService(db)
    
    try:
        folder = await folder_service.create_folder(
            user_id=current_user.id,
            name=data.name,
            parent_id=data.parent_id
        )
        return folder
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{folder_id}",
    response_model=FolderPublic,
    summary="Get folder details"
)
async def get_folder(
    folder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get metadata for a single folder."""
    folder_service = FolderService(db)
    
    folder = await folder_service.get_folder_by_id(folder_id, current_user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المجلد غير موجود"
        )
    
    return folder


@router.patch(
    "/{folder_id}",
    response_model=FolderPublic,
    dependencies=[Depends(verify_csrf)],
    summary="Update folder"
)
async def update_folder(
    folder_id: UUID,
    data: FolderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update folder name or move it."""
    folder_service = FolderService(db)
    
    try:
        folder = None
        if data.name:
            folder = await folder_service.rename_folder(
                folder_id, current_user.id, data.name
            )
        
        if data.parent_id is not None:
             # Explicit parent_id (allow None for root)
             folder = await folder_service.move_folder(
                 folder_id, current_user.id, data.parent_id
             )
             
        if not folder:
             folder = await folder_service.get_folder_by_id(folder_id, current_user.id)
             
        return folder
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{folder_id}",
    response_model=MessageResponse,
    dependencies=[Depends(verify_csrf)],
    summary="Delete folder"
)
async def delete_folder(
    folder_id: UUID,
    recursive: bool = Query(False, description="Delete non-empty folder recursively"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a folder. Must be empty unless recursive=True."""
    folder_service = FolderService(db)
    
    try:
        await folder_service.delete_folder(folder_id, current_user.id, recursive)
        return MessageResponse(message="تم حذف المجلد بنجاح")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
