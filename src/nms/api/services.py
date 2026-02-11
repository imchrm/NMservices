"""Service-related API endpoints (read-only, for bot/client access)."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from nms.models.service import (
    ServiceResponse,
    ServiceListResponse,
)
from nms.models.db_models import Service
from nms.database import get_db
from nms.api.dependencies import get_api_key

router = APIRouter(prefix="/services", tags=["services"])
log = logging.getLogger(__name__)


@router.get(
    "",
    response_model=ServiceListResponse,
    dependencies=[Depends(get_api_key)],
    summary="Get list of services",
)
async def get_services(
    include_inactive: bool = Query(False, description="Include inactive services"),
    db: AsyncSession = Depends(get_db),
) -> ServiceListResponse:
    """
    Get list of services.

    Args:
        include_inactive: If True, include inactive services
        db: Database session

    Returns:
        List of services
    """
    query = select(Service)
    if not include_inactive:
        query = query.where(Service.is_active == True)
    query = query.order_by(Service.name)

    result = await db.execute(query)
    services = result.scalars().all()

    return ServiceListResponse(
        services=[ServiceResponse.model_validate(s) for s in services],
        total=len(services),
    )


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    dependencies=[Depends(get_api_key)],
    summary="Get service by ID",
)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """
    Get service details by ID.

    Args:
        service_id: Service ID
        db: Database session

    Returns:
        Service details

    Raises:
        HTTPException: 404 if service not found
    """
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return ServiceResponse.model_validate(service)
