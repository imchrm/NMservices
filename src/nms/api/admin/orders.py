"""Admin API endpoints for order management."""

import logging
from datetime import datetime
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from nms.database import get_db
from nms.models.db_models import User, Order, Service
from nms.models.admin import (
    AdminOrderResponse,
    AdminOrderWithUserResponse,
    AdminOrderCreateRequest,
    AdminOrderUpdateRequest,
    AdminOrderListResponse,
    AdminStatsResponse,
    AdminUserResponse,
)
from nms.api.dependencies import get_admin_key

log = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


@router.get("", response_model=AdminOrderListResponse, dependencies=[Depends(get_admin_key)])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = Query(
        default=None,
        description="Filter by order status (e.g., 'pending', 'completed')"
    ),
    sort_by: Literal["id", "user_id", "status", "total_amount", "address_text", "scheduled_at", "created_at", "updated_at"] = Query(
        default="created_at",
        description="Field to sort by"
    ),
    order: Literal["asc", "desc"] = Query(
        default="desc",
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
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all orders with filtering and sorting support.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Optional status filter (e.g., 'pending', 'completed')
        sort_by: Field to sort by (id, user_id, status, total_amount, created_at, updated_at)
        order: Sort order (asc or desc)
        date_from: Optional start of date range filter (inclusive)
        date_to: Optional end of date range filter (inclusive)
        db: Database session

    Returns:
        List of orders with total count
    """
    try:
        # Map sort_by to actual column
        sort_columns = {
            "id": Order.id,
            "user_id": Order.user_id,
            "status": Order.status,
            "total_amount": Order.total_amount,
            "address_text": Order.address_text,
            "scheduled_at": Order.scheduled_at,
            "created_at": Order.created_at,
            "updated_at": Order.updated_at,
        }

        sort_column = sort_columns[sort_by]

        # Apply sort order
        if order == "desc":
            order_clause = sort_column.desc()
        else:
            order_clause = sort_column.asc()

        # Build query with sorting
        query = select(Order).order_by(order_clause)

        if status_filter:
            query = query.where(Order.status == status_filter)
        if date_from is not None:
            query = query.where(Order.created_at >= date_from)
        if date_to is not None:
            query = query.where(Order.created_at <= date_to)

        # Get total count
        count_query = select(func.count(Order.id))
        if status_filter:
            count_query = count_query.where(Order.status == status_filter)
        if date_from is not None:
            count_query = count_query.where(Order.created_at >= date_from)
        if date_to is not None:
            count_query = count_query.where(Order.created_at <= date_to)

        count_result = await db.execute(count_query)
        total = count_result.scalar_one()

        # Get orders with pagination
        result = await db.execute(query.offset(skip).limit(limit))
        orders = result.scalars().all()

        return AdminOrderListResponse(
            orders=[AdminOrderResponse.model_validate(order) for order in orders],
            total=total
        )
    except Exception as e:
        log.error(f"Error listing orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list orders"
        ) from e


@router.post("", response_model=AdminOrderResponse, dependencies=[Depends(get_admin_key)])
async def create_order(
    request: AdminOrderCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new order.

    Args:
        request: Order creation request
        db: Database session

    Returns:
        Created order
    """
    try:
        # Verify user exists
        user_result = await db.execute(select(User).where(User.id == request.user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID {request.user_id} does not exist"
            )

        # Create new order
        new_order = Order(
            user_id=request.user_id,
            status=request.status,
            total_amount=request.total_amount,
            notes=request.notes
        )
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        log.info(f"[ADMIN] Order created: ID={new_order.id}, user_id={new_order.user_id}")

        return AdminOrderResponse.model_validate(new_order)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error creating order: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        ) from e


@router.get("/{order_id}", response_model=AdminOrderWithUserResponse, dependencies=[Depends(get_admin_key)])
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get order by ID with user details.

    Args:
        order_id: Order ID
        db: Database session

    Returns:
        Order details with user information
    """
    try:
        result = await db.execute(
            select(Order)
            .options(selectinload(Order.user))
            .where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )

        return AdminOrderWithUserResponse(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total_amount,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            user=AdminUserResponse.model_validate(order.user)
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order"
        ) from e


@router.patch("/{order_id}", response_model=AdminOrderResponse, dependencies=[Depends(get_admin_key)])
async def update_order(
    order_id: int,
    request: AdminOrderUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update order by ID.

    Args:
        order_id: Order ID
        request: Order update request
        db: Database session

    Returns:
        Updated order
    """
    try:
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )

        # Update fields if provided
        if request.status is not None:
            order.status = request.status
        if request.total_amount is not None:
            order.total_amount = request.total_amount
        if request.notes is not None:
            order.notes = request.notes

        await db.commit()
        await db.refresh(order)

        log.info(f"[ADMIN] Order {order_id} updated")

        return AdminOrderResponse.model_validate(order)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating order {order_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order"
        ) from e


@router.delete("/{order_id}", dependencies=[Depends(get_admin_key)])
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete order by ID.

    Args:
        order_id: Order ID
        db: Database session

    Returns:
        Success message
    """
    try:
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )

        await db.delete(order)
        await db.commit()

        log.info(f"[ADMIN] Order {order_id} deleted")

        return {
            "status": "ok",
            "message": f"Order {order_id} deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting order {order_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete order"
        ) from e


# Statistics endpoint
stats_router = APIRouter(prefix="/admin", tags=["admin-stats"])


@stats_router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(get_admin_key)])
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Get database statistics.

    Args:
        db: Database session

    Returns:
        Database statistics
    """
    try:
        # Total users
        users_count = await db.execute(select(func.count(User.id)))
        total_users = users_count.scalar_one()

        # Total orders
        orders_count = await db.execute(select(func.count(Order.id)))
        total_orders = orders_count.scalar_one()

        # Total active services
        services_count = await db.execute(
            select(func.count(Service.id)).where(Service.is_active == True)
        )
        total_services = services_count.scalar_one()

        # Orders by status
        status_result = await db.execute(
            select(Order.status, func.count(Order.id))
            .group_by(Order.status)
        )
        orders_by_status = {status: count for status, count in status_result.all()}

        return AdminStatsResponse(
            total_users=total_users,
            total_orders=total_orders,
            total_services=total_services,
            orders_by_status=orders_by_status
        )
    except Exception as e:
        log.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        ) from e
