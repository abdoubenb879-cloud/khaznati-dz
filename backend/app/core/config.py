"""
Khaznati DZ - Configuration Module

Central configuration management using Pydantic Settings.
All environment variables are loaded and validated here.
"""

from functools import lru_cache
from typing import List
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
    
    # Database
    database_url: str = "postgresql://localhost/khaznati"
    
    # Storage (S3)
    storage_backend: str = "s3"
    s3_endpoint_url: str = ""
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket_name: str = "khaznati-files"
    s3_region: str = "auto"
    
    # Email
    email_backend: str = "smtp"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@khaznati.dz"
    email_from_name: str = "Khaznati DZ"
    
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
    chunk_size_mb: int = 5
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
        return self.chunk_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience export
settings = get_settings()
