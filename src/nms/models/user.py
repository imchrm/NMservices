"""User-related data models."""

from pydantic import BaseModel, Field


class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""

    phone_number: str = Field(..., description="User's phone number")


class RegistrationResponse(BaseModel):
    """Response model for user registration."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message")
    user_id: int = Field(..., description="Created user ID")
