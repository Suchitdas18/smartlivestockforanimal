"""Application configuration settings."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Smart Livestock AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/livestock_ai"
    
    # For SQLite fallback (demo mode)
    USE_SQLITE: bool = True
    SQLITE_URL: str = "sqlite:///./livestock_ai.db"
    
    # Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_VIDEO_TYPES: list = ["video/mp4", "video/mpeg", "video/quicktime"]
    
    # AI Model Settings
    DETECTION_CONFIDENCE_THRESHOLD: float = 0.5
    HEALTH_CONFIDENCE_THRESHOLD: float = 0.7
    OCR_CONFIDENCE_THRESHOLD: float = 0.6
    
    # Alert Settings
    CRITICAL_HEALTH_THRESHOLD: float = 0.3
    ATTENTION_HEALTH_THRESHOLD: float = 0.6
    
    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
