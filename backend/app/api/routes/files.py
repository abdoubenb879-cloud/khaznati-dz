"""
Khaznati DZ - File API Routes

Endpoints for file management, uploading, downloading, and sharing.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_verified_user, verify_csrf
from app.models.user import User
from app.schemas.file import (
    FilePublic,
    UploadInitRequest,
    UploadInitResponse,
    UploadCompleteRequest,
    DownloadResponse,
    FileListParams,
    FileUpdate
)
from app.schemas.common import PaginatedResponse, MessageResponse, PaginationMeta
from app.services.file_service import FileService


router = APIRouter(prefix="/files", tags=["Files"])


@router.get(
    "",
    response_model=PaginatedResponse[FilePublic],
    summary="List files"
)
async def list_files(
    folder_id: Optional[UUID] = Query(None, description="Filter by folder"),
    search: Optional[str] = Query(None, description="Search by name"),
    mime_type: Optional[str] = Query(None, description="Filter by MIME type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's files with filtering and pagination.
    """
    file_service = FileService(db)
    
    files, total = await file_service.list_files(
        user_id=current_user.id,
        folder_id=folder_id,
        search=search,
        mime_type=mime_type,
        include_trashed=False,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Convert to schema
    files_public = [FilePublic.from_model(f) for f in files]
    
    return PaginatedResponse(
        data=files_public,
        pagination=PaginationMeta.create(page, limit, total)
    )


@router.post(
    "/upload/init",
    response_model=UploadInitResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf)],
    summary="Initialize file upload"
)
async def init_upload(
    data: UploadInitRequest,
    current_user: User = Depends(get_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize a file upload.
    Returns presigned URL(s) for uploading directly to storage.
    Handles both simple and multipart (chunked) uploads.
    """
    file_service = FileService(db)
    
    try:
        result = await file_service.init_upload(
            user=current_user,
            name=data.name,
            size_bytes=data.size_bytes,
            folder_id=data.folder_id,
            mime_type=data.mime_type,
            checksum=data.checksum
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/upload/complete",
    response_model=FilePublic,
    dependencies=[Depends(verify_csrf)],
    summary="Complete file upload"
)
async def complete_upload(
    data: UploadCompleteRequest,
    current_user: User = Depends(get_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm that file upload is complete.
    For multipart uploads, assembles the chunks.
    """
    file_service = FileService(db)
    
    try:
        # Convert Pydantic models to dictionaries for the service
        parts_dicts = [p.model_dump() for p in data.parts] if data.parts else None
        
        file = await file_service.complete_upload(
            file_id=data.file_id,
            user_id=current_user.id,
            upload_id=data.upload_id,
            parts=parts_dicts
        )
        return FilePublic.from_model(file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{file_id}/download",
    response_model=DownloadResponse,
    summary="Get download URL"
)
async def get_download_url(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a temporary presigned URL to download a file.
    """
    file_service = FileService(db)
    
    try:
        result = await file_service.get_download_url(file_id, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/{file_id}",
    response_model=FilePublic,
    summary="Get file details"
)
async def get_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get metadata for a single file."""
    file_service = FileService(db)
    
    file = await file_service.get_file_by_id(file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"  # File not found
        )
    
    return FilePublic.from_model(file)


@router.patch(
    "/{file_id}",
    response_model=FilePublic,
    dependencies=[Depends(verify_csrf)],
    summary="Update file"
)
async def update_file(
    file_id: UUID,
    data: FileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update file name or location (move)."""
    file_service = FileService(db)
    
    try:
        file = None
        if data.name:
            file = await file_service.rename_file(file_id, current_user.id, data.name)
        
        if data.folder_id is not None:  # explicit move, allow None for root
            # If we already updated name, use the returned file's ID (though it's the same)
            file = await file_service.move_file(file_id, current_user.id, data.folder_id)
        
        # If nothing updated but file exists
        if not file:
             file = await file_service.get_file_by_id(file_id, current_user.id)
             
        return FilePublic.from_model(file)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "غير موجود" in str(e) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@router.delete(
    "/{file_id}",
    response_model=MessageResponse,
    dependencies=[Depends(verify_csrf)],
    summary="Move file to trash"
)
async def delete_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a file (move to trash)."""
    file_service = FileService(db)
    
    try:
        await file_service.trash_file(file_id, current_user.id)
        return MessageResponse(message="تم نقل الملف إلى سلة المحذوفات")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
