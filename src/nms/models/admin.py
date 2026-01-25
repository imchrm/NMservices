"""Admin API request and response models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# User models
class AdminUserResponse(BaseModel):
    """Response model for user details."""
    
    id: int
    phone_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminUserWithOrdersResponse(BaseModel):
    """Response model for user with their orders."""
    
    id: int
    phone_number: str
    created_at: datetime
    updated_at: datetime
    orders: list["AdminOrderResponse"]

    class Config:
        from_attributes = True


class AdminUserCreateRequest(BaseModel):
    """Request model for creating a user."""
    
    phone_number: str = Field(..., description="User's phone number")


class AdminUserListResponse(BaseModel):
    """Response model for list of users."""
    
    users: list[AdminUserResponse]
    total: int


# Order models
class AdminOrderResponse(BaseModel):
    """Response model for order details."""
    
    id: int
    user_id: int
    status: str
    total_amount: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminOrderWithUserResponse(BaseModel):
    """Response model for order with user details."""
    
    id: int
    user_id: int
    status: str
    total_amount: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    user: AdminUserResponse

    class Config:
        from_attributes = True


class AdminOrderCreateRequest(BaseModel):
    """Request model for creating an order."""
    
    user_id: int = Field(..., description="User ID")
    status: str = Field(default="pending", description="Order status")
    total_amount: Optional[Decimal] = Field(None, description="Total amount")
    notes: Optional[str] = Field(None, description="Order notes")


class AdminOrderUpdateRequest(BaseModel):
    """Request model for updating an order."""
    
    status: Optional[str] = Field(None, description="Order status")
    total_amount: Optional[Decimal] = Field(None, description="Total amount")
    notes: Optional[str] = Field(None, description="Order notes")


class AdminOrderListResponse(BaseModel):
    """Response model for list of orders."""
    
    orders: list[AdminOrderResponse]
    total: int


# Statistics models
class AdminStatsResponse(BaseModel):
    """Response model for database statistics."""
    
    total_users: int
    total_orders: int
    orders_by_status: dict[str, int]
