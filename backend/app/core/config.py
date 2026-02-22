"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Environment
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./dashboard.db"
    
    # Query Configuration
    QUERY_TIMEOUT: int = 30
    MAX_QUERY_RESULTS: int = 10000
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-10-21"
    
    # AI Configuration
    AI_MAX_TOKENS: int = 1024
    AI_TEMPERATURE: float = 0.1
    
    # Dashboard Configuration
    DASHBOARD_CONFIG_DIR: str = "../frontend/src/config/dashboards"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # ← ADD THIS: Ignore extra fields in .env
        
        @staticmethod
        def parse_env_var(field_name: str, raw_val: str):
            """Parse environment variables, especially for JSON arrays"""
            if field_name == 'CORS_ORIGINS':
                try:
                    return json.loads(raw_val)
                except json.JSONDecodeError:
                    # Fallback to comma-separated
                    return [origin.strip() for origin in raw_val.split(',')]
            return raw_val


settings = Settings()