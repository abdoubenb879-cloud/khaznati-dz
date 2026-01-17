"""
Khaznati DZ - Configuration Module

Central configuration management using Pydantic Settings.
Uses Telegram Bot for storage and Supabase for database.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Khaznati DZ"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    
    # Supabase Database
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Telegram Bot (File Storage)
    api_id: int = 0
    api_hash: str = ""
    bot_token: str = ""
    storage_channel_id: int = 0
    chunk_size: int = 20 * 1024 * 1024  # 20MB default
    
    # Multi-user mode
    multi_user: bool = True
    
    # Email (Resend)
    resend_api_key: str = ""
    resend_from_email: str = "noreply@khaznati.dz"
    
    # Email (SMTP Fallback)
    smtp_email: str = ""
    smtp_password: str = ""
    
    # Session & Security
    session_secret: str = "session-secret-change-me"
    session_expire_minutes: int = 1440  # 24 hours
    csrf_secret: str = "csrf-secret-change-me"
    allowed_origins: str = "http://localhost:8000"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    login_rate_limit: int = 5
    
    # File Upload
    max_upload_size_mb: int = 500
    allowed_extensions: str = "*"
    
    # Localization
    default_language: str = "ar"
    supported_languages: str = "ar,fr,en"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def supported_languages_list(self) -> List[str]:
        """Parse supported languages as a list."""
        return [lang.strip() for lang in self.supported_languages.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env.lower() == "production"
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024
    
    @property
    def chunk_size_bytes(self) -> int:
        """Chunk size in bytes."""
        return self.chunk_size


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience export
settings = get_settings()
