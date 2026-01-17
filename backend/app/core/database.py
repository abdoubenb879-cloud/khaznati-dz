"""
Khaznati DZ - Database Module

Re-exports the Supabase client for database operations.
This module provides compatibility with existing imports.
"""

from app.core.supabase_client import db, get_db, SupabaseClient

# Export for backwards compatibility
__all__ = ['db', 'get_db', 'SupabaseClient']


async def create_tables():
    """No-op for Supabase (tables are managed via Supabase dashboard)."""
    print("✅ Using Supabase - tables managed externally")
    pass


async def drop_tables():
    """No-op for Supabase (tables are managed via Supabase dashboard)."""
    pass
