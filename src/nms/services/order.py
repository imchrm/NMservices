"""Order management services."""

import random
import time


class OrderService:
    """Service for order creation and management."""

    @staticmethod
    def process_payment(amount: int) -> bool:
        """
        Process payment for order.

        Args:
            amount: Payment amount in sum

        Returns:
            True if payment successful
        """
        print(f"[STUB-PAYMENT] Processing payment of {amount} sum...")
        time.sleep(1)  # Simulate network delay
        return True

    @staticmethod
    def save_order(user_id: int, tariff: str) -> int:
        """
        Save order to database.

        Args:
            user_id: ID of user creating order
            tariff: Tariff code

        Returns:
            Generated order ID
        """
        fake_order_id = random.randint(100, 999)
        print(
            f"[STUB-DB] Order #{fake_order_id} created for User {user_id} (Tariff: {tariff})"
        )
        return fake_order_id

    @staticmethod
    def notify_dispatcher(order_id: int) -> None:
        """
        Notify dispatcher about new order.

        Args:
            order_id: ID of created order
        """
        print(f"[STUB-NOTIFY] Dispatcher notified about Order #{order_id}")

    def create_order(self, user_id: int, tariff_code: str, amount: int = 30000) -> int:
        """
        Create new order with payment processing.

        Args:
            user_id: ID of user creating order
            tariff_code: Tariff code for order
            amount: Payment amount (default: 30000 sum)

        Returns:
            Created order ID
        """
        self.process_payment(amount)
        order_id = self.save_order(user_id, tariff_code)
        self.notify_dispatcher(order_id)
        return order_id
