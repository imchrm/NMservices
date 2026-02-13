"""Admin API endpoints for service management."""

import logging
from datetime import datetime
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from nms.database import get_db
from nms.models.db_models import Service
from nms.models.service import (
    ServiceResponse,
    ServiceCreateRequest,
    ServiceUpdateRequest,
    ServiceListResponse,
)
from nms.api.dependencies import get_admin_key

log = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/services", tags=["admin-services"])


@router.get("", response_model=ServiceListResponse, dependencies=[Depends(get_admin_key)])
async def list_services(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = Query(True, description="Include inactive services"),
    sort_by: Literal["id", "name", "base_price", "is_active"] = Query(
        default="id",
        description="Field to sort by"
    ),
    order: Literal["asc", "desc"] = Query(
        default="asc",
        description="Sort order (ascending or descending)"
    ),
    date_from: Optional[datetime] = Query(
        default=None,
        description="Filter by created_at >= date_from (ISO 8601)"
    ),
    date_to: Optional[datetime] = Query(
        default=None,
        description="Filter by created_at <= date_to (ISO 8601)"
    ),
    db: AsyncSession = Depends(get_db),
) -> ServiceListResponse:
    """
    Get list of all services (including inactive by default).

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_inactive: If True, include inactive services (default True for admin)
        sort_by: Field to sort by
        order: Sort order (asc or desc)
        db: Database session

    Returns:
        List of services with total count
    """
    try:
        sort_columns = {
            "id": Service.id,
            "name": Service.name,
            "base_price": Service.base_price,
            "is_active": Service.is_active,
        }

        sort_column = sort_columns[sort_by]

        if order == "desc":
            order_clause = sort_column.desc()
        else:
            order_clause = sort_column.asc()

        query = select(Service).order_by(order_clause)

        if not include_inactive:
            query = query.where(Service.is_active == True)
        if date_from is not None:
            query = query.where(Service.created_at >= date_from)
        if date_to is not None:
            query = query.where(Service.created_at <= date_to)

        count_query = select(func.count(Service.id))
        if not include_inactive:
            count_query = count_query.where(Service.is_active == True)
        if date_from is not None:
            count_query = count_query.where(Service.created_at >= date_from)
        if date_to is not None:
            count_query = count_query.where(Service.created_at <= date_to)

        count_result = await db.execute(count_query)
        total = count_result.scalar_one()

        result = await db.execute(query.offset(skip).limit(limit))
        services = result.scalars().all()

        return ServiceListResponse(
            services=[ServiceResponse.model_validate(s) for s in services],
            total=total,
        )
    except Exception as e:
        log.error(f"Error listing services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list services"
        ) from e


@router.get("/{service_id}", response_model=ServiceResponse, dependencies=[Depends(get_admin_key)])
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """
    Get service by ID (admin view, includes inactive services).

    Args:
        service_id: Service ID
        db: Database session

    Returns:
        Service details
    """
    try:
        result = await db.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID {service_id} not found"
            )

        return ServiceResponse.model_validate(service)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting service {service_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service"
        ) from e


@router.post("", response_model=ServiceResponse, dependencies=[Depends(get_admin_key)], status_code=201)
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
    try:
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

        log.info(f"[ADMIN] Created service: {service.id} - {service.name}")
        return ServiceResponse.model_validate(service)
    except Exception as e:
        log.error(f"Error creating service: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create service"
        ) from e


@router.patch("/{service_id}", response_model=ServiceResponse, dependencies=[Depends(get_admin_key)])
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
    """
    try:
        result = await db.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID {service_id} not found"
            )

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service, field, value)

        await db.commit()
        await db.refresh(service)

        log.info(f"[ADMIN] Updated service: {service.id} - {service.name}")
        return ServiceResponse.model_validate(service)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating service {service_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update service"
        ) from e


@router.delete("/{service_id}", dependencies=[Depends(get_admin_key)], status_code=204)
async def deactivate_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Deactivate a service (soft delete).

    Args:
        service_id: Service ID
        db: Database session
    """
    try:
        result = await db.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID {service_id} not found"
            )

        service.is_active = False
        await db.commit()

        log.info(f"[ADMIN] Deactivated service: {service.id} - {service.name}")
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deactivating service {service_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate service"
        ) from e
