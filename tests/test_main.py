"""Tests for NMservices API endpoints."""

import pytest
from fastapi.testclient import TestClient


# --- 1. Тест доступности сервера (Public) ---
def test_read_root(client: TestClient):
    """Test root endpoint availability."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "NoMus API is running"}


# --- 2. Тесты безопасности (Security) ---


def test_register_no_auth(client: TestClient):
    """Попытка запроса без заголовка X-API-Key"""
    response = client.post("/users/register", json={"phone_number": "+998900000000"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}


def test_register_wrong_auth(client: TestClient, wrong_api_key: str):
    """Попытка запроса с неверным ключом"""
    headers = {"X-API-Key": wrong_api_key}
    response = client.post(
        "/users/register", json={"phone_number": "+998900000000"}, headers=headers
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}


def test_create_order_no_auth(client: TestClient):
    """Попытка создания заказа без заголовка X-API-Key"""
    response = client.post("/create_order", json={"user_id": 1, "tariff_code": "standard_300"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}


# --- 3. Тесты функционала (Happy Path & Validation) ---


def test_register_success(client: TestClient, valid_api_key: str):
    """Успешная регистрация"""
    headers = {"X-API-Key": valid_api_key}
    payload = {"phone_number": "+998901112233"}

    response = client.post("/users/register", json=payload, headers=headers)

    # Проверяем статус
    assert response.status_code == 200
    # Проверяем структуру ответа
    data = response.json()
    assert data["status"] == "ok"
    assert "user_id" in data
    assert isinstance(data["user_id"], int)


def test_register_validation_error(client: TestClient, valid_api_key: str):
    """Ошибка валидации данных (не передали phone_number)"""
    headers = {"X-API-Key": valid_api_key}
    payload = {}  # Пустой JSON

    response = client.post("/register", json=payload, headers=headers)

    assert response.status_code == 422  # Стандартный код ошибки валидации в FastAPI


def test_create_order_success(client: TestClient, valid_api_key: str, test_user: int):
    """Успешное создание заказа с реальным пользователем"""
    headers = {"X-API-Key": valid_api_key}
    payload = {"user_id": test_user, "tariff_code": "standard_300"}

    response = client.post("/create_order", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["order_id"] > 0
    assert isinstance(data["order_id"], int)


def test_create_order_nonexistent_user(client: TestClient, valid_api_key: str):
    """Создание заказа для несуществующего пользователя"""
    headers = {"X-API-Key": valid_api_key}
    payload = {"user_id": 99999, "tariff_code": "standard_300"}

    response = client.post("/create_order", json=payload, headers=headers)

    assert response.status_code == 400
    data = response.json()
    assert "User with ID 99999 does not exist" in data["detail"]


def test_create_order_validation_error(client: TestClient, valid_api_key: str):
    """Ошибка валидации данных (не передали обязательные поля)"""
    headers = {"X-API-Key": valid_api_key}
    payload = {}  # Пустой JSON

    response = client.post("/create_order", json=payload, headers=headers)

    assert response.status_code == 422  # Стандартный код ошибки валидации в FastAPI


# --- 4. Тесты нового роутера /orders ---


def test_orders_endpoint_success(client: TestClient, valid_api_key: str, test_user: int):
    """Успешное создание заказа через новый эндпоинт /orders"""
    headers = {"X-API-Key": valid_api_key}
    payload = {"user_id": test_user, "tariff_code": "premium_500"}

    response = client.post("/orders", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["order_id"] > 0
    assert isinstance(data["order_id"], int)


def test_orders_endpoint_nonexistent_user(client: TestClient, valid_api_key: str):
    """Создание заказа через /orders для несуществующего пользователя"""
    headers = {"X-API-Key": valid_api_key}
    payload = {"user_id": 88888, "tariff_code": "premium_500"}

    response = client.post("/orders", json=payload, headers=headers)

    assert response.status_code == 400
    data = response.json()
    assert "User with ID 88888 does not exist" in data["detail"]
