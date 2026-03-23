"""Payment-related API endpoints."""

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.payment import PaymentInitiateRequest, PaymentInitiateResponse, PaymentStatusResponse
from ..models.db_models import Order, Payment
from ..services.payment import PaymentService
from ..database import get_db
from ..config import get_settings
from .dependencies import get_api_key

router = APIRouter(prefix="/payment", tags=["payment"])
payment_service = PaymentService()
log = logging.getLogger(__name__)

# Templates directory
templates_dir = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

settings = get_settings()


@router.post(
    "/initiate",
    response_model=PaymentInitiateResponse,
    dependencies=[Depends(get_api_key)],
    summary="Initiate payment for an order",
)
async def initiate_payment(
    request: PaymentInitiateRequest,
    db: AsyncSession = Depends(get_db),
) -> PaymentInitiateResponse:
    """
    Create a payment record and return a checkout URL.

    The bot calls this after creating an order to get a payment link
    that will be shown to the user as an inline button.
    """
    try:
        from sqlalchemy import select

        # Get the order to find amount
        result = await db.execute(
            select(Order).where(Order.id == request.order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {request.order_id} not found",
            )

        amount = order.total_amount
        if not amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has no amount set",
            )

        payment = await payment_service.create_payment(
            order_id=request.order_id,
            amount=amount,
            db=db,
        )

        # Build checkout URL
        base_url = settings.payment_base_url.rstrip("/")
        payment_url = f"{base_url}/payment/checkout/{payment.id}?token={payment.token}"

        return PaymentInitiateResponse(
            status="ok",
            payment_id=payment.id,
            payment_url=payment_url,
        )
    except ValueError as e:
        log.error("Error initiating payment: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        log.error("Error initiating payment: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@router.get(
    "/checkout/{payment_id}",
    response_class=HTMLResponse,
    summary="Payment checkout page (demo emulation)",
)
async def checkout_page(
    request: Request,
    payment_id: int,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Render the payment checkout demo page.

    This page emulates a Payme/Click payment form. The user clicks
    "Pay" and the page sends a webhook to confirm the payment.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    # Find payment and validate token
    result = await db.execute(
        select(Payment)
        .options(selectinload(Payment.order))
        .where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment or payment.token != token:
        return HTMLResponse(
            content="<h1>Payment not found</h1><p>Invalid or expired payment link.</p>",
            status_code=404,
        )

    if payment.status != "pending":
        already_status = payment.status
        return templates.TemplateResponse(
            request=request,
            name="checkout.html",
            context={
                "payment_id": payment.id,
                "order_id": payment.order_id,
                "amount": int(payment.amount),
                "amount_formatted": f"{int(payment.amount):,}".replace(",", " "),
                "token": payment.token,
                "already_paid": True,
                "payment_status": already_status,
                "service_name": "",
                "webhook_url": "",
                "bot_username": settings.telegram_bot_username,
            },
        )

    # Get service name via order
    service_name = ""
    if payment.order and payment.order.service_id:
        from ..models.db_models import Service
        svc_result = await db.execute(
            select(Service).where(Service.id == payment.order.service_id)
        )
        service = svc_result.scalar_one_or_none()
        if service:
            service_name = service.name

    base_url = settings.payment_base_url.rstrip("/")
    webhook_url = f"{base_url}/webhooks/payme"

    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "amount": int(payment.amount),
            "amount_formatted": f"{int(payment.amount):,}".replace(",", " "),
            "token": payment.token,
            "already_paid": False,
            "payment_status": payment.status,
            "service_name": service_name,
            "webhook_url": webhook_url,
            "bot_username": settings.telegram_bot_username,
        },
    )


@router.get(
    "/status/{payment_id}",
    response_model=PaymentStatusResponse,
    dependencies=[Depends(get_api_key)],
    summary="Check payment status",
)
async def get_payment_status(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
) -> PaymentStatusResponse:
    """Get current payment status by payment ID."""
    payment = await payment_service.get_payment_status(payment_id, db)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found",
        )

    return PaymentStatusResponse(
        payment_id=payment.id,
        order_id=payment.order_id,
        amount=payment.amount,
        status=payment.status,
        provider=payment.provider,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )
