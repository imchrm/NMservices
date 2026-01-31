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

        Priority: phone_number is the primary identifier.
        - If user with this phone exists — update telegram_id/language_code if needed
        - If user with this telegram_id exists (but different phone) — clear old telegram_id,
          then create/update user with new phone
        - Otherwise — create new user

        Args:
            phone: User's phone number
            db: Database session
            telegram_id: User's Telegram ID (optional)
            language_code: User's preferred language code (optional)

        Returns:
            User ID from database
        """
        # 1. Check if user exists by phone (primary identifier)
        result = await db.execute(select(User).where(User.phone_number == phone))
        user_by_phone = result.scalar_one_or_none()

        # 2. Check if telegram_id is already used by another user
        user_by_telegram = None
        if telegram_id:
            result = await db.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user_by_telegram = result.scalar_one_or_none()

        # 3. If telegram_id belongs to a different user — clear it (user changed phone)
        if user_by_telegram and user_by_phone and user_by_telegram.id != user_by_phone.id:
            print(f"[DB] Clearing telegram_id {telegram_id} from user ID {user_by_telegram.id} (phone changed)")
            user_by_telegram.telegram_id = None
            await db.flush()
        elif user_by_telegram and not user_by_phone:
            # telegram_id exists but phone is new — clear old telegram_id
            print(f"[DB] Clearing telegram_id {telegram_id} from user ID {user_by_telegram.id} (new phone)")
            user_by_telegram.telegram_id = None
            await db.flush()

        # 4. User with this phone exists — update fields if needed
        if user_by_phone:
            updated = False
            if telegram_id and user_by_phone.telegram_id != telegram_id:
                user_by_phone.telegram_id = telegram_id
                updated = True
            if language_code and user_by_phone.language_code != language_code:
                user_by_phone.language_code = language_code
                updated = True
            if updated:
                await db.commit()
                print(f"[DB] User {phone} updated: telegram_id={telegram_id}, language_code={language_code}")
            else:
                print(f"[DB] User {phone} already exists with ID {user_by_phone.id}")
            return user_by_phone.id

        # 5. Create new user
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
