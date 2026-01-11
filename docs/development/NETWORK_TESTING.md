# Тестирование API в локальной сети

Руководство по тестированию NMservices API из локальной сети с использованием Telegram-бота или тестового скрипта.

## Конфигурация

### Локальная сеть
- **IP сервера**: `192.168.1.219` (ваш WiFi адрес)
- **Порт**: `8000`
- **База данных**: PostgreSQL на `localhost:5432/nomus`

### API Ключи
По умолчанию используется `test_secret` (из `src/nms/config.py:25`).

Для изменения создайте файл `.env`:
```env
API_SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/nomus
ENVIRONMENT=development
```

## Шаг 1: Запуск сервера

На машине с базой данных (localhost):

```bash
# Убедитесь, что PostgreSQL запущена и база данных 'nomus' создана
# Запустите сервер на всех интерфейсах (0.0.0.0)
poetry run uvicorn nms.main:app --reload --app-dir src --host 0.0.0.0 --port 8000
```

Проверьте, что сервер слушает на всех интерфейсах:
```bash
# Windows PowerShell
netstat -an | findstr ":8000"
# Должно показать: TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING
```
```bash
# Linux/Mac bash
netstat -an | grep ":8000"
# Должно показать: tcp  0   0    127.0.0.1:8000           0.0.0.0:*              LISTEN
```

### Настройка файервола (Windows)

Если подключение не работает, откройте порт 8000:

```powershell
# PowerShell (от администратора)
New-NetFirewallRule -DisplayName "NMservices API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

## Шаг 2: Тестирование подключения

### Способ 1: Браузер (с той же машины)
Откройте: http://192.168.1.219:8000/docs

### Способ 2: Curl (с другой машины в локальной сети)
```bash
curl http://192.168.1.219:8000/
```

Должен вернуть:
```json
{"message": "NoMus API is running"}
```

## Шаг 3: Тестирование регистрации

### Вариант A: Использование тестового скрипта

Запустите скрипт `scripts/test_registration.py`:

```bash
poetry run python scripts/test_registration.py
```

Скрипт выполнит:
1. Проверку доступности сервера
2. Регистрацию тестового пользователя
3. Вывод результата с user_id

**Настройка скрипта:**

Отредактируйте константы в `scripts/test_registration.py`:
```python
API_BASE_URL = "http://192.168.1.219:8000"  # IP вашего сервера
API_KEY = "test_secret"                      # Ваш API ключ
TEST_PHONE = "+998901234567"                 # Тестовый номер
```

### Вариант B: Из Telegram-бота (NoMus)

В коде вашего бота используйте `httpx` для отправки запросов:

```python
import httpx

async def register_user_via_api(phone_number: str) -> dict:
    """Регистрирует пользователя через NMservices API."""
    api_url = "http://192.168.1.219:8000/users/register"
    api_key = "test_secret"

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "phone_number": phone_number
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

# Использование в обработчике бота:
result = await register_user_via_api("+998901234567")
user_id = result.get("user_id")
print(f"User registered with ID: {user_id}")
```

### Вариант C: PowerShell

```powershell
$headers = @{ "X-API-Key" = "test_secret" }
$body = @{ phone_number = "+998901234567" } | ConvertTo-Json

Invoke-RestMethod -Uri "http://192.168.1.219:8000/users/register" `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $body
```

### Вариант D: Curl

```bash
curl -X POST "http://192.168.1.219:8000/users/register" \
  -H "X-API-Key: test_secret" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+998901234567"}'
```

## Ожидаемый результат

При успешной регистрации:
```json
{
  "status": "ok",
  "message": "User registered successfully",
  "user_id": 1
}
```

В логах сервера вы увидите:
```
[STUB-SMS] Sending code to +998901234567...
[DB] User +998901234567 saved with ID 1
```

При повторной регистрации того же номера:
```
[DB] User +998901234567 already exists with ID 1
```

## Проверка в базе данных

Подключитесь к PostgreSQL и проверьте:

```sql
-- Посмотреть всех зарегистрированных пользователей
SELECT * FROM users;

-- Проверить конкретного пользователя
SELECT * FROM users WHERE phone_number = '+998901234567';
```

## Troubleshooting

### Проблема: Connection refused

**Решение:**
1. Убедитесь, что сервер запущен на `0.0.0.0`, а не на `127.0.0.1`
2. Проверьте файервол Windows
3. Убедитесь, что используете правильный IP (192.168.1.219)

### Проблема: 401 Unauthorized

**Решение:**
Проверьте, что API ключ совпадает с `API_SECRET_KEY` в конфигурации.

### Проблема: 500 Internal Server Error

**Решение:**
1. Проверьте логи сервера
2. Убедитесь, что PostgreSQL запущена
3. Проверьте, что база данных 'nomus' создана
4. Проверьте `DATABASE_URL` в конфигурации

### Проблема: База данных не подключается

**Решение:**
```bash
# Проверьте статус PostgreSQL
# Создайте базу данных если нужно
psql -U postgres -c "CREATE DATABASE nomus;"

# Инициализируйте таблицы
poetry run python -c "import asyncio; from nms.database import init_db; asyncio.run(init_db())"
```

## Архитектура тестирования

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│ Telegram Bot    │─────────▶│  NMservices API  │─────────▶│ PostgreSQL  │
│ (NoMus)         │  HTTP    │  (FastAPI)       │  SQL     │  (nomus)    │
│ 192.168.1.XXX   │          │  192.168.1.219   │          │  localhost  │
└─────────────────┘          │  :8000           │          │  :5432      │
                             └──────────────────┘          └─────────────┘
      ИЛИ                            ▲
                                     │ HTTP
┌─────────────────┐                  │
│ Test Script     │──────────────────┘
│ (Python)        │
└─────────────────┘
```

## Следующие шаги

После успешного тестирования:
1. Интегрируйте код регистрации в вашего Telegram-бота
2. Протестируйте полный флоу регистрации через бота
3. Проверьте корректность сохранения данных в БД
4. Настройте production окружение с правильными API ключами
