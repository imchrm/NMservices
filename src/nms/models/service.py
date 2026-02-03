"""Service-related data models."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ServiceResponse(BaseModel):
    """Response model for service."""

    id: int
    name: str
    description: str | None = None
    base_price: Decimal | None = None
    duration_minutes: int | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class ServiceCreateRequest(BaseModel):
    """Request model for service creation."""

    name: str = Field(..., min_length=1, max_length=255, description="Service name")
    description: str | None = Field(None, description="Service description")
    base_price: Decimal | None = Field(None, ge=0, description="Base price in sum")
    duration_minutes: int | None = Field(None, ge=1, description="Duration in minutes")
    is_active: bool = Field(True, description="Whether service is active")


class ServiceUpdateRequest(BaseModel):
    """Request model for service update."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Service name")
    description: str | None = Field(None, description="Service description")
    base_price: Decimal | None = Field(None, ge=0, description="Base price in sum")
    duration_minutes: int | None = Field(None, ge=1, description="Duration in minutes")
    is_active: bool | None = Field(None, description="Whether service is active")


class ServiceListResponse(BaseModel):
    """Response model for service list."""

    services: list[ServiceResponse]
    total: int
