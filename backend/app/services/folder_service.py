"""
Khaznati DZ - Folder Service

Business logic for folder operations using Supabase.
"""

from typing import Optional, List, Dict

from app.core.supabase_client import db


class FolderService:
    """Service class for folder operations."""
    
    def __init__(self):
        self.db = db
    
    def create_folder(self, user_id: str, name: str, parent_id: str = None) -> Optional[Dict]:
        """
        Create a new folder.
        
        Args:
            user_id: User's ID
            name: Folder name
            parent_id: Parent folder ID (None for root)
            
        Returns:
            Folder metadata dict if successful
        """
        folder_id = self.db.create_folder(user_id, name, parent_id)
        if folder_id:
            return self.get_folder(folder_id)
        return None
    
    def get_folder(self, folder_id: str) -> Optional[Dict]:
        """Get folder metadata."""
        file = self.db.get_file(folder_id)
        if file and file.get("is_folder"):
            return {
                "id": file["id"],
                "name": file["filename"],
                "parent_id": file.get("parent_id"),
                "created_at": file.get("created_at"),
            }
        return None
    
    def get_or_create_folder(self, user_id: str, name: str, parent_id: str = None) -> Optional[str]:
        """Find or create a folder by name."""
        return self.db.get_or_create_folder(user_id, name, parent_id)
    
    def list_folders(self, user_id: str, parent_id: str = None) -> List[Dict]:
        """List all folders in a parent folder (or root)."""
        all_items = self.db.list_files(user_id, parent_id)
        folders = [item for item in all_items if item.get("is_folder")]
        
        return [{
            "id": f["id"],
            "name": f["filename"],
            "parent_id": f.get("parent_id"),
            "created_at": f.get("created_at"),
        } for f in folders]
    
    def get_all_folders(self, user_id: str) -> List[Dict]:
        """Get all folders for a user (for move dialog)."""
        return self.db.get_all_folders(user_id)
    
    def rename_folder(self, folder_id: str, user_id: str, new_name: str) -> bool:
        """Rename a folder."""
        try:
            self.db.rename_file(folder_id, user_id, new_name)
            return True
        except:
            return False
    
    def move_folder(self, folder_id: str, user_id: str, new_parent_id: str = None) -> bool:
        """Move a folder to a different parent."""
        try:
            # Prevent moving folder into itself or its children
            if folder_id == new_parent_id:
                return False
            
            # Check if new_parent is a child of folder_id
            if new_parent_id:
                breadcrumbs = self.db.get_breadcrumbs(new_parent_id)
                for crumb in breadcrumbs:
                    if crumb["id"] == folder_id:
                        return False
            
            self.db.move_file(folder_id, user_id, new_parent_id)
            return True
        except:
            return False
    
    def delete_folder(self, folder_id: str, user_id: str, permanent: bool = False) -> bool:
        """
        Delete a folder.
        
        Args:
            folder_id: Folder's ID
            user_id: User's ID
            permanent: If True, permanently delete. If False, move to trash.
        """
        try:
            if permanent:
                # Recursively delete contents first
                contents = self.db.list_files(user_id, folder_id)
                for item in contents:
                    if item.get("is_folder"):
                        self.delete_folder(item["id"], user_id, permanent=True)
                    else:
                        self.db.permanent_delete(item["id"], user_id)
                
                # Delete the folder itself
                self.db.permanent_delete(folder_id, user_id)
            else:
                # Soft delete
                self.db.soft_delete_file(folder_id, user_id)
            
            return True
        except Exception as e:
            print(f"[FOLDER] Delete failed: {e}")
            return False
    
    def restore_folder(self, folder_id: str, user_id: str) -> bool:
        """Restore a folder from trash."""
        try:
            self.db.restore_file(folder_id, user_id)
            return True
        except:
            return False
    
    def get_breadcrumbs(self, folder_id: str) -> List[Dict]:
        """Get breadcrumb navigation for a folder."""
        return self.db.get_breadcrumbs(folder_id)
    
    def get_folder_path(self, folder_id: str) -> str:
        """Get the full path of a folder as a string."""
        breadcrumbs = self.get_breadcrumbs(folder_id)
        return "/" + "/".join([b["name"] for b in breadcrumbs])


# Convenience instance
folder_service = FolderService()
