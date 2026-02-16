"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Configurable Dashboard"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database - SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./dashboard.db"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Query Configuration
    QUERY_TIMEOUT: int = 30  # seconds
    MAX_QUERY_RESULTS: int = 10000
    
    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # seconds (5 minutes)
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()


settings = get_settings()
