"""
Khaznati DZ - Pydantic Schemas

All API request/response schemas.
"""

from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserUpdate,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    UserResponse,
    UserPublic,
    AuthResponse,
    MessageResponse,
)
from app.schemas.file import (
    FolderCreate,
    FolderUpdate,
    FolderMove,
    FolderResponse,
    FolderTree,
    FileResponse,
    FileMove,
    FileRename,
    FileBulkAction,
    UploadInitResponse,
    ChunkUploadResponse,
    UploadCompleteResponse,
    BrowserResponse,
    TrashResponse,
    SearchResponse,
)
from app.schemas.share import (
    ShareLinkCreate,
    ShareLinkPasswordVerify,
    ShareLinkResponse,
    ShareLinkPublic,
    ShareLinksListResponse,
)

__all__ = [
    # User
    "UserRegister",
    "UserLogin",
    "UserUpdate",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetConfirm",
    "UserResponse",
    "UserPublic",
    "AuthResponse",
    "MessageResponse",
    # File & Folder
    "FolderCreate",
    "FolderUpdate",
    "FolderMove",
    "FolderResponse",
    "FolderTree",
    "FileResponse",
    "FileMove",
    "FileRename",
    "FileBulkAction",
    "UploadInitResponse",
    "ChunkUploadResponse",
    "UploadCompleteResponse",
    "BrowserResponse",
    "TrashResponse",
    "SearchResponse",
    # Share
    "ShareLinkCreate",
    "ShareLinkPasswordVerify",
    "ShareLinkResponse",
    "ShareLinkPublic",
    "ShareLinksListResponse",
]
