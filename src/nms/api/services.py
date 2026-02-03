"""Service-related API endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from nms.models.service import (
    ServiceResponse,
    ServiceCreateRequest,
    ServiceUpdateRequest,
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
    include_inactive: bool = Query(False, description="Include inactive services (admin)"),
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


@router.post(
    "",
    response_model=ServiceResponse,
    dependencies=[Depends(get_api_key)],
    summary="Create new service (admin)",
    status_code=201,
)
async def create_service(
    request: ServiceCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """
    Create a new service.

    Args:
        request: Service creation data
        db: Database session

    Returns:
        Created service
    """
    service = Service(
        name=request.name,
        description=request.description,
        base_price=request.base_price,
        duration_minutes=request.duration_minutes,
        is_active=request.is_active,
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)

    log.info(f"Created service: {service.id} - {service.name}")
    return ServiceResponse.model_validate(service)


@router.patch(
    "/{service_id}",
    response_model=ServiceResponse,
    dependencies=[Depends(get_api_key)],
    summary="Update service (admin)",
)
async def update_service(
    service_id: int,
    request: ServiceUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """
    Update an existing service.

    Args:
        service_id: Service ID
        request: Service update data
        db: Database session

    Returns:
        Updated service

    Raises:
        HTTPException: 404 if service not found
    """
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)

    await db.commit()
    await db.refresh(service)

    log.info(f"Updated service: {service.id} - {service.name}")
    return ServiceResponse.model_validate(service)


@router.delete(
    "/{service_id}",
    dependencies=[Depends(get_api_key)],
    summary="Deactivate service (admin)",
    status_code=204,
)
async def deactivate_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Deactivate a service (soft delete).

    Args:
        service_id: Service ID
        db: Database session

    Raises:
        HTTPException: 404 if service not found
    """
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.is_active = False
    await db.commit()

    log.info(f"Deactivated service: {service.id} - {service.name}")
