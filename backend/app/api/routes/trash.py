"""
Khaznati DZ - Trash API Routes

Endpoints for managing deleted files and folders.
"""

from fastapi import APIRouter, HTTPException, status, Request

from app.services.file_service import file_service
from app.api.routes.auth import get_current_user


router = APIRouter(prefix="/trash", tags=["Trash"])


@router.get(
    "",
    summary="List trash items"
)
async def list_trash(request: Request):
    """List files currently in trash."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    items = file_service.get_trash(user_id)
    
    return {
        "items": items,
        "count": len(items)
    }


@router.post(
    "/files/{file_id}/restore",
    summary="Restore file"
)
async def restore_file(file_id: str, request: Request):
    """Restore a file from trash to its original location."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    success = file_service.restore_file(file_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"  # File not found
        )
    
    return {"message": "تم استعادة الملف بنجاح", "success": True}


@router.delete(
    "/files/{file_id}",
    summary="Permanently delete file"
)
async def delete_permanently(file_id: str, request: Request):
    """Permanently delete a file. This action cannot be undone."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    success = file_service.delete_file(file_id, user_id, permanent=True)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"
        )
    
    return {"message": "تم حذف الملف نهائياً", "success": True}


@router.post(
    "/empty",
    summary="Empty trash"
)
async def empty_trash(request: Request):
    """Permanently delete all items in trash."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    count = file_service.empty_trash(user_id)
    
    return {
        "message": f"تم إفراغ سلة المحذوفات ({count} ملفات)",
        "count": count,
        "success": True
    }
