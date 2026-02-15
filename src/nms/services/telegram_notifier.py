"""Telegram notification service for sending order status updates to users."""

import logging
from decimal import Decimal

import httpx

log = logging.getLogger(__name__)

# Localized status notification templates: {language: {status: template}}
_STATUS_TEMPLATES: dict[str, dict[str, str]] = {
    "ru": {
        "confirmed": (
            "Заказ #{order_id} подтверждён.\n"
            "Услуга: {service_name}\n"
            "Стоимость: {amount} сум\n"
            "Мастер скоро свяжется с вами."
        ),
        "in_progress": (
            "Заказ #{order_id}: мастер в пути.\n"
            "Услуга: {service_name}\n"
            "Стоимость: {amount} сум"
        ),
        "completed": (
            "Заказ #{order_id} выполнен!\n"
            "Услуга: {service_name}\n"
            "Стоимость: {amount} сум\n"
            "Спасибо за использование NoMus!"
        ),
        "cancelled": (
            "Заказ #{order_id} отменён.\n"
            "Услуга: {service_name}\n"
            "Стоимость: {amount} сум"
        ),
    },
    "en": {
        "confirmed": (
            "Order #{order_id} confirmed.\n"
            "Service: {service_name}\n"
            "Price: {amount} sum\n"
            "The specialist will contact you shortly."
        ),
        "in_progress": (
            "Order #{order_id}: specialist is on the way.\n"
            "Service: {service_name}\n"
            "Price: {amount} sum"
        ),
        "completed": (
            "Order #{order_id} completed!\n"
            "Service: {service_name}\n"
            "Price: {amount} sum\n"
            "Thank you for using NoMus!"
        ),
        "cancelled": (
            "Order #{order_id} cancelled.\n"
            "Service: {service_name}\n"
            "Price: {amount} sum"
        ),
    },
    "uz": {
        "confirmed": (
            "Buyurtma #{order_id} tasdiqlandi.\n"
            "Xizmat: {service_name}\n"
            "Narxi: {amount} so'm\n"
            "Usta tez orada siz bilan bog'lanadi."
        ),
        "in_progress": (
            "Buyurtma #{order_id}: usta yo'lda.\n"
            "Xizmat: {service_name}\n"
            "Narxi: {amount} so'm"
        ),
        "completed": (
            "Buyurtma #{order_id} bajarildi!\n"
            "Xizmat: {service_name}\n"
            "Narxi: {amount} so'm\n"
            "NoMus dan foydalanganingiz uchun rahmat!"
        ),
        "cancelled": (
            "Buyurtma #{order_id} bekor qilindi.\n"
            "Xizmat: {service_name}\n"
            "Narxi: {amount} so'm"
        ),
    },
}


def format_price(raw: Decimal | str | None) -> str:
    """Format price: 150000.00 → '150 000'."""
    if raw is None:
        return "—"
    try:
        value = int(Decimal(str(raw)))
        return f"{value:,}".replace(",", " ")
    except Exception:
        return str(raw)


class TelegramNotifier:
    """Sends order status notifications to Telegram users via Bot API."""

    def __init__(self, bot_token: str) -> None:
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token)

    async def send_message(self, chat_id: int, text: str) -> bool:
        """Send a plain text message via Telegram Bot API."""
        if not self.is_configured:
            log.warning("[TG-NOTIFY] Bot token not configured, skipping notification")
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.api_url}/sendMessage",
                    json={"chat_id": chat_id, "text": text},
                )
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return True
            log.warning(
                "[TG-NOTIFY] API error for chat_id=%s: %s %s",
                chat_id,
                response.status_code,
                response.text[:200],
            )
            return False
        except Exception as e:
            log.error("[TG-NOTIFY] Failed to send message to chat_id=%s: %s", chat_id, e)
            return False

    async def notify_order_status(
        self,
        telegram_id: int,
        order_id: int,
        service_name: str,
        total_amount: Decimal | str | None,
        new_status: str,
        language_code: str | None = None,
    ) -> bool:
        """
        Send an order status notification to a Telegram user.

        Returns True if the message was delivered, False otherwise.
        """
        lang = language_code or "ru"
        templates = _STATUS_TEMPLATES.get(lang, _STATUS_TEMPLATES["ru"])
        template = templates.get(new_status)

        if not template:
            log.info(
                "[TG-NOTIFY] No template for status '%s', skipping notification for order #%s",
                new_status,
                order_id,
            )
            return False

        text = template.format(
            order_id=order_id,
            service_name=service_name or "—",
            amount=format_price(total_amount),
        )

        delivered = await self.send_message(telegram_id, text)
        if delivered:
            log.info(
                "[TG-NOTIFY] Notification sent: order #%s → telegram_id=%s (status=%s)",
                order_id,
                telegram_id,
                new_status,
            )
        return delivered
