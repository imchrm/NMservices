"""Order management services."""

import logging
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from nms.models.db_models import Order, User

log = logging.getLogger(__name__)


class OrderService:
    """Service for order creation and management."""

    @staticmethod
    async def process_payment(amount: Decimal) -> bool:
        """
        Process payment for order.

        Args:
            amount: Payment amount in sum

        Returns:
            True if payment successful

        Note:
            Currently a stub implementation. In production, this would
            integrate with a payment gateway (e.g., Payme, Click, Uzcard).
        """
        log.info(f"[PAYMENT-STUB] Processing payment of {amount} sum...")
        # TODO: Integrate with real payment gateway
        return True

    @staticmethod
    async def save_order(
        user_id: int,
        tariff: str,
        amount: Decimal,
        db: AsyncSession
    ) -> int:
        """
        Save order to database.

        Args:
            user_id: ID of user creating order
            tariff: Tariff code
            amount: Order amount
            db: Database session

        Returns:
            Created order ID

        Raises:
            ValueError: If user doesn't exist
        """
        # Verify user exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            log.error(f"User with ID {user_id} not found")
            raise ValueError(f"User with ID {user_id} does not exist")

        # Create new order
        new_order = Order(
            user_id=user_id,
            status="pending",
            total_amount=amount,
            notes=f"Tariff: {tariff}"
        )
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        log.info(f"[DB] Order #{new_order.id} created for User {user_id} (Tariff: {tariff}, Amount: {amount})")
        return new_order.id

    @staticmethod
    async def notify_dispatcher(order_id: int) -> None:
        """
        Notify dispatcher about new order.

        Args:
            order_id: ID of created order

        Note:
            Currently a stub implementation. In production, this would
            send notifications via Telegram, SMS, or push notifications.
        """
        log.info(f"[NOTIFY-STUB] Dispatcher notified about Order #{order_id}")
        # TODO: Implement real notification system (Telegram bot, SMS, etc.)

    async def create_order(
        self,
        user_id: int,
        tariff_code: str,
        db: AsyncSession,
        amount: Decimal = Decimal("30000.00")
    ) -> int:
        """
        Create new order with payment processing.

        Args:
            user_id: ID of user creating order
            tariff_code: Tariff code for order
            db: Database session
            amount: Payment amount (default: 30000.00 sum)

        Returns:
            Created order ID

        Raises:
            ValueError: If user doesn't exist or payment fails
        """
        # Process payment first
        payment_success = await self.process_payment(amount)
        if not payment_success:
            log.error(f"Payment failed for user {user_id}")
            raise ValueError("Payment processing failed")

        # Save order to database
        order_id = await self.save_order(user_id, tariff_code, amount, db)

        # Notify dispatcher
        await self.notify_dispatcher(order_id)

        return order_id
