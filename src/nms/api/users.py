"""User-related API endpoints."""

from fastapi import APIRouter, Depends
from ..models import UserRegistrationRequest, RegistrationResponse
from ..services.auth import AuthService
from .dependencies import get_api_key

router = APIRouter(prefix="/users", tags=["users"])
auth_service = AuthService()


@router.post(
    "/register",
    response_model=RegistrationResponse,
    dependencies=[Depends(get_api_key)],
    summary="Register new user",
)
async def register_user(request: UserRegistrationRequest) -> RegistrationResponse:
    """
    Register a new user with phone verification.

    Args:
        request: User registration data

    Returns:
        Registration response with user ID
    """
    user_id = auth_service.register_user(request.phone_number)

    return RegistrationResponse(
        status="ok", message="User registered successfully", user_id=user_id
    )
