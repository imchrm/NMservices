"""Main application entry point for NMservices."""
import logging

from fastapi import FastAPI, Depends, HTTPException, status
from nms.config import get_settings
from nms.api.users import router as users_router
from nms.api.orders import router as orders_router
from nms.api.dependencies import get_api_key
from nms.models import (
    UserRegistrationRequest,
    RegistrationResponse,
    OrderCreateRequest,
    OrderResponse,
)
from nms.database import get_db
from nms.services.auth import AuthService
from nms.services.order import OrderService

settings = get_settings()

def _setup_logging() -> logging.Logger:
    log_config = settings.logging
    logging.basicConfig(
        level=getattr(logging, log_config.level),
        format=log_config.format,
    )
    return logging.getLogger(__name__)

log = _setup_logging()

app = FastAPI(title=settings.app_title)

# Include routers
app.include_router(users_router)
app.include_router(orders_router)

# Service instances for legacy endpoints
auth_service = AuthService()
order_service = OrderService()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "NoMus API is running"}


# Backward compatibility endpoints
@app.post(
    "/register",
    response_model=RegistrationResponse,
    dependencies=[Depends(get_api_key)],
    deprecated=True,
)
async def register_user_legacy(
    request: UserRegistrationRequest, db=Depends(get_db)
):
    """Legacy endpoint - use /users/register instead."""
    try:
        user_id = await auth_service.register_user(request.phone_number, db)
        return RegistrationResponse(
            status="ok", message="User registered successfully", user_id=user_id
        )
    except Exception as e:
        # We write the real error in the server logs
        log.error("Error registering user: %s", e) 
        # We send a general message to the user
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error. Please try again later." 
        ) from e


@app.post(
    "/create_order",
    response_model=OrderResponse,
    dependencies=[Depends(get_api_key)],
    deprecated=True,
)
async def create_order_legacy(
    request: OrderCreateRequest, db=Depends(get_db)
):
    """Legacy endpoint - use /orders instead."""
    try:
        order_id = await order_service.create_order(
            request.user_id, request.tariff_code, db
        )
        return OrderResponse(
            status="ok", order_id=order_id, message="Order created and payment processed"
        )
    except ValueError as e:
        log.error("Error creating order: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        log.error("Error creating order: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later."
        ) from e


def run():
    """Run the application with uvicorn."""
    import uvicorn

    uvicorn.run(
        "nms.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
