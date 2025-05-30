from typing import Optional
from pydantic_settings import BaseSettings
import secrets
from functools import lru_cache
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Learning Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./elearning.db")
    SQLALCHEMY_DATABASE_URI: str = DATABASE_URL

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = os.getenv(
        "BACKEND_CORS_ORIGINS", 
        "http://localhost:3000"
    ).split(",")

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 