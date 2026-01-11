"""
Тестовый скрипт для проверки регистрации пользователя через API NMservices.

Использование:
    python scripts/test_registration.py

Этот скрипт:
1. Отправляет POST запрос на эндпоинт /users/register
2. Проверяет успешность регистрации
3. Выводит результат и user_id
"""

import asyncio
import httpx
import sys
from typing import Optional

# Конфигурация
API_BASE_URL = "http://192.168.1.219:8000"  # IP вашего сервера в локальной сети
API_KEY = "test_secret"  # Должен совпадать с API_SECRET_KEY в .env
TEST_PHONE = "+998901234567"  # Тестовый номер телефона


async def test_user_registration(
    phone: str,
    api_url: str = API_BASE_URL,
    api_key: str = API_KEY
) -> Optional[dict]:
    """
    Тестирует регистрацию пользователя.

    Args:
        phone: Номер телефона для регистрации
        api_url: Базовый URL API
        api_key: API ключ для аутентификации

    Returns:
        Ответ от сервера или None в случае ошибки
    """
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "phone_number": phone
    }

    print(f"📱 Тестируем регистрацию пользователя...")
    print(f"   Сервер: {api_url}")
    print(f"   Телефон: {phone}")
    print("-" * 60)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Сначала проверим, что сервер доступен
            print("🔍 Проверка доступности сервера...")
            health_response = await client.get(f"{api_url}/")
            print(f"✅ Сервер доступен: {health_response.json()}")
            print()

            # Отправляем запрос на регистрацию
            print("📤 Отправка запроса на регистрацию...")
            response = await client.post(
                f"{api_url}/users/register",
                headers=headers,
                json=payload
            )

            # Проверяем статус ответа
            if response.status_code == 200:
                result = response.json()
                print("✅ Регистрация успешна!")
                print(f"   User ID: {result.get('user_id')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
                return result
            else:
                print(f"❌ Ошибка: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return None

        except httpx.ConnectError as e:
            print(f"❌ Не удалось подключиться к серверу: {api_url}")
            print(f"   Убедитесь, что:")
            print(f"   1. Сервер запущен (uvicorn)")
            print(f"   2. IP адрес правильный")
            print(f"   3. Порт 8000 открыт в файерволе")
            print(f"   Ошибка: {e}")
            return None

        except httpx.TimeoutException:
            print(f"❌ Таймаут при подключении к серверу")
            return None

        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return None


async def test_multiple_registrations():
    """Тестирует несколько регистраций для проверки работы БД."""
    test_phones = [
        "+998901234567",
        "+998912345678",
        "+998923456789",
    ]

    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 60)
    print()

    results = []
    for phone in test_phones:
        result = await test_user_registration(phone)
        results.append(result)
        print()
        await asyncio.sleep(0.5)  # Небольшая пауза между запросами

    # Статистика
    print("=" * 60)
    print("📊 РЕЗУЛЬТАТЫ")
    print("=" * 60)
    successful = sum(1 for r in results if r is not None)
    print(f"Всего тестов: {len(results)}")
    print(f"Успешных: {successful}")
    print(f"Неудачных: {len(results) - successful}")
    print()

    return results


def main():
    """Главная функция для запуска тестов."""
    try:
        # Запускаем тест с одним номером
        asyncio.run(test_user_registration(TEST_PHONE))

        # Раскомментируйте для множественных тестов:
        # asyncio.run(test_multiple_registrations())

    except KeyboardInterrupt:
        print("\n⚠️  Тест прерван пользователем")
        sys.exit(0)


if __name__ == "__main__":
    main()
