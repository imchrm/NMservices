"""Order-related data models."""

from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    """Request model for order creation."""

    user_id: int = Field(..., description="User ID creating the order")
    tariff_code: str = Field(..., description="Tariff code (e.g., 'standard_300')")


class OrderResponse(BaseModel):
    """Response model for order creation."""

    status: str = Field(..., description="Operation status")
    order_id: int = Field(..., description="Created order ID")
    message: str = Field(..., description="Response message")
