"""User-related API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from nms.models import UserRegistrationRequest, RegistrationResponse
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
        request: User registration data
        db: Database session

    Returns:
        Registration response with user ID
    """
    user_id = await auth_service.register_user(request.phone_number, db)

    return RegistrationResponse(
        status="ok", message="User registered successfully", user_id=user_id
    )
