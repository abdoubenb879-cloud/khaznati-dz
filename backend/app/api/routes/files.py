"""
Khaznati DZ - File API Routes

Endpoints for file management, uploading, downloading, and sharing.
Uses Telegram for storage and Supabase for metadata.
"""

import os
import tempfile
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import FileResponse

from app.services.file_service import file_service
from app.api.routes.auth import get_current_user, get_current_user_id


router = APIRouter(prefix="/files", tags=["Files"])


@router.get(
    "",
    summary="List files"
)
async def list_files(
    request: Request,
    folder_id: Optional[str] = None
):
    """List user's files in a folder (or root)."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    files = file_service.list_files(user_id, folder_id)
    
    return {
        "files": files,
        "folder_id": folder_id
    }


@router.post(
    "/upload",
    summary="Upload a file"
)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(None)
):
    """
    Upload a file to storage.
    
    - **file**: The file to upload
    - **folder_id**: Optional folder to upload to (root if not specified)
    """
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        result = file_service.upload_file(
            user_id=user_id,
            file_path=tmp_path,
            filename=file.filename,
            folder_id=folder_id
        )
        
        return {
            "message": "تم رفع الملف بنجاح",  # File uploaded successfully
            "file": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"فشل رفع الملف: {str(e)}"  # Upload failed
        )
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get(
    "/{file_id}",
    summary="Get file details"
)
async def get_file(file_id: str, request: Request):
    """Get metadata for a single file."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    file = file_service.get_file(file_id)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"  # File not found
        )
    
    # Check ownership
    if file.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مسموح"  # Not allowed
        )
    
    return file


@router.get(
    "/{file_id}/download",
    summary="Download a file"
)
async def download_file(file_id: str, request: Request):
    """Download a file."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    file = file_service.get_file(file_id)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"
        )
    
    # Check ownership
    if file.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مسموح"
        )
    
    if file.get("is_folder"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكن تحميل مجلد"  # Cannot download folder
        )
    
    # Download to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.get('filename')}") as tmp:
        output_path = tmp.name
    
    try:
        file_service.download_file(file_id, output_path)
        
        return FileResponse(
            output_path,
            filename=file.get("filename"),
            media_type="application/octet-stream",
            background=None  # Will be deleted after response
        )
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"فشل تحميل الملف: {str(e)}"  # Download failed
        )


@router.patch(
    "/{file_id}",
    summary="Rename file"
)
async def rename_file(file_id: str, request: Request):
    """Rename a file."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    body = await request.json()
    
    new_name = body.get("name", "").strip()
    
    if not new_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الاسم مطلوب"  # Name required
        )
    
    success = file_service.rename_file(file_id, user_id, new_name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"
        )
    
    return {"message": "تم تغيير الاسم بنجاح", "success": True}


@router.post(
    "/{file_id}/move",
    summary="Move file to folder"
)
async def move_file(file_id: str, request: Request):
    """Move a file to a different folder."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    body = await request.json()
    
    new_folder_id = body.get("folder_id")  # None for root
    
    success = file_service.move_file(file_id, user_id, new_folder_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"
        )
    
    return {"message": "تم نقل الملف بنجاح", "success": True}


@router.delete(
    "/{file_id}",
    summary="Delete file (move to trash)"
)
async def delete_file(file_id: str, request: Request, permanent: bool = False):
    """Delete a file. By default moves to trash, use permanent=true for hard delete."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    success = file_service.delete_file(file_id, user_id, permanent=permanent)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"
        )
    
    return {"message": "تم حذف الملف بنجاح", "success": True}


@router.post(
    "/{file_id}/restore",
    summary="Restore file from trash"
)
async def restore_file(file_id: str, request: Request):
    """Restore a file from trash."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    success = file_service.restore_file(file_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"
        )
    
    return {"message": "تم استعادة الملف بنجاح", "success": True}


@router.get(
    "/{file_id}/share",
    summary="Create share link"
)
async def create_share_link(file_id: str, request: Request):
    """Create a public share link for a file."""
    user = get_current_user(request)
    user_id = user.get("telegram_id")
    
    # Verify ownership
    file = file_service.get_file(file_id)
    if not file or file.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود"
        )
    
    token = file_service.create_share_link(file_id)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل إنشاء رابط المشاركة"
        )
    
    return {
        "token": token,
        "url": f"/share/{token}"
    }
