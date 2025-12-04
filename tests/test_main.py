from fastapi.testclient import TestClient
from nms.main import app
from nms.config import get_settings

settings = get_settings()

# Создаем тестового клиента. Он делает вид, что отправляет запросы по сети,
# но на самом деле вызывает функции вашего приложения напрямую (это очень быстро).
client = TestClient(app)

# Правильный ключ (тот, который у вас в коде по умолчанию или в .env)
VALID_API_KEY = settings.api_secret_key
WRONG_API_KEY = "wrong_password"


# --- 1. Тест доступности сервера (Public) ---
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "NoMus API is running"}


# --- 2. Тесты безопасности (Security) ---


def test_register_no_auth():
    """Попытка запроса без заголовка X-API-Key"""
    response = client.post("/register", json={"phone_number": "+998900000000"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}


def test_register_wrong_auth():
    """Попытка запроса с неверным ключом"""
    headers = {"X-API-Key": WRONG_API_KEY}
    response = client.post(
        "/register", json={"phone_number": "+998900000000"}, headers=headers
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}


# --- 3. Тесты функционала (Happy Path & Validation) ---


def test_register_success():
    """Успешная регистрация"""
    headers = {"X-API-Key": VALID_API_KEY}
    payload = {"phone_number": "+998901234567"}

    response = client.post("/register", json=payload, headers=headers)

    # Проверяем статус
    assert response.status_code == 200
    # Проверяем структуру ответа
    data = response.json()
    assert data["status"] == "ok"
    assert "user_id" in data
    assert isinstance(data["user_id"], int)


def test_register_validation_error():
    """Ошибка валидации данных (не передали phone_number)"""
    headers = {"X-API-Key": VALID_API_KEY}
    payload = {}  # Пустой JSON

    response = client.post("/register", json=payload, headers=headers)

    assert response.status_code == 422  # Стандартный код ошибки валидации в FastAPI


def test_create_order_success():
    """Успешное создание заказа"""
    headers = {"X-API-Key": VALID_API_KEY}
    payload = {"user_id": 101, "tariff_code": "standard_300"}

    response = client.post("/create_order", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["order_id"] > 0
