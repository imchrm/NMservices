"""User-related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from nms.models import UserRegistrationRequest, RegistrationResponse
from nms.models.user import UserResponse
from nms.services.auth import AuthService
from nms.database import get_db
from nms.api.dependencies import get_api_key

router = APIRouter(prefix="/users", tags=["users"])
auth_service = AuthService()


@router.post(
    "/register",
    response_model=RegistrationResponse,
    dependencies=[Depends(get_api_key)],
    summary="Register new user",
)
async def register_user(
    request: UserRegistrationRequest, db: AsyncSession = Depends(get_db)
) -> RegistrationResponse:
    """
    Register a new user with phone verification.

    Args:
        request: User registration data (phone_number, optional telegram_id)
        db: Database session

    Returns:
        Registration response with user ID
    """
    user_id = await auth_service.register_user(
        request.phone_number, db, request.telegram_id
    )

    return RegistrationResponse(
        status="ok", message="User registered successfully", user_id=user_id
    )


@router.get(
    "/by-telegram/{telegram_id}",
    response_model=UserResponse,
    dependencies=[Depends(get_api_key)],
    summary="Get user by Telegram ID",
)
async def get_user_by_telegram_id(
    telegram_id: int, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Get user by Telegram ID.

    Args:
        telegram_id: User's Telegram ID
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: 404 if user not found
    """
    user = await AuthService.get_user_by_telegram_id(telegram_id, db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.model_validate(user)
