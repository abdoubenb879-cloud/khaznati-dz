"""
Khaznati DZ - Storage Service

S3-compatible storage operations for file management.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List
from uuid import UUID
import hashlib

import aioboto3
from botocore.config import Config

from app.core.config import settings


class StorageService:
    """Service for S3-compatible object storage operations."""
    
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket_name = settings.s3_bucket_name
        self.config = Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        )
    
    def _get_client_kwargs(self) -> dict:
        """Get common kwargs for S3 client."""
        return {
            "endpoint_url": settings.s3_endpoint_url or None,
            "aws_access_key_id": settings.s3_access_key_id,
            "aws_secret_access_key": settings.s3_secret_access_key,
            "region_name": settings.s3_region,
            "config": self.config
        }
    
    def generate_storage_key(
        self,
        user_id: UUID,
        file_id: UUID,
        filename: str
    ) -> str:
        """
        Generate a unique storage key for a file.
        
        Format: users/{user_id}/{year}/{month}/{file_id}/{safe_filename}
        """
        now = datetime.now(timezone.utc)
        safe_name = self._sanitize_filename(filename)
        return f"users/{user_id}/{now.year}/{now.month:02d}/{file_id}/{safe_name}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for storage."""
        # Remove path separators and null bytes
        forbidden = ['/', '\\', '\0', '..']
        result = filename
        for char in forbidden:
            result = result.replace(char, '_')
        # Limit length
        if len(result) > 200:
            name, ext = result.rsplit('.', 1) if '.' in result else (result, '')
            max_name_len = 200 - len(ext) - 1
            result = f"{name[:max_name_len]}.{ext}" if ext else name[:200]
        return result
    
    async def generate_upload_url(
        self,
        storage_key: str,
        content_type: str = "application/octet-stream",
        expires_in: int = 3600
    ) -> str:
        """
        Generate a presigned URL for direct file upload.
        
        Args:
            storage_key: S3 object key
            content_type: MIME type of the file
            expires_in: URL expiration in seconds
            
        Returns:
            Presigned upload URL
        """
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            url = await s3.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": storage_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in
            )
            return url
    
    async def generate_download_url(
        self,
        storage_key: str,
        filename: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate a presigned URL for file download.
        
        Args:
            storage_key: S3 object key
            filename: Original filename for Content-Disposition
            expires_in: URL expiration in seconds
            
        Returns:
            Presigned download URL
        """
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            url = await s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": storage_key,
                    "ResponseContentDisposition": f'attachment; filename="{filename}"',
                },
                ExpiresIn=expires_in
            )
            return url
    
    async def initiate_multipart_upload(
        self,
        storage_key: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Initiate a multipart upload for large files.
        
        Args:
            storage_key: S3 object key
            content_type: MIME type
            
        Returns:
            Upload ID for the multipart upload
        """
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            response = await s3.create_multipart_upload(
                Bucket=self.bucket_name,
                Key=storage_key,
                ContentType=content_type
            )
            return response["UploadId"]
    
    async def generate_part_upload_urls(
        self,
        storage_key: str,
        upload_id: str,
        total_size: int,
        part_size: int = 10 * 1024 * 1024,  # 10 MB default
        expires_in: int = 3600
    ) -> List[dict]:
        """
        Generate presigned URLs for multipart upload parts.
        
        Args:
            storage_key: S3 object key
            upload_id: Multipart upload ID
            total_size: Total file size in bytes
            part_size: Size of each part
            expires_in: URL expiration in seconds
            
        Returns:
            List of part info with presigned URLs
        """
        parts = []
        part_number = 1
        remaining = total_size
        
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            while remaining > 0:
                current_part_size = min(part_size, remaining)
                
                url = await s3.generate_presigned_url(
                    "upload_part",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": storage_key,
                        "UploadId": upload_id,
                        "PartNumber": part_number,
                    },
                    ExpiresIn=expires_in
                )
                
                parts.append({
                    "part_number": part_number,
                    "presigned_url": url,
                    "size_bytes": current_part_size
                })
                
                part_number += 1
                remaining -= current_part_size
        
        return parts
    
    async def complete_multipart_upload(
        self,
        storage_key: str,
        upload_id: str,
        parts: List[dict]
    ) -> dict:
        """
        Complete a multipart upload.
        
        Args:
            storage_key: S3 object key
            upload_id: Multipart upload ID
            parts: List of {part_number, etag}
            
        Returns:
            Completion response
        """
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            response = await s3.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=storage_key,
                UploadId=upload_id,
                MultipartUpload={
                    "Parts": [
                        {"PartNumber": p["part_number"], "ETag": p["etag"]}
                        for p in sorted(parts, key=lambda x: x["part_number"])
                    ]
                }
            )
            return response
    
    async def abort_multipart_upload(
        self,
        storage_key: str,
        upload_id: str
    ) -> None:
        """Abort a multipart upload."""
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            await s3.abort_multipart_upload(
                Bucket=self.bucket_name,
                Key=storage_key,
                UploadId=upload_id
            )
    
    async def delete_object(self, storage_key: str) -> None:
        """Delete an object from storage."""
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            await s3.delete_object(
                Bucket=self.bucket_name,
                Key=storage_key
            )
    
    async def delete_objects(self, storage_keys: List[str]) -> None:
        """Delete multiple objects from storage."""
        if not storage_keys:
            return
            
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            await s3.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    "Objects": [{"Key": key} for key in storage_keys]
                }
            )
    
    async def check_object_exists(self, storage_key: str) -> bool:
        """Check if an object exists in storage."""
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            try:
                await s3.head_object(
                    Bucket=self.bucket_name,
                    Key=storage_key
                )
                return True
            except Exception:
                return False
    
    async def get_object_size(self, storage_key: str) -> Optional[int]:
        """Get the size of an object in bytes."""
        async with self.session.client("s3", **self._get_client_kwargs()) as s3:
            try:
                response = await s3.head_object(
                    Bucket=self.bucket_name,
                    Key=storage_key
                )
                return response.get("ContentLength")
            except Exception:
                return None


# Singleton instance
storage_service = StorageService()
