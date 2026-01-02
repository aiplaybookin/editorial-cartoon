"""
Application configuration
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union, Optional
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Arrakis-Marketeer"
    APP_VERSION: str = "0.0.1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/email_campaign_db"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    
    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    #ALLOWED_ORIGINS: List[str] = [
    #    "http://localhost:3000",
    #    "http://localhost:8000",
    #]
    
    # Email (for password reset)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@yourdomain.com"
    EMAILS_FROM_NAME: str = "Email Campaign Manager"
    
    # Redis (for token blacklist)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Anthropic API
    ANTHROPIC_API_KEY: str = ""  # Set in .env
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()