"""
Khaznati DZ - File & Folder Schemas

Pydantic schemas for file and folder operations.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


# =============================================================================
# Folder Schemas
# =============================================================================

class FolderCreate(BaseModel):
    """Schema for creating a folder."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Folder name"
    )
    parent_id: Optional[UUID] = Field(
        None,
        description="Parent folder ID (null for root level)"
    )


class FolderUpdate(BaseModel):
    """Schema for updating a folder."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New folder name"
    )


class FolderMove(BaseModel):
    """Schema for moving a folder."""
    
    parent_id: Optional[UUID] = Field(
        None,
        description="New parent folder ID (null for root)"
    )


class FolderResponse(BaseModel):
    """Schema for folder in API responses."""
    
    id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    item_count: int = 0
    
    class Config:
        from_attributes = True


class FolderTree(BaseModel):
    """Schema for folder with nested children."""
    
    id: UUID
    name: str
    parent_id: Optional[UUID]
    children: List["FolderTree"] = []
    
    class Config:
        from_attributes = True


# =============================================================================
# File Schemas
# =============================================================================

class FileResponse(BaseModel):
    """Schema for file in API responses."""
    
    id: UUID
    name: str
    size_bytes: int
    size_display: str
    mime_type: Optional[str]
    folder_id: Optional[UUID]
    is_trashed: bool
    created_at: datetime
    updated_at: datetime
    
    # Type indicators
    is_image: bool = False
    is_video: bool = False
    is_audio: bool = False
    is_document: bool = False
    extension: Optional[str] = None
    
    class Config:
        from_attributes = True


class FileMove(BaseModel):
    """Schema for moving a file."""
    
    folder_id: Optional[UUID] = Field(
        None,
        description="Target folder ID (null for root)"
    )


class FileRename(BaseModel):
    """Schema for renaming a file."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="New file name"
    )


class FileBulkAction(BaseModel):
    """Schema for bulk file operations."""
    
    file_ids: List[UUID] = Field(
        ...,
        min_length=1,
        description="List of file IDs"
    )
    action: str = Field(
        ...,
        pattern="^(delete|restore|move)$",
        description="Action to perform"
    )
    folder_id: Optional[UUID] = Field(
        None,
        description="Target folder for move action"
    )


# =============================================================================
# Upload Schemas
# =============================================================================

class UploadInitResponse(BaseModel):
    """Response for upload initialization."""
    
    upload_id: str
    chunk_size: int
    total_chunks: int


class ChunkUploadResponse(BaseModel):
    """Response for chunk upload."""
    
    chunk_index: int
    received: bool
    remaining_chunks: int


class UploadCompleteResponse(BaseModel):
    """Response for upload completion."""
    
    file: FileResponse
    message: str


# =============================================================================
# Browser Schemas
# =============================================================================

class BrowserResponse(BaseModel):
    """Schema for file browser listing."""
    
    current_folder: Optional[FolderResponse]
    breadcrumbs: List[FolderResponse]
    folders: List[FolderResponse]
    files: List[FileResponse]
    total_items: int
    
    class Config:
        from_attributes = True


class TrashResponse(BaseModel):
    """Schema for trash listing."""
    
    files: List[FileResponse]
    total_items: int
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Schema for search results."""
    
    query: str
    files: List[FileResponse]
    folders: List[FolderResponse]
    total_results: int
