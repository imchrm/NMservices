import random
import time
from fastapi import FastAPI, Depends, Security, HTTPException, status
from .models import (
    UserRegistrationRequest,
    RegistrationResponse,
    OrderCreateRequest,
    OrderResponse,
)
import os
from dotenv import load_dotenv
from fastapi.security.api_key import APIKeyHeader

load_dotenv()

# Получаем ключ из .env (или используем дефолтный для теста)
API_TOKEN = os.getenv("API_SECRET_KEY", "test_secret")
API_KEY_NAME = "X-API-Key"

# Получаем ключ из .env (или используем дефолтный для теста)
API_TOKEN = os.getenv("API_SECRET_KEY", "test_secret")
API_KEY_NAME = "X-API-Key"

# Определяем схему безопасности: ожидаем заголовок X-API-Key
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(title="NoMus Backend API (PoC)")


# --- Функция проверки ключа ---
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_TOKEN:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


# --- MOCKS / STUBS (Заглушки) ---


def mock_sms_service(phone: str):
    """Simulating sending SMS"""
    print(f"[STUB-SMS] Sending code to {phone}...")
    return True


def mock_payment_service(amount: int):
    """Payment simulation"""
    print(f"[STUB-PAYMENT] Processing payment of {amount} sum...")
    time.sleep(1)  # Simulate network delay
    return True


def mock_db_save_user(phone: str):
    """Simulating saving a user to the database"""
    fake_id = random.randint(1000, 9999)
    print(f"[STUB-DB] User {phone} saved with ID {fake_id}")
    return fake_id


def mock_db_save_order(user_id: int, tariff: str):
    """Simulating order saving"""
    fake_order_id = random.randint(100, 999)
    print(
        f"[STUB-DB] Order #{fake_order_id} created for User {user_id} (Tariff: {tariff})"
    )
    print(f"[STUB-NOTIFY] Dispatcher notified about Order #{fake_order_id}")
    return fake_order_id


# --- ENDPOINTS (Точки входа для Бота) ---


@app.get("/")
async def root():
    return {"message": "NoMus API is running"}


@app.post(
    "/register",
    response_model=RegistrationResponse,
    dependencies=[Depends(get_api_key)],
)
async def register_user(request: UserRegistrationRequest):
    # 1. Логика заглушки SMS (хоть по сценарию бот сам проверяет код,
    # но регистрация факта подтвержденного номера происходит здесь)
    mock_sms_service(request.phone_number)

    # 2. Логика заглушки БД
    user_id = mock_db_save_user(request.phone_number)

    return RegistrationResponse(
        status="ok", message="User registered successfully", user_id=user_id
    )


@app.post(
    "/create_order", response_model=OrderResponse, dependencies=[Depends(get_api_key)]
)
async def create_order(request: OrderCreateRequest):
    # 1. Логика заглушки оплаты
    # Допустим, тариф 'standard' стоит 30000 сум
    mock_payment_service(30000)

    # 2. Логика заглушки БД и Уведомлений
    order_id = mock_db_save_order(request.user_id, request.tariff_code)

    return OrderResponse(
        status="ok", order_id=order_id, message="Order created and payment processed"
    )


def run():
    import uvicorn

    uvicorn.run("nms.main:app", host="0.0.0.0", port=8000, reload=True)
