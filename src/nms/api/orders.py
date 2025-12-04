"""Order-related API endpoints."""

from fastapi import APIRouter, Depends
from ..models import OrderCreateRequest, OrderResponse
from ..services.order import OrderService
from .dependencies import get_api_key

router = APIRouter(prefix="/orders", tags=["orders"])
order_service = OrderService()


@router.post(
    "",
    response_model=OrderResponse,
    dependencies=[Depends(get_api_key)],
    summary="Create new order",
)
async def create_order(request: OrderCreateRequest) -> OrderResponse:
    """
    Create a new order with payment processing.

    Args:
        request: Order creation data

    Returns:
        Order response with order ID
    """
    order_id = order_service.create_order(request.user_id, request.tariff_code)

    return OrderResponse(
        status="ok", order_id=order_id, message="Order created and payment processed"
    )
