"""
Application Configuration
Supports PostgreSQL (production) and SQLite (testing)
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    ENVIRONMENT: str = "development"  # development, testing, production
    
    # Database - PostgreSQL (Main)
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/betsan_crm"
    
    # Database - SQLite (Testing)
    TEST_DATABASE_URL: str = "sqlite:///./test_betsan.db"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # TCMB
    TCMB_API_URL: str = "https://www.tcmb.gov.tr/kurlar/today.xml"
    
    # Application
    DEBUG: bool = True
    ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @property
    def active_database_url(self) -> str:
        """Get the active database URL based on environment"""
        if self.ENVIRONMENT == "testing":
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite"""
        return self.active_database_url.startswith("sqlite")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
