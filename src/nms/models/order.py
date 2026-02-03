"""Order-related data models."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    """Request model for order creation."""

    user_id: int = Field(..., description="User ID creating the order")
    service_id: int = Field(..., description="Service ID")
    address_text: str | None = Field(None, description="Address for service delivery")
    scheduled_at: datetime | None = Field(None, description="Scheduled time for service")
    notes: str | None = Field(None, description="Additional notes")


class OrderResponse(BaseModel):
    """Response model for order creation."""

    status: str = Field(..., description="Operation status")
    order_id: int = Field(..., description="Created order ID")
    message: str = Field(..., description="Response message")


class OrderDetailResponse(BaseModel):
    """Detailed response model for order."""

    id: int
    user_id: int
    service_id: int | None = None
    service_name: str | None = None
    status: str
    total_amount: Decimal | None = None
    address_text: str | None = None
    scheduled_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
