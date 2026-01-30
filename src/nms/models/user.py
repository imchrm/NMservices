"""User-related data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""

    phone_number: str = Field(..., description="User's phone number")
    telegram_id: int | None = Field(None, description="User's Telegram ID")
    language_code: str | None = Field(None, description="User's preferred language code (ru, uz, en)")


class RegistrationResponse(BaseModel):
    """Response model for user registration."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message")
    user_id: int = Field(..., description="Created user ID")


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int = Field(..., description="User ID")
    phone_number: str = Field(..., description="User's phone number")
    telegram_id: int | None = Field(None, description="User's Telegram ID")
    language_code: str | None = Field(None, description="User's preferred language code")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class LanguageUpdateRequest(BaseModel):
    """Request model for updating user's language."""

    language_code: str = Field(..., description="Language code (ru, uz, en)")


class LanguageUpdateResponse(BaseModel):
    """Response model for language update."""

    status: str = Field(..., description="Operation status")
