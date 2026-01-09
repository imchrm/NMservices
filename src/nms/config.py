"""Configuration module for NMservices."""

from functools import lru_cache
from pydantic import Field, BaseModel   
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


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
