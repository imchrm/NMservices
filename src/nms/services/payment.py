"""Payment management services."""

import logging
import secrets
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from nms.models.db_models import Payment, PaymentStatus, Order, OrderStatus

log = logging.getLogger(__name__)


class PaymentService:
    """Service for payment processing and management."""

    @staticmethod
    def _generate_token() -> str:
        """Generate a unique security token for payment URL."""
        return secrets.token_urlsafe(32)

    @staticmethod
    async def create_payment(
        order_id: int,
        amount: Decimal,
        db: AsyncSession,
        provider: str = "payme_demo",
    ) -> Payment:
        """
        Create a new payment record for an order.

        Args:
            order_id: Order ID to create payment for
            amount: Payment amount
            db: Database session
            provider: Payment provider name

        Returns:
            Created Payment object

        Raises:
            ValueError: If order not found or payment already exists
        """
        # Verify order exists
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")

        # Check if payment already exists for this order
        existing = await db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Payment already exists for order {order_id}")

        token = PaymentService._generate_token()
        payment = Payment(
            order_id=order_id,
            amount=amount,
            status=PaymentStatus.PENDING,
            provider=provider,
            token=token,
        )
        db.add(payment)
        await db.commit()
        await db.refresh(payment)

        log.info(
            "[PAYMENT] Created payment #%s for order #%s (amount: %s, provider: %s)",
            payment.id, order_id, amount, provider,
        )
        return payment

    @staticmethod
    async def get_payment_by_token(token: str, db: AsyncSession) -> Payment | None:
        """Get payment by security token."""
        result = await db.execute(select(Payment).where(Payment.token == token))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_payment_by_order_id(order_id: int, db: AsyncSession) -> Payment | None:
        """Get payment by order ID."""
        result = await db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def process_webhook(
        order_id: int,
        token: str,
        amount: Decimal,
        status: str,
        db: AsyncSession,
    ) -> Payment:
        """
        Process a payment webhook callback.

        Validates the token, updates payment status, and updates order status.

        Args:
            order_id: Order ID
            token: Security token for validation
            amount: Payment amount (for verification)
            status: New payment status (paid/failed)
            db: Database session

        Returns:
            Updated Payment object

        Raises:
            ValueError: If validation fails
        """
        # Find payment by order_id
        result = await db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise ValueError(f"Payment not found for order {order_id}")

        # Validate token
        if payment.token != token:
            raise ValueError("Invalid payment token")

        # Validate amount
        if payment.amount != amount:
            raise ValueError(
                f"Amount mismatch: expected {payment.amount}, got {amount}"
            )

        # Check that payment is still pending
        if payment.status not in (PaymentStatus.PENDING, PaymentStatus.PROCESSING):
            raise ValueError(f"Payment is already in status: {payment.status}")

        # Update payment status
        if status == "paid":
            payment.status = PaymentStatus.PAID
        elif status == "failed":
            payment.status = PaymentStatus.FAILED
        else:
            raise ValueError(f"Invalid payment status: {status}")

        # Update order status based on payment result
        order_result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = order_result.scalar_one_or_none()
        if order:
            if status == "paid":
                order.status = OrderStatus.CONFIRMED
                log.info(
                    "[PAYMENT] Order #%s confirmed after successful payment", order_id
                )
            elif status == "failed":
                order.status = OrderStatus.CANCELLED
                log.info(
                    "[PAYMENT] Order #%s cancelled after failed payment", order_id
                )

        await db.commit()
        await db.refresh(payment)

        log.info(
            "[PAYMENT] Webhook processed: payment #%s, order #%s, status: %s",
            payment.id, order_id, status,
        )
        return payment

    @staticmethod
    async def get_payment_status(payment_id: int, db: AsyncSession) -> Payment | None:
        """Get payment by ID."""
        result = await db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
