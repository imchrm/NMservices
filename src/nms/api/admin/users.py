"""Admin API endpoints for user management."""

import logging
from datetime import datetime
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from nms.database import get_db
from nms.models.db_models import User, Order
from nms.models.admin import (
    AdminUserResponse,
    AdminUserWithOrdersResponse,
    AdminUserCreateRequest,
    AdminUserListResponse,
    AdminOrderResponse,
)
from nms.api.dependencies import get_admin_key

log = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/users", tags=["admin-users"])


@router.get("", response_model=AdminUserListResponse, dependencies=[Depends(get_admin_key)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    sort_by: Literal["id", "phone_number", "telegram_id", "language_code", "created_at", "updated_at"] = Query(
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
    q: Optional[str] = Query(
        default=None,
        description="Search by phone number (contains)"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all users with sorting support.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        sort_by: Field to sort by (id, phone_number, created_at, updated_at)
        order: Sort order (asc or desc)
        date_from: Optional start of date range filter (inclusive)
        date_to: Optional end of date range filter (inclusive)
        db: Database session

    Returns:
        List of users with total count
    """
    try:
        # Get total count
        count_query = select(func.count(User.id))
        if date_from is not None:
            count_query = count_query.where(User.created_at >= date_from)
        if date_to is not None:
            count_query = count_query.where(User.created_at <= date_to)
        if q is not None:
            count_query = count_query.where(User.phone_number.contains(q))
        count_result = await db.execute(count_query)
        total = count_result.scalar_one()

        # Map sort_by to actual column
        sort_columns = {
            "id": User.id,
            "phone_number": User.phone_number,
            "telegram_id": User.telegram_id,
            "language_code": User.language_code,
            "created_at": User.created_at,
            "updated_at": User.updated_at,
        }

        sort_column = sort_columns[sort_by]

        # Apply sort order
        if order == "desc":
            order_clause = sort_column.desc()
        else:
            order_clause = sort_column.asc()

        # Get users with sorting and date filtering
        users_query = select(User).order_by(order_clause)
        if date_from is not None:
            users_query = users_query.where(User.created_at >= date_from)
        if date_to is not None:
            users_query = users_query.where(User.created_at <= date_to)
        if q is not None:
            users_query = users_query.where(User.phone_number.contains(q))
        result = await db.execute(
            users_query
            .offset(skip)
            .limit(limit)
        )
        users = result.scalars().all()

        return AdminUserListResponse(
            users=[AdminUserResponse.model_validate(user) for user in users],
            total=total
        )
    except Exception as e:
        log.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        ) from e


@router.post("", response_model=AdminUserResponse, dependencies=[Depends(get_admin_key)])
async def create_user(
    request: AdminUserCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    
    Args:
        request: User creation request
        db: Database session
    
    Returns:
        Created user
    """
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.phone_number == request.phone_number)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with phone number {request.phone_number} already exists"
            )
        
        # Create new user
        new_user = User(
            phone_number=request.phone_number,
            telegram_id=request.telegram_id,
            language_code=request.language_code
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        log.info(f"[ADMIN] User created: ID={new_user.id}, phone={new_user.phone_number}")
        
        return AdminUserResponse.model_validate(new_user)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error creating user: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        ) from e


@router.get("/{user_id}", response_model=AdminUserResponse, dependencies=[Depends(get_admin_key)])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        User details
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return AdminUserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        ) from e


@router.delete("/{user_id}", dependencies=[Depends(get_admin_key)])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user by ID. All user's orders will be deleted as well (CASCADE).
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        Success message
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Count orders before deletion
        orders_result = await db.execute(
            select(func.count(Order.id)).where(Order.user_id == user_id)
        )
        orders_count = orders_result.scalar_one()
        
        # Delete user (orders will be deleted via CASCADE)
        await db.delete(user)
        await db.commit()
        
        log.info(f"[ADMIN] User {user_id} deleted with {orders_count} orders")
        
        return {
            "status": "ok",
            "message": f"User {user_id} deleted",
            "orders_deleted": orders_count
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting user {user_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        ) from e


@router.get("/{user_id}/orders", response_model=list[AdminOrderResponse], dependencies=[Depends(get_admin_key)])
async def get_user_orders(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all orders for a specific user.
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        List of user's orders
    """
    try:
        # Check if user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Get orders
        result = await db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        orders = result.scalars().all()
        
        return [AdminOrderResponse.model_validate(order) for order in orders]
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting orders for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user orders"
        ) from e
