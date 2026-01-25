"""API dependencies for dependency injection."""

from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from ..config import get_settings

settings = get_settings()

api_key_header = APIKeyHeader(name=settings.api_key_name, auto_error=False)
admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """
    Validate API key from request header.

    Args:
        api_key_header: API key from X-API-Key header

    Returns:
        Validated API key

    Raises:
        HTTPException: If API key is invalid
    """
    if api_key_header == settings.api_secret_key:
        return api_key_header

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )


async def get_admin_key(admin_key_header: str = Security(admin_key_header)) -> str:
    """
    Validate admin API key from request header.

    Args:
        admin_key_header: Admin API key from X-Admin-Key header

    Returns:
        Validated admin API key

    Raises:
        HTTPException: If admin API key is invalid
    """
    if admin_key_header == settings.admin_secret_key:
        return admin_key_header

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate admin credentials",
    )
