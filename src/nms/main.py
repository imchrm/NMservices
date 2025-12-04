"""Main application entry point for NMservices."""

from fastapi import FastAPI, Depends
from .config import get_settings
from .api.users import router as users_router
from .api.orders import router as orders_router
from .api.dependencies import get_api_key
from .models import (
    UserRegistrationRequest,
    RegistrationResponse,
    OrderCreateRequest,
    OrderResponse,
)
from .services.auth import AuthService
from .services.order import OrderService

settings = get_settings()

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
async def register_user_legacy(request: UserRegistrationRequest):
    """Legacy endpoint - use /users/register instead."""
    user_id = auth_service.register_user(request.phone_number)
    return RegistrationResponse(
        status="ok", message="User registered successfully", user_id=user_id
    )


@app.post(
    "/create_order",
    response_model=OrderResponse,
    dependencies=[Depends(get_api_key)],
    deprecated=True,
)
async def create_order_legacy(request: OrderCreateRequest):
    """Legacy endpoint - use /orders instead."""
    order_id = order_service.create_order(request.user_id, request.tariff_code)
    return OrderResponse(
        status="ok", order_id=order_id, message="Order created and payment processed"
    )


def run():
    """Run the application with uvicorn."""
    import uvicorn

    uvicorn.run(
        "nms.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
