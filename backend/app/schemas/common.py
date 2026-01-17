"""
Khaznati DZ - Common Schemas

Shared Pydantic models for pagination, errors, and common patterns.
"""

from datetime import datetime
from typing import Generic, TypeVar, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.limit


class PaginationMeta(BaseModel):
    """Pagination metadata for responses."""
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationMeta":
        """Create pagination meta from counts."""
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        return cls(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    data: List[T]
    pagination: PaginationMeta


class ErrorDetail(BaseModel):
    """Error detail following RFC 7807."""
    type: str = Field(description="Error type URI")
    title: str = Field(description="Short error title")
    status: int = Field(description="HTTP status code")
    detail: Optional[str] = Field(default=None, description="Human-readable explanation")
    instance: Optional[str] = Field(default=None, description="URI of the specific instance")


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
    success: bool = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str
    timestamp: datetime


class StorageStats(BaseModel):
    """Storage usage statistics."""
    used_bytes: int
    quota_bytes: int
    remaining_bytes: int
    percentage_used: float
    
    @classmethod
    def from_user(cls, used: int, quota: int) -> "StorageStats":
        """Create from user storage values."""
        remaining = max(0, quota - used) if quota >= 0 else -1
        percentage = (used / quota * 100) if quota > 0 else 0.0
        return cls(
            used_bytes=used,
            quota_bytes=quota,
            remaining_bytes=remaining,
            percentage_used=round(percentage, 2)
        )


class SortParams(BaseModel):
    """Sorting parameters."""
    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort direction")
