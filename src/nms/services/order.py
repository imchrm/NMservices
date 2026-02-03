"""Order management services."""

import logging
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from nms.models.db_models import Order, User, Service

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
    async def get_service(service_id: int, db: AsyncSession) -> Service | None:
        """
        Get service by ID.

        Args:
            service_id: Service ID
            db: Database session

        Returns:
            Service if found and active, None otherwise
        """
        result = await db.execute(
            select(Service).where(Service.id == service_id, Service.is_active == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def save_order(
        user_id: int,
        service_id: int,
        amount: Decimal,
        db: AsyncSession,
        address_text: str | None = None,
        scheduled_at: datetime | None = None,
        notes: str | None = None,
    ) -> int:
        """
        Save order to database.

        Args:
            user_id: ID of user creating order
            service_id: ID of selected service
            amount: Order amount (copied from service base_price)
            db: Database session
            address_text: Address for service delivery
            scheduled_at: Scheduled time for service
            notes: Additional notes

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
            service_id=service_id,
            status="pending",
            total_amount=amount,
            address_text=address_text,
            scheduled_at=scheduled_at,
            notes=notes,
        )
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        log.info(
            f"[DB] Order #{new_order.id} created for User {user_id} "
            f"(Service: {service_id}, Amount: {amount})"
        )
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
        service_id: int,
        db: AsyncSession,
        address_text: str | None = None,
        scheduled_at: datetime | None = None,
        notes: str | None = None,
    ) -> int:
        """
        Create new order with payment processing.

        Args:
            user_id: ID of user creating order
            service_id: ID of selected service
            db: Database session
            address_text: Address for service delivery
            scheduled_at: Scheduled time for service
            notes: Additional notes

        Returns:
            Created order ID

        Raises:
            ValueError: If user doesn't exist, service not found, or payment fails
        """
        # Get service and validate
        service = await self.get_service(service_id, db)
        if not service:
            log.error(f"Service with ID {service_id} not found or inactive")
            raise ValueError(f"Service with ID {service_id} not found or inactive")

        # Get amount from service (Variant C - copy price)
        amount = service.base_price or Decimal("0.00")

        # Process payment first
        payment_success = await self.process_payment(amount)
        if not payment_success:
            log.error(f"Payment failed for user {user_id}")
            raise ValueError("Payment processing failed")

        # Save order to database
        order_id = await self.save_order(
            user_id=user_id,
            service_id=service_id,
            amount=amount,
            db=db,
            address_text=address_text,
            scheduled_at=scheduled_at,
            notes=notes,
        )

        # Notify dispatcher
        await self.notify_dispatcher(order_id)

        return order_id
