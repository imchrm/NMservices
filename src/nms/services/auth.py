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
    async def save_user(
        phone: str,
        db: AsyncSession,
        telegram_id: int | None = None,
        language_code: str | None = None,
    ) -> int:
        """
        Save user to database.

        Args:
            phone: User's phone number
            db: Database session
            telegram_id: User's Telegram ID (optional)
            language_code: User's preferred language code (optional)

        Returns:
            User ID from database
        """
        # Check if user already exists by telegram_id
        if telegram_id:
            result = await db.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            existing_user = result.scalar_one_or_none()
            if existing_user:
                # Update language_code if provided
                if language_code:
                    existing_user.language_code = language_code
                    await db.commit()
                print(f"[DB] User with telegram_id {telegram_id} already exists with ID {existing_user.id}")
                return existing_user.id

        # Check if user already exists by phone
        result = await db.execute(select(User).where(User.phone_number == phone))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Update telegram_id if not set
            if telegram_id and not existing_user.telegram_id:
                existing_user.telegram_id = telegram_id
            # Update language_code if provided
            if language_code:
                existing_user.language_code = language_code
            if telegram_id or language_code:
                await db.commit()
                print(f"[DB] User {phone} updated with telegram_id={telegram_id}, language_code={language_code}")
            print(f"[DB] User {phone} already exists with ID {existing_user.id}")
            return existing_user.id

        # Create new user
        new_user = User(phone_number=phone, telegram_id=telegram_id, language_code=language_code)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        print(f"[DB] User {phone} saved with ID {new_user.id}, telegram_id={telegram_id}, language_code={language_code}")
        return new_user.id

    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int, db: AsyncSession) -> User | None:
        """
        Get user by Telegram ID.

        Args:
            telegram_id: User's Telegram ID
            db: Database session

        Returns:
            User object or None if not found
        """
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def register_user(
        self,
        phone: str,
        db: AsyncSession,
        telegram_id: int | None = None,
        language_code: str | None = None,
    ) -> int:
        """
        Register new user with phone verification.

        Args:
            phone: User's phone number
            db: Database session
            telegram_id: User's Telegram ID (optional)
            language_code: User's preferred language code (optional)

        Returns:
            Created user ID
        """
        AuthService.send_sms(phone)
        user_id = await AuthService.save_user(phone, db, telegram_id, language_code)
        return user_id

    @staticmethod
    async def update_user_language(
        user_id: int, language_code: str, db: AsyncSession
    ) -> bool:
        """
        Update user's language code.

        Args:
            user_id: User ID
            language_code: New language code
            db: Database session

        Returns:
            True if updated successfully, False if user not found
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.language_code = language_code
        await db.commit()
        print(f"[DB] User {user_id} language updated to {language_code}")
        return True
