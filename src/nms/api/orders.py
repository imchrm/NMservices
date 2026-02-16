"""Order-related API endpoints."""

import logging
from typing import Optional
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from ..models import OrderCreateRequest, OrderResponse
from ..models.db_models import Order, User, Service
from ..services.order import OrderService
from ..database import get_db
from .dependencies import get_api_key

router = APIRouter(prefix="/orders", tags=["orders"])
order_service = OrderService()
log = logging.getLogger(__name__)


@router.post(
    "",
    response_model=OrderResponse,
    dependencies=[Depends(get_api_key)],
    summary="Create new order",
)
async def create_order(
    request: OrderCreateRequest, db=Depends(get_db)
) -> OrderResponse:
    """
    Create a new order with payment processing.

    Args:
        request: Order creation data (user_id, service_id, address_text, scheduled_at, notes)
        db: Database session

    Returns:
        Order response with order ID

    Raises:
        HTTPException: If user doesn't exist, service not found, or order creation fails
    """
    try:
        order_id = await order_service.create_order(
            user_id=request.user_id,
            service_id=request.service_id,
            db=db,
            address_text=request.address_text,
            scheduled_at=request.scheduled_at,
            notes=request.notes,
        )
        return OrderResponse(
            status="ok", order_id=order_id, message="Order created and payment processed"
        )
    except ValueError as e:
        log.error("Error creating order: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        log.error("Error creating order: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later."
        ) from e


# ─── Active order endpoint ───────────────────────────────────────────

_ACTIVE_STATUSES = {"pending", "confirmed", "in_progress"}


class ActiveOrderDetail(BaseModel):
    order_id: int
    service_name: Optional[str] = None
    total_amount: Optional[Decimal] = None
    address_text: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ActiveOrdersResponse(BaseModel):
    """Response for active orders lookup."""

    orders: list[ActiveOrderDetail] = []


@router.get(
    "/active",
    response_model=ActiveOrdersResponse,
    dependencies=[Depends(get_api_key)],
    summary="Get user's active orders",
)
async def get_active_orders(
    telegram_id: int = Query(..., description="User's Telegram ID"),
    db: AsyncSession = Depends(get_db),
) -> ActiveOrdersResponse:
    """
    Returns all active orders for the user.

    Active = status in (pending, confirmed, in_progress).
    """
    try:
        user_result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return ActiveOrdersResponse()

        result = await db.execute(
            select(Order, Service.name.label("service_name"))
            .outerjoin(Service, Order.service_id == Service.id)
            .where(
                Order.user_id == user.id,
                Order.status.in_(_ACTIVE_STATUSES),
            )
            .order_by(Order.created_at.desc())
        )
        rows = result.all()
        if not rows:
            return ActiveOrdersResponse()

        orders = [
            ActiveOrderDetail(
                order_id=order.id,
                service_name=svc_name,
                total_amount=order.total_amount,
                address_text=order.address_text,
                status=order.status,
                created_at=order.created_at,
            )
            for order, svc_name in rows
        ]
        return ActiveOrdersResponse(orders=orders)
    except Exception as e:
        log.error("Error fetching active orders: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch active orders",
        ) from e


# ─── Notification endpoints ──────────────────────────────────────────


class PendingNotification(BaseModel):
    """One pending status notification."""

    order_id: int
    service_name: Optional[str] = None
    total_amount: Optional[Decimal] = None
    status: str
    notified_status: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class PendingNotificationsResponse(BaseModel):
    notifications: list[PendingNotification]


class AckRequest(BaseModel):
    telegram_id: int = Field(..., description="Telegram ID of the user")
    order_ids: list[int] = Field(..., description="Order IDs to acknowledge")


@router.get(
    "/pending-notifications",
    response_model=PendingNotificationsResponse,
    dependencies=[Depends(get_api_key)],
    summary="Get pending status notifications for a user",
)
async def get_pending_notifications(
    telegram_id: int = Query(..., description="User's Telegram ID"),
    db: AsyncSession = Depends(get_db),
) -> PendingNotificationsResponse:
    """
    Returns orders whose status changed but the user has not been notified yet.

    The bot calls this when a user starts a conversation to show missed updates.
    """
    try:
        # Find user by telegram_id
        user_result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return PendingNotificationsResponse(notifications=[])

        # Find orders with undelivered notifications
        # notified_status IS NULL or notified_status != status
        # Exclude 'pending' — user already knows about it from order creation
        result = await db.execute(
            select(Order, Service.name.label("service_name"))
            .outerjoin(Service, Order.service_id == Service.id)
            .where(
                Order.user_id == user.id,
                Order.status != "pending",
                or_(
                    Order.notified_status.is_(None),
                    Order.notified_status != Order.status,
                ),
            )
            .order_by(Order.updated_at.asc())
        )
        rows = result.all()

        notifications = []
        for order, svc_name in rows:
            notifications.append(
                PendingNotification(
                    order_id=order.id,
                    service_name=svc_name,
                    total_amount=order.total_amount,
                    status=order.status,
                    notified_status=order.notified_status,
                    updated_at=order.updated_at,
                )
            )

        return PendingNotificationsResponse(notifications=notifications)
    except Exception as e:
        log.error("Error fetching pending notifications: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications",
        ) from e


@router.post(
    "/notifications/ack",
    dependencies=[Depends(get_api_key)],
    summary="Acknowledge delivered notifications",
)
async def ack_notifications(
    request: AckRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Mark notifications as delivered: sets notified_status = status for given orders.

    The bot calls this after it has shown the notification messages to the user.
    """
    try:
        # Find user
        user_result = await db.execute(
            select(User).where(User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Update notified_status for matching orders
        result = await db.execute(
            select(Order).where(
                Order.user_id == user.id,
                Order.id.in_(request.order_ids),
            )
        )
        orders = result.scalars().all()

        updated = 0
        for order in orders:
            if order.notified_status != order.status:
                order.notified_status = order.status
                updated += 1

        if updated:
            await db.commit()

        return {"status": "ok", "acknowledged": updated}
    except HTTPException:
        raise
    except Exception as e:
        log.error("Error acknowledging notifications: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge notifications",
        ) from e
