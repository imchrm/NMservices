"""Authentication and user registration services."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from nms.models.db_models import User


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
    async def save_user(phone: str, db: AsyncSession) -> int:
        """
        Save user to database.

        Args:
            phone: User's phone number
            db: Database session

        Returns:
            User ID from database
        """
        # Check if user already exists
        result = await db.execute(select(User).where(User.phone_number == phone))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            user_id = existing_user.id
            print(f"[DB] User {phone} already exists with ID {existing_user.id}")
            return user_id

        # Create new user
        new_user = User(phone_number=phone)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        print(f"[DB] User {phone} saved with ID {new_user.id}")
        return new_user.id

    async def register_user(self, phone: str, db: AsyncSession) -> int:
        """
        Register new user with phone verification.

        Args:
            phone: User's phone number
            db: Database session

        Returns:
            Created user ID
        """
        AuthService.send_sms(phone)
        user_id = await AuthService.save_user(phone, db)
        return user_id
