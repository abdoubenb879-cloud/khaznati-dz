"""
Khaznati DZ - Trash API Routes

Endpoints for managing deleted files and folders.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, verify_csrf
from app.models.user import User
from app.schemas.file import FilePublic
from app.schemas.common import PaginatedResponse, MessageResponse, PaginationMeta
from app.services.file_service import FileService


router = APIRouter(prefix="/trash", tags=["Trash"])


@router.get(
    "",
    response_model=PaginatedResponse[FilePublic],
    summary="List trash items"
)
async def list_trash(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List text files currently in trash."""
    file_service = FileService(db)
    
    files, total = await file_service.list_files(
        user_id=current_user.id,
        folder_id=None, # across all folders
        include_trashed=True,
        page=page,
        limit=limit
    )
    
    # Files service returns filtered list, so if include_trashed=True logic in service 
    # handles returning *only* trashed or *including* trashed.
    # Our service impl: if include_trashed=True -> returns ONLY trashed items.
    
    files_public = [FilePublic.from_model(f) for f in files]
    
    return PaginatedResponse(
        data=files_public,
        pagination=PaginationMeta.create(page, limit, total)
    )


@router.post(
    "/files/{file_id}/restore",
    response_model=FilePublic,
    dependencies=[Depends(verify_csrf)],
    summary="Restore file"
)
async def restore_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Restore a file from trash to its original location."""
    file_service = FileService(db)
    
    try:
        file = await file_service.restore_file(file_id, current_user.id)
        return FilePublic.from_model(file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/files/{file_id}",
    response_model=MessageResponse,
    dependencies=[Depends(verify_csrf)],
    summary="Permanently delete file"
)
async def delete_permanently(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Permanently delete a file. This action cannot be undone."""
    file_service = FileService(db)
    
    try:
        await file_service.delete_file_permanently(file_id, current_user.id)
        return MessageResponse(message="تم حذف الملف نهائياً")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/empty",
    response_model=MessageResponse,
    dependencies=[Depends(verify_csrf)],
    summary="Empty trash"
)
async def empty_trash(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Permanently delete all items in trash."""
    file_service = FileService(db)
    
    count = await file_service.empty_trash(current_user.id)
    
    return MessageResponse(
        message=f"تم إفراغ سلة المحذوفات ({count} ملفات)"
    )
