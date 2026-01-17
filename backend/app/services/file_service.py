"""
Khaznati DZ - File Service

Business logic for file operations using Telegram storage and Supabase.
"""

import os
import tempfile
import secrets
from typing import Optional, List, Dict
from datetime import datetime

from app.core.supabase_client import db
from app.core.config import settings
from app.services.telegram_service import telegram_storage


class Chunker:
    """Utility class for splitting files into chunks."""
    
    def __init__(self, chunk_size: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
    
    def split_file(self, file_path: str, output_dir: str) -> List[str]:
        """Split a file into chunks and return list of chunk paths."""
        chunk_paths = []
        chunk_index = 0
        
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(self.chunk_size)
                if not data:
                    break
                
                chunk_path = os.path.join(output_dir, f"chunk_{chunk_index}")
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(data)
                
                chunk_paths.append(chunk_path)
                chunk_index += 1
        
        return chunk_paths
    
    def join_chunks(self, chunk_paths: List[str], output_path: str) -> str:
        """Join chunks back into a single file."""
        with open(output_path, 'wb') as output_file:
            for chunk_path in sorted(chunk_paths):
                with open(chunk_path, 'rb') as chunk_file:
                    output_file.write(chunk_file.read())
        return output_path


class FileService:
    """Service class for file operations."""
    
    def __init__(self):
        self.db = db
        self.storage = telegram_storage
        self.chunker = Chunker()
    
    def list_files(self, user_id: str, folder_id: str = None) -> List[Dict]:
        """List files in a folder (or root if folder_id is None)."""
        files = self.db.list_files(user_id, folder_id)
        
        # Format response
        result = []
        for f in files:
            result.append({
                "id": f["id"],
                "name": f["filename"],
                "size": f.get("total_size", 0),
                "is_folder": f.get("is_folder", False),
                "parent_id": f.get("parent_id"),
                "created_at": f.get("created_at"),
                "share_token": f.get("share_token"),
            })
        return result
    
    def get_file(self, file_id: str) -> Optional[Dict]:
        """Get file metadata."""
        return self.db.get_file(file_id)
    
    def upload_file(
        self, 
        user_id: str, 
        file_path: str, 
        filename: str, 
        folder_id: str = None,
        progress_callback=None
    ) -> Optional[Dict]:
        """
        Upload a file to Telegram storage.
        
        Args:
            user_id: User's ID
            file_path: Path to the local file
            filename: Original filename
            folder_id: Parent folder ID (None for root)
            progress_callback: Optional progress callback
            
        Returns:
            File metadata dict if successful
        """
        try:
            file_size = os.path.getsize(file_path)
            
            # Determine number of chunks needed
            chunk_count = (file_size + settings.chunk_size - 1) // settings.chunk_size
            
            # Create file record in database
            file_id = self.db.add_file(
                user_id=user_id,
                filename=filename,
                total_size=file_size,
                chunk_count=chunk_count,
                parent_id=folder_id
            )
            
            if not file_id:
                raise Exception("Failed to create file record")
            
            # Create temp directory for chunks
            with tempfile.TemporaryDirectory() as temp_dir:
                # Split file into chunks
                chunk_paths = self.chunker.split_file(file_path, temp_dir)
                
                # Upload chunks to Telegram
                messages = self.storage.upload_chunks(chunk_paths)
                
                # Record chunk metadata
                for idx, msg in enumerate(messages):
                    chunk_size = os.path.getsize(chunk_paths[idx])
                    self.db.add_chunk(
                        file_id=file_id,
                        chunk_index=idx,
                        message_id=msg.id,
                        chunk_size=chunk_size
                    )
            
            return self.get_file(file_id)
            
        except Exception as e:
            print(f"[FILE] Upload failed: {e}")
            raise
    
    def download_file(
        self, 
        file_id: str, 
        output_path: str,
        progress_callback=None
    ) -> Optional[str]:
        """
        Download a file from Telegram storage.
        
        Args:
            file_id: File's ID
            output_path: Path to save the file
            progress_callback: Optional progress callback
            
        Returns:
            Output path if successful
        """
        try:
            # Get file metadata
            file_meta = self.db.get_file(file_id)
            if not file_meta:
                raise Exception("File not found")
            
            if file_meta.get("is_folder"):
                raise Exception("Cannot download a folder")
            
            # Get chunks
            chunks = self.db.get_chunks(file_id)
            if not chunks:
                raise Exception("No chunks found for file")
            
            # Extract message IDs
            message_ids = [c["message_id"] for c in sorted(chunks, key=lambda x: x["chunk_index"])]
            
            # Download chunks
            with tempfile.TemporaryDirectory() as temp_dir:
                chunk_paths = self.storage.download_chunks(message_ids, temp_dir)
                
                # Filter out None values
                valid_chunks = [p for p in chunk_paths if p is not None]
                
                if len(valid_chunks) != len(message_ids):
                    raise Exception("Some chunks failed to download")
                
                # Join chunks
                self.chunker.join_chunks(valid_chunks, output_path)
            
            return output_path
            
        except Exception as e:
            print(f"[FILE] Download failed: {e}")
            raise
    
    def rename_file(self, file_id: str, user_id: str, new_name: str) -> bool:
        """Rename a file."""
        try:
            self.db.rename_file(file_id, user_id, new_name)
            return True
        except:
            return False
    
    def move_file(self, file_id: str, user_id: str, new_folder_id: str = None) -> bool:
        """Move a file to a different folder."""
        try:
            self.db.move_file(file_id, user_id, new_folder_id)
            return True
        except:
            return False
    
    def delete_file(self, file_id: str, user_id: str, permanent: bool = False) -> bool:
        """
        Delete a file.
        
        Args:
            file_id: File's ID
            user_id: User's ID
            permanent: If True, permanently delete. If False, move to trash.
        """
        try:
            if permanent:
                # Delete from Telegram first
                chunks = self.db.get_chunks(file_id)
                for chunk in chunks:
                    try:
                        self.storage.delete_message(chunk["message_id"])
                    except:
                        pass  # Continue even if Telegram delete fails
                
                # Delete from database
                self.db.permanent_delete(file_id, user_id)
            else:
                # Soft delete (move to trash)
                self.db.soft_delete_file(file_id, user_id)
            
            return True
        except Exception as e:
            print(f"[FILE] Delete failed: {e}")
            return False
    
    def restore_file(self, file_id: str, user_id: str) -> bool:
        """Restore a file from trash."""
        try:
            self.db.restore_file(file_id, user_id)
            return True
        except:
            return False
    
    def get_trash(self, user_id: str) -> List[Dict]:
        """Get all files in trash."""
        files = self.db.get_trash(user_id)
        return [{
            "id": f["id"],
            "name": f["filename"],
            "size": f.get("total_size", 0),
            "is_folder": f.get("is_folder", False),
            "deleted_at": f.get("deleted_at"),
        } for f in files]
    
    def empty_trash(self, user_id: str) -> int:
        """Empty the trash. Returns number of files deleted."""
        trashed = self.db.get_trash(user_id)
        count = 0
        for f in trashed:
            if self.delete_file(f["id"], user_id, permanent=True):
                count += 1
        return count
    
    def create_share_link(self, file_id: str) -> Optional[str]:
        """Create a share link for a file."""
        token = secrets.token_urlsafe(16)
        try:
            self.db.set_share_token(file_id, token)
            return token
        except:
            return None
    
    def get_file_by_share_token(self, token: str) -> Optional[Dict]:
        """Get a file by its share token."""
        return self.db.get_file_by_token(token)
    
    def get_breadcrumbs(self, folder_id: str) -> List[Dict]:
        """Get breadcrumb navigation for a folder."""
        return self.db.get_breadcrumbs(folder_id)


# Convenience instance
file_service = FileService()
