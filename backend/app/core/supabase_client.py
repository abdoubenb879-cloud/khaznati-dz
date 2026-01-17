"""
Khaznati DZ - Supabase Database Client

Uses Supabase REST API directly for database operations.
Adapted from CloudVault's database_cloud.py for Python compatibility.
"""

import os
import time
import random
import urllib.request
import urllib.parse
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.core.config import settings


class SupabaseClient:
    """Handles database operations via Supabase REST API."""
    
    def __init__(self):
        self.url = settings.supabase_url
        self.key = settings.supabase_key
        if not self.url or not self.key:
            print("[DB] Warning: SUPABASE_URL or SUPABASE_KEY missing. Cloud DB won't work.")
            self.client = None
        else:
            self.client = True  # Flag to indicate we're ready
            print(f"[DB] Supabase REST API initialized")
    
    def _request(self, table: str, method: str = "GET", data: dict = None, params: dict = None) -> Optional[List[Dict]]:
        """Make a request to Supabase REST API."""
        if not self.client:
            return None
            
        url = f"{self.url}/rest/v1/{table}"
        if params:
            url += "?" + urllib.parse.urlencode(params, safe=':,.')
        
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        body = json.dumps(data).encode('utf-8') if data else None
        
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = response.read().decode('utf-8')
                return json.loads(result) if result else []
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"[DB] HTTP Error {e.code}: {error_body}")
            raise
        except Exception as e:
            print(f"[DB] Request error: {e}")
            raise

    # ========== USER METHODS ==========
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email for login."""
        result = self._request("users", params={"email": f"eq.{email}", "select": "*"})
        return result[0] if result else None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by telegram_id."""
        result = self._request("users", params={"telegram_id": f"eq.{user_id}", "select": "*"})
        return result[0] if result else None
    
    def create_user(self, name: str, email: str, password_hash: str) -> Optional[str]:
        """Create a new user with email/password."""
        # Generate a unique ID for the new user
        user_id = -random.randint(1000000000, 9999999999)
        data = {
            "telegram_id": str(user_id),
            "username": name,
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "is_premium": False,
            # Required fields from Supabase schema
            "session_string": "email_user",
            "api_id": 0,
            "api_hash": "email_auth"
        }
        try:
            result = self._request("users", method="POST", data=data)
            if result and len(result) > 0:
                return result[0].get('telegram_id', str(user_id))
            return str(user_id)
        except Exception as e:
            print(f"[DB] Error creating user: {e}")
            return None
    
    def update_password(self, user_id: str, password_hash: str) -> bool:
        """Update user's password hash."""
        try:
            self._request("users", method="PATCH", 
                         data={"password_hash": password_hash}, 
                         params={"telegram_id": f"eq.{user_id}"})
            return True
        except:
            return False

    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user fields."""
        try:
            self._request("users", method="PATCH", 
                         data=kwargs, 
                         params={"telegram_id": f"eq.{user_id}"})
            return True
        except:
            return False
    
    def set_reset_token(self, user_id: str, token: str):
        """Set password reset token for user."""
        self._request("users", method="PATCH", 
                     data={"reset_token": token}, 
                     params={"telegram_id": f"eq.{user_id}"})
    
    def get_user_by_reset_token(self, token: str) -> Optional[Dict]:
        """Get user by reset token."""
        result = self._request("users", params={"reset_token": f"eq.{token}", "select": "*"})
        return result[0] if result else None
    
    def clear_reset_token(self, user_id: str):
        """Clear the reset token after password reset."""
        self._request("users", method="PATCH", 
                     data={"reset_token": None}, 
                     params={"telegram_id": f"eq.{user_id}"})

    # ========== FILE METHODS ==========
    
    def add_file(self, user_id: str, filename: str, total_size: int, chunk_count: int, 
                 parent_id: str = None, thumbnail: str = None) -> Optional[str]:
        """Tracks an uploaded file for a specific user."""
        data = {
            "user_id": str(user_id),
            "filename": filename,
            "total_size": total_size,
            "chunk_count": chunk_count,
            "parent_id": parent_id,
            "is_folder": False
        }
        print(f"[DB DEBUG] Adding file with data: {data}")
        result = self._request("files", method="POST", data=data)
        return result[0]['id'] if result else None
    
    def get_file(self, file_id: str) -> Optional[Dict]:
        """Retrieves file metadata by ID."""
        result = self._request("files", params={"id": f"eq.{file_id}", "select": "*"})
        return result[0] if result else None
    
    def list_files(self, user_id: str, parent_id: str = None) -> List[Dict]:
        """Lists files in a specific folder (or root), excluding deleted files."""
        if parent_id is None:
            params = {
                "user_id": f"eq.{user_id}", 
                "parent_id": "is.null", 
                "or": "(is_deleted.is.null,is_deleted.eq.false)",
                "select": "*", 
                "order": "is_folder.desc,created_at.desc"
            }
        else:
            params = {
                "user_id": f"eq.{user_id}", 
                "parent_id": f"eq.{parent_id}", 
                "or": "(is_deleted.is.null,is_deleted.eq.false)",
                "select": "*", 
                "order": "is_folder.desc,created_at.desc"
            }
        
        result = self._request("files", params=params)
        return result if result else []
    
    def rename_file(self, file_id: str, user_id: str, new_name: str):
        """Rename a file."""
        self._request("files", method="PATCH", 
                     data={"filename": new_name}, 
                     params={"id": f"eq.{file_id}", "user_id": f"eq.{user_id}"})
    
    def move_file(self, file_id: str, user_id: str, new_parent_id: str = None):
        """Update a file's parent folder."""
        data = {"parent_id": new_parent_id}
        self._request("files", method="PATCH", data=data, params={
            "id": f"eq.{file_id}",
            "user_id": f"eq.{user_id}"
        })
    
    def soft_delete_file(self, file_id: str, user_id: str):
        """Soft delete a file (move to trash)."""
        self._request("files", method="PATCH", 
                     data={"is_deleted": True, "deleted_at": datetime.utcnow().isoformat()}, 
                     params={"id": f"eq.{file_id}", "user_id": f"eq.{user_id}"})
    
    def restore_file(self, file_id: str, user_id: str):
        """Restore a file from trash."""
        self._request("files", method="PATCH", 
                     data={"is_deleted": False, "deleted_at": None}, 
                     params={"id": f"eq.{file_id}", "user_id": f"eq.{user_id}"})
    
    def permanent_delete(self, file_id: str, user_id: str):
        """Permanently delete a file and its chunks."""
        # Delete chunks first
        self._request("chunks", method="DELETE", params={"file_id": f"eq.{file_id}"})
        # Then delete file
        self._request("files", method="DELETE", params={"id": f"eq.{file_id}", "user_id": f"eq.{user_id}"})
    
    def get_trash(self, user_id: str) -> List[Dict]:
        """Get all deleted files for a user."""
        result = self._request("files", params={
            "user_id": f"eq.{user_id}", 
            "is_deleted": "eq.true",
            "select": "*",
            "order": "deleted_at.desc"
        })
        return result if result else []
    
    def empty_trash(self, user_id: str):
        """Permanently delete all trashed files for a user."""
        trashed = self.get_trash(user_id)
        for file in trashed:
            self.permanent_delete(file['id'], user_id)

    # ========== FOLDER METHODS ==========
    
    def create_folder(self, user_id: str, name: str, parent_id: str = None) -> Optional[str]:
        """Creates a new folder for a user."""
        data = {
            "user_id": str(user_id),
            "filename": name,
            "total_size": 0,
            "chunk_count": 0,
            "parent_id": parent_id,
            "is_folder": True
        }
        result = self._request("files", method="POST", data=data)
        return result[0]['id'] if result else None
    
    def get_or_create_folder(self, user_id: str, name: str, parent_id: str = None) -> Optional[str]:
        """Finds an existing folder or creates a new one."""
        params = {
            "user_id": f"eq.{user_id}",
            "filename": f"eq.{name}",
            "is_folder": "is.true",
            "is_deleted": "is.false"
        }
        if parent_id:
            params["parent_id"] = f"eq.{parent_id}"
        else:
            params["parent_id"] = "is.null"

        existing = self._request("files", method="GET", params=params)
        if existing:
            return existing[0]['id']

        return self.create_folder(user_id, name, parent_id)
    
    def get_all_folders(self, user_id: str) -> List[Dict]:
        """Get all folders for a user."""
        result = self._request("files", params={
            "user_id": f"eq.{user_id}",
            "is_folder": "eq.true",
            "is_deleted": "neq.true",
            "select": "id,filename"
        })
        return result if result else []
    
    def get_breadcrumbs(self, folder_id: str) -> List[Dict]:
        """Returns list of {'id': id, 'name': name} for breadcrumb navigation."""
        breadcrumbs = []
        current_id = folder_id
        for _ in range(10): 
            if current_id is None: 
                break
            
            result = self._request("files", params={"id": f"eq.{current_id}", "select": "id,filename,parent_id"})
            if not result: 
                break
            
            folder = result[0]
            breadcrumbs.insert(0, {'id': folder['id'], 'name': folder['filename']})
            current_id = folder['parent_id']
            
        return breadcrumbs

    # ========== CHUNK METHODS ==========
    
    def add_chunk(self, file_id: str, chunk_index: int, message_id: int, chunk_size: int):
        """Tracks individual chunks for a file."""
        data = {
            "file_id": file_id,
            "chunk_index": chunk_index,
            "message_id": message_id,
            "chunk_size": chunk_size
        }
        self._request("chunks", method="POST", data=data)
    
    def get_chunks(self, file_id: str) -> List[Dict]:
        """Retrieves all chunks for a file."""
        result = self._request("chunks", params={"file_id": f"eq.{file_id}", "select": "*", "order": "chunk_index.asc"})
        return result if result else []

    # ========== SHARE METHODS ==========
    
    def set_share_token(self, file_id: str, token: str):
        """Updates the share token for a file."""
        self._request("files", method="PATCH", data={"share_token": token}, params={"id": f"eq.{file_id}"})
    
    def get_file_by_token(self, token: str) -> Optional[Dict]:
        """Retrieves file metadata by share token."""
        result = self._request("files", params={"share_token": f"eq.{token}", "select": "*"})
        return result[0] if result else None


# Singleton instance
_db_instance = None

def get_db() -> SupabaseClient:
    """Get the global database client instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = SupabaseClient()
    return _db_instance


# Convenience export
db = get_db()
