from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional, Union
import os
import json


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Basic configuration
    APP_NAME: str = "Card Battle Arena"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    ENVIRONMENT: str = Field(default="development", validation_alias="ENVIRONMENT")

    # Security
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, validation_alias="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, validation_alias="DATABASE_MAX_OVERFLOW")

    # Redis
    REDIS_URL: str = Field(..., validation_alias="REDIS_URL")
    REDIS_DB: int = Field(default=0, validation_alias="REDIS_DB")

    # CORS
    ALLOWED_HOSTS: Union[List[str], str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        validation_alias="ALLOWED_HOSTS"
    )

    # Game configuration
    MAX_DECK_SIZE: int = Field(default=30, validation_alias="MAX_DECK_SIZE")
    STARTING_HAND_SIZE: int = Field(default=5, validation_alias="STARTING_HAND_SIZE")
    MAX_MANA: int = Field(default=10, validation_alias="MAX_MANA")
    TURN_TIME_LIMIT_SECONDS: int = Field(default=90, validation_alias="TURN_TIME_LIMIT_SECONDS")

    # Matching system
    ELO_INITIAL_RATING: int = Field(default=1000, validation_alias="ELO_INITIAL_RATING")
    MATCHMAKING_TIMEOUT_SECONDS: int = Field(default=300, validation_alias="MATCHMAKING_TIMEOUT_SECONDS")
    MAX_MATCHMAKING_RANGE: int = Field(default=200, validation_alias="MAX_MATCHMAKING_RANGE")

    # WebSocket
    WS_CONNECTION_TIMEOUT_SECONDS: int = Field(default=3600, validation_alias="WS_CONNECTION_TIMEOUT_SECONDS")
    WS_HEARTBEAT_INTERVAL_SECONDS: int = Field(default=30, validation_alias="WS_HEARTBEAT_INTERVAL_SECONDS")
    WS_MAX_MESSAGE_SIZE: int = Field(default=1024 * 1024, validation_alias="WS_MAX_MESSAGE_SIZE")  # 1MB

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, validation_alias="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_BURST: int = Field(default=10, validation_alias="RATE_LIMIT_BURST")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", validation_alias="LOG_FORMAT")

    # File uploads
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, validation_alias="MAX_UPLOAD_SIZE")  # 10MB
    UPLOAD_DIR: str = Field(default="uploads", validation_alias="UPLOAD_DIR")

    # Email (for password reset, notifications)
    SMTP_TLS: bool = Field(default=True, validation_alias="SMTP_TLS")
    SMTP_PORT: Optional[int] = Field(default=None, validation_alias="SMTP_PORT")
    SMTP_HOST: Optional[str] = Field(default=None, validation_alias="SMTP_HOST")
    SMTP_USER: Optional[str] = Field(default=None, validation_alias="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, validation_alias="SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[str] = Field(default=None, validation_alias="EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = Field(default=None, validation_alias="EMAILS_FROM_NAME")

    # External services
    SENTRY_DSN: Optional[str] = Field(default=None, validation_alias="SENTRY_DSN")
    GOOGLE_ANALYTICS_ID: Optional[str] = Field(default=None, validation_alias="GOOGLE_ANALYTICS_ID")

    # Feature flags
    ENABLE_REGISTRATION: bool = Field(default=True, validation_alias="ENABLE_REGISTRATION")
    ENABLE_PASSWORD_RESET: bool = Field(default=True, validation_alias="ENABLE_PASSWORD_RESET")
    ENABLE_SOCIAL_FEATURES: bool = Field(default=True, validation_alias="ENABLE_SOCIAL_FEATURES")
    ENABLE_SPECTATOR_MODE: bool = Field(default=True, validation_alias="ENABLE_SPECTATOR_MODE")
    ENABLE_TOURNAMENTS: bool = Field(default=False, validation_alias="ENABLE_TOURNAMENTS")

    # Cache settings
    CACHE_TTL_SECONDS: int = Field(default=300, validation_alias="CACHE_TTL_SECONDS")
    CARD_CACHE_TTL_SECONDS: int = Field(default=3600, validation_alias="CARD_CACHE_TTL_SECONDS")  # 1 hour

    @field_validator('ALLOWED_HOSTS', mode='before')
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            # Try to parse as JSON array first
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If that fails, split by comma
                return [host.strip() for host in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Validate critical settings
if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY must be at least 32 characters long")

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is required")

if not settings.REDIS_URL:
    raise ValueError("REDIS_URL is required")