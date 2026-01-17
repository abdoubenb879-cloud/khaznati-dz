"""
Khaznati DZ - Share Link Schemas

Pydantic schemas for file sharing operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# =============================================================================
# Request Schemas
# =============================================================================

class ShareLinkCreate(BaseModel):
    """Schema for creating a share link."""
    
    file_id: UUID = Field(..., description="ID of file to share")
    password: Optional[str] = Field(
        None,
        min_length=4,
        max_length=32,
        description="Optional password protection"
    )
    expires_in_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Days until expiration (1-365)"
    )
    max_downloads: Optional[int] = Field(
        None,
        ge=1,
        le=10000,
        description="Maximum download count"
    )


class ShareLinkPasswordVerify(BaseModel):
    """Schema for verifying share link password."""
    
    password: str = Field(..., description="Share link password")


# =============================================================================
# Response Schemas
# =============================================================================

class ShareLinkResponse(BaseModel):
    """Schema for share link in API responses."""
    
    id: UUID
    token: str
    file_id: UUID
    file_name: str
    file_size: int
    file_size_display: str
    has_password: bool
    expires_at: Optional[datetime]
    is_expired: bool
    download_count: int
    max_downloads: Optional[int]
    is_active: bool
    created_at: datetime
    public_url: str
    
    class Config:
        from_attributes = True


class ShareLinkPublic(BaseModel):
    """Public share link info (for download page)."""
    
    token: str
    file_name: str
    file_size: int
    file_size_display: str
    mime_type: Optional[str]
    has_password: bool
    is_valid: bool
    
    class Config:
        from_attributes = True


class ShareLinksListResponse(BaseModel):
    """Schema for listing all share links."""
    
    share_links: list[ShareLinkResponse]
    total: int
