"""Order-related API endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from ..models import OrderCreateRequest, OrderResponse
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
