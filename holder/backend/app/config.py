"""
Configuration module for SSI Holder FastAPI application
"""
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app configuration
    app_name: str = "SSI Holder API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_secret_key: str = "jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Database
    database_url: str = "sqlite:///./holder.db"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # ACA-Py integration
    acapy_admin_url: str = "http://localhost:8031"
    acapy_admin_api_key: str = "99c07c82db457e281a5afda23b7b8d4ae28f36685e008768ff610c97421cd335"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()