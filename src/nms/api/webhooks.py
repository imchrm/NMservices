"""Webhook endpoints for payment providers."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.payment import PaymeWebhookPayload
from ..services.payment import PaymentService
from ..database import get_db

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
payment_service = PaymentService()
log = logging.getLogger(__name__)


@router.post(
    "/payme",
    summary="Payme payment webhook (demo emulation)",
)
async def payme_webhook(
    payload: PaymeWebhookPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Handle Payme payment webhook callback.

    In demo mode: called by the checkout page when user clicks "Pay".
    In production: called by real Payme service after payment is processed.

    The endpoint validates the token, updates payment and order statuses.
    No API key required — webhook endpoints use token-based validation.
    """
    try:
        payment = await payment_service.process_webhook(
            order_id=payload.order_id,
            token=payload.token,
            amount=payload.amount,
            status=payload.status,
            db=db,
        )
        return {
            "status": "ok",
            "payment_id": payment.id,
            "payment_status": payment.status,
        }
    except ValueError as e:
        log.error("Webhook validation error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        log.error("Webhook processing error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e
