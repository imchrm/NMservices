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


# --- 5. Тесты telegram_id ---


def test_register_with_telegram_id(client: TestClient, valid_api_key: str):
    """Успешная регистрация с telegram_id"""
    headers = {"X-API-Key": valid_api_key}
    payload = {"phone_number": "+998901112244", "telegram_id": 123456789}

    response = client.post("/users/register", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "user_id" in data
    assert isinstance(data["user_id"], int)


def test_get_user_by_telegram_id_found(
    client: TestClient, valid_api_key: str, test_user_with_telegram: dict
):
    """Поиск пользователя по telegram_id — найден"""
    headers = {"X-API-Key": valid_api_key}
    telegram_id = test_user_with_telegram["telegram_id"]

    response = client.get(f"/users/by-telegram/{telegram_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == telegram_id
    assert data["id"] == test_user_with_telegram["user_id"]
    assert "phone_number" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_user_by_telegram_id_not_found(client: TestClient, valid_api_key: str):
    """Поиск пользователя по telegram_id — не найден (404)"""
    headers = {"X-API-Key": valid_api_key}
    telegram_id = 999999999  # Несуществующий telegram_id

    response = client.get(f"/users/by-telegram/{telegram_id}", headers=headers)

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_register_existing_telegram_id_returns_same_user(
    client: TestClient, valid_api_key: str, test_user_with_telegram: dict
):
    """Повторная регистрация с тем же telegram_id возвращает существующего пользователя"""
    headers = {"X-API-Key": valid_api_key}
    payload = {
        "phone_number": "+998901119999",  # Другой номер
        "telegram_id": test_user_with_telegram["telegram_id"],  # Тот же telegram_id
    }

    response = client.post("/users/register", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    # Должен вернуть ID существующего пользователя
    assert data["user_id"] == test_user_with_telegram["user_id"]


# --- 6. Тесты language_code ---


def test_register_with_language_code(client: TestClient, valid_api_key: str):
    """Успешная регистрация с language_code"""
    headers = {"X-API-Key": valid_api_key}
    payload = {
        "phone_number": "+998901112255",
        "telegram_id": 111222333,
        "language_code": "uz",
    }

    response = client.post("/users/register", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "user_id" in data

    # Проверяем, что язык сохранился
    user_response = client.get(
        f"/users/by-telegram/{payload['telegram_id']}", headers=headers
    )
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data["language_code"] == "uz"


def test_get_user_returns_language_code(
    client: TestClient, valid_api_key: str, test_user_with_telegram: dict
):
    """Получение пользователя возвращает language_code"""
    headers = {"X-API-Key": valid_api_key}
    telegram_id = test_user_with_telegram["telegram_id"]

    response = client.get(f"/users/by-telegram/{telegram_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "language_code" in data


def test_update_language_success(
    client: TestClient, valid_api_key: str, test_user_with_telegram: dict
):
    """Успешное обновление языка пользователя"""
    headers = {"X-API-Key": valid_api_key}
    user_id = test_user_with_telegram["user_id"]

    response = client.patch(
        f"/users/{user_id}/language",
        json={"language_code": "en"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

    # Проверяем, что язык обновился
    telegram_id = test_user_with_telegram["telegram_id"]
    user_response = client.get(f"/users/by-telegram/{telegram_id}", headers=headers)
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data["language_code"] == "en"


def test_update_language_user_not_found(client: TestClient, valid_api_key: str):
    """Обновление языка для несуществующего пользователя"""
    headers = {"X-API-Key": valid_api_key}

    response = client.patch(
        "/users/99999/language",
        json={"language_code": "ru"},
        headers=headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_update_language_no_auth(client: TestClient):
    """Попытка обновления языка без авторизации"""
    response = client.patch("/users/1/language", json={"language_code": "ru"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}
