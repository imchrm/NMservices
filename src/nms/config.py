"""Configuration module for NMservices."""

import json
from functools import lru_cache
from pydantic import Field, BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class LoggingConfig(BaseModel):
    """Logging Configuration"""

    level: str = "DEBUG"
    format: str = "%(asctime)s - %(levelname)s - %(message)s"

class Settings(BaseSettings):
    """Application settings."""
    logging: LoggingConfig = LoggingConfig()
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )

    # API Security
    api_secret_key: str = Field(default="test_secret", alias="API_SECRET_KEY")
    api_key_name: str = Field(default="X-API-Key")
    admin_secret_key: str = Field(default="admin_secret", alias="ADMIN_SECRET_KEY")

    # Application
    app_title: str = Field(default="NoMus Backend API (PoC)")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)

    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/nomus",
        alias="DATABASE_URL",
    )

    # Telegram Bot (for sending notifications to users)
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")

    # Payment
    payment_base_url: str = Field(
        default="http://localhost:8000",
        alias="PAYMENT_BASE_URL",
        description="Base URL for payment checkout pages (used to build payment links)",
    )

    # CORS (Cross-Origin Resource Sharing)
    # Type is str | list[str] so pydantic-settings won't force json.loads()
    # on plain string values like "*" or "https://example.com"
    cors_origins: str | list[str] = Field(
        default=["http://localhost:5173"],  # Vite dev server
        alias="CORS_ORIGINS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if not v.strip():
                return ["http://localhost:5173"]
            if v.strip() == "*":
                return ["*"]
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
