"""
Khaznati DZ - Folder API Routes

Endpoints for folder management and navigation.
Uses Supabase for metadata storage.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status, Request

from app.services.folder_service import folder_service
from app.services.file_service import file_service
from app.api.routes.auth import get_current_user


router = APIRouter(prefix="/folders", tags=["Folders"])


@router.get(
    "",
    summary="List folders"
)
async def list_folders(
    request: Request,
    parent_id: Optional[str] = None
):
    """List folders within a parent folder."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    folders = folder_service.list_folders(user_id, parent_id)
    
    return {
        "folders": folders,
        "parent_id": parent_id
    }


@router.get(
    "/content",
    summary="Get folder contents (browse)"
)
async def get_folder_content(
    request: Request,
    folder_id: Optional[str] = None
):
    """
    Get full contents of a folder (folders + files) and breadcrumbs.
    This is the main endpoint for the file explorer UI.
    """
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    # Get files and folders
    files = file_service.list_files(user_id, folder_id)
    folders = [f for f in files if f.get("is_folder")]
    regular_files = [f for f in files if not f.get("is_folder")]
    
    # Get breadcrumbs
    breadcrumbs = []
    if folder_id:
        breadcrumbs = folder_service.get_breadcrumbs(folder_id)
    
    return {
        "folders": folders,
        "files": regular_files,
        "breadcrumbs": breadcrumbs,
        "current_folder_id": folder_id
    }


@router.get(
    "/all",
    summary="Get all folders (for move dialog)"
)
async def get_all_folders(request: Request):
    """Get all folders for the user (used in move file dialog)."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    folders = folder_service.get_all_folders(user_id)
    
    return {"folders": folders}


@router.post(
    "",
    summary="Create folder"
)
async def create_folder(request: Request):
    """Create a new folder."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    body = await request.json()
    
    name = body.get("name", "").strip()
    parent_id = body.get("parent_id")
    
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="اسم المجلد مطلوب"  # Folder name required
        )
    
    folder = folder_service.create_folder(user_id, name, parent_id)
    
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل إنشاء المجلد"  # Failed to create folder
        )
    
    return {
        "message": "تم إنشاء المجلد بنجاح",
        "folder": folder
    }


@router.get(
    "/{folder_id}",
    summary="Get folder details"
)
async def get_folder(folder_id: str, request: Request):
    """Get metadata for a single folder."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    folder = folder_service.get_folder(folder_id)
    
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المجلد غير موجود"  # Folder not found
        )
    
    return folder


@router.patch(
    "/{folder_id}",
    summary="Rename folder"
)
async def rename_folder(folder_id: str, request: Request):
    """Rename a folder."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    body = await request.json()
    
    new_name = body.get("name", "").strip()
    
    if not new_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الاسم مطلوب"
        )
    
    success = folder_service.rename_folder(folder_id, user_id, new_name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المجلد غير موجود"
        )
    
    return {"message": "تم تغيير الاسم بنجاح", "success": True}


@router.post(
    "/{folder_id}/move",
    summary="Move folder"
)
async def move_folder(folder_id: str, request: Request):
    """Move a folder to a different parent."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    body = await request.json()
    
    new_parent_id = body.get("parent_id")  # None for root
    
    success = folder_service.move_folder(folder_id, user_id, new_parent_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكن نقل المجلد"  # Cannot move folder
        )
    
    return {"message": "تم نقل المجلد بنجاح", "success": True}


@router.delete(
    "/{folder_id}",
    summary="Delete folder"
)
async def delete_folder(
    folder_id: str, 
    request: Request,
    permanent: bool = False
):
    """Delete a folder."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    success = folder_service.delete_folder(folder_id, user_id, permanent=permanent)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المجلد غير موجود"
        )
    
    return {"message": "تم حذف المجلد بنجاح", "success": True}
