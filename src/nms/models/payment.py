"""Payment-related data models."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class PaymentInitiateRequest(BaseModel):
    """Request model for payment initiation."""

    order_id: int = Field(..., description="Order ID to create payment for")


class PaymentInitiateResponse(BaseModel):
    """Response model for payment initiation."""

    status: str = Field(..., description="Operation status")
    payment_id: int = Field(..., description="Created payment ID")
    payment_url: str = Field(..., description="URL for payment checkout page")


class PaymentStatusResponse(BaseModel):
    """Response model for payment status check."""

    payment_id: int
    order_id: int
    amount: Decimal
    status: str
    provider: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymeWebhookPayload(BaseModel):
    """Payload from Payme webhook (demo emulation)."""

    order_id: int = Field(..., description="Order ID")
    token: str = Field(..., description="Payment security token")
    amount: Decimal = Field(..., description="Payment amount")
    status: str = Field(..., description="Payment status: paid or failed")
