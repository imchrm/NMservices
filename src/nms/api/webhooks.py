"""Webhook endpoints for payment providers."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.payment import PaymeWebhookPayload
from ..models.db_models import Order, User, Service
from ..services.payment import PaymentService
from ..services.telegram_notifier import TelegramNotifier
from ..database import get_db
from ..config import get_settings

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

    The endpoint validates the token, updates payment and order statuses,
    and sends a Telegram notification to the user.
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

        # Send Telegram notification to user about payment result
        await _notify_payment_result(payload.order_id, db)

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


async def _notify_payment_result(order_id: int, db: AsyncSession) -> None:
    """Send Telegram push notification about payment result."""
    try:
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            return

        user_result = await db.execute(select(User).where(User.id == order.user_id))
        user = user_result.scalar_one_or_none()
        if not user or not user.telegram_id:
            log.info("[WEBHOOK] No telegram_id for user %s, skipping push", order.user_id)
            return

        svc_result = await db.execute(select(Service).where(Service.id == order.service_id))
        service = svc_result.scalar_one_or_none()
        service_name = service.name if service else "—"

        settings = get_settings()
        notifier = TelegramNotifier(settings.telegram_bot_token)
        delivered = await notifier.notify_order_status(
            telegram_id=user.telegram_id,
            order_id=order.id,
            service_name=service_name,
            total_amount=order.total_amount,
            new_status=order.status,
            language_code=user.language_code,
        )

        if delivered:
            order.notified_status = order.status
            await db.commit()
            log.info("[WEBHOOK] Push notification delivered for order #%s", order.id)
        else:
            log.info(
                "[WEBHOOK] Push failed for order #%s, user will be notified on next visit",
                order.id,
            )
    except Exception as e:
        log.error("[WEBHOOK] Notification error for order #%s: %s", order_id, e)
