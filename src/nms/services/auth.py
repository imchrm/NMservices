"""Authentication and user registration services."""

import random


class AuthService:
    """Service for user authentication and registration."""

    @staticmethod
    def send_sms(phone: str) -> bool:
        """
        Send SMS verification code to phone number.

        Args:
            phone: Phone number to send SMS to

        Returns:
            True if SMS sent successfully
        """
        print(f"[STUB-SMS] Sending code to {phone}...")
        return True

    @staticmethod
    def save_user(phone: str) -> int:
        """
        Save user to database.

        Args:
            phone: User's phone number

        Returns:
            Generated user ID
        """
        fake_id = random.randint(1000, 9999)
        print(f"[STUB-DB] User {phone} saved with ID {fake_id}")
        return fake_id

    def register_user(self, phone: str) -> int:
        """
        Register new user with phone verification.

        Args:
            phone: User's phone number

        Returns:
            Created user ID
        """
        self.send_sms(phone)
        user_id = self.save_user(phone)
        return user_id
