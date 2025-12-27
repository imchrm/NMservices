# Database Setup Guide

Руководство по настройке PostgreSQL для проекта NoMus Telegram-бота.

## Требования

- PostgreSQL 12+ установлен и запущен
- Доступ к PostgreSQL серверу (локальному или удалённому)

## Быстрый старт

### 1. Установка зависимостей

```bash
poetry install
```

Это установит новые зависимости:
- `asyncpg` - асинхронный драйвер PostgreSQL
- `sqlalchemy[asyncio]` - ORM с поддержкой async/await

### 2. Создание базы данных

Подключитесь к PostgreSQL и создайте базу данных:

```bash
# Используя psql
psql -U postgres

# В консоли psql:
CREATE DATABASE nomus;
\q
```

Или используя pgAdmin или другой GUI инструмент.

### 3. Инициализация таблиц

**Вариант A: Автоматически через SQLAlchemy** (рекомендуется для разработки)

Таблицы будут созданы автоматически при первом запуске приложения.

**Вариант B: Вручную через SQL скрипт**

```bash
psql -U postgres -d nomus -f scripts/init_db.sql
```

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите подключение к вашей БД:

```env
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@HOST:PORT/nomus
```

#### Примеры для разных окружений:

**Локальная разработка (Windows):**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/nomus
```

**Локальная разработка (Linux/Mac):**
```env
DATABASE_URL=postgresql+asyncpg://postgres:mypassword@localhost:5432/nomus
```

**Docker:**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/nomus
```

**Удалённый сервер:**
```env
DATABASE_URL=postgresql+asyncpg://user:pass@192.168.1.100:5432/nomus
```

### 5. Запуск приложения

```bash
poetry run uvicorn nms.main:app --reload --app-dir src
```

При запуске вы должны увидеть подтверждение подключения к БД в логах.

## Схема базы данных

### Таблица `users`

| Колонка | Тип | Описание |
|---------|-----|----------|
| **id** | SERIAL | Первичный ключ, автоинкремент |
| **phone_number** | VARCHAR(20) | Уникальный номер телефона |
| **created_at** | TIMESTAMP | Дата создания записи |
| **updated_at** | TIMESTAMP | Дата последнего обновления |

**Индексы:**
- Primary key на `id`
- Unique constraint на `phone_number`
- Index на `phone_number` для быстрого поиска

**Триггеры:**
- Автоматическое обновление `updated_at` при изменении записи

## Тестирование подключения

### Проверка через API

После запуска приложения, зарегистрируйте тестового пользователя:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/users/register' \
  -H 'accept: application/json' \
  -H 'X-API-Key: test_secret' \
  -H 'Content-Type: application/json' \
  -d '{
  "phone_number": "+998901234567"
}'
```

Ожидаемый ответ:
```json
{
  "status": "ok",
  "message": "User registered successfully",
  "user_id": 1
}
```

### Проверка в базе данных

```bash
psql -U postgres -d nomus

SELECT * FROM users;
```

Должны увидеть созданного пользователя с `id=1`.

### Повторная регистрация

При повторной регистрации с тем же номером телефона вернётся существующий `user_id`:

```bash
# Повторный запрос вернёт тот же user_id=1
curl -X 'POST' \
  'http://127.0.0.1:8000/users/register' \
  -H 'X-API-Key: test_secret' \
  -H 'Content-Type: application/json' \
  -d '{"phone_number": "+998901234567"}'
```

## Архитектура

### Новые файлы

```
src/nms/
├── database.py              # Конфигурация БД и session management
├── config.py                # Добавлена настройка DATABASE_URL
├── models/
│   └── db_models.py         # ORM модели (User)
└── services/
    └── auth.py              # Обновлён для работы с БД
```

### Изменения в коде

**До (заглушка):**
```python
@staticmethod
def save_user(phone: str) -> int:
    fake_id = random.randint(1000, 9999)
    return fake_id
```

**После (реальная БД):**
```python
@staticmethod
async def save_user(phone: str, db: AsyncSession) -> int:
    # Проверка существующего пользователя
    result = await db.execute(select(User).where(User.phone_number == phone))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return existing_user.id

    # Создание нового пользователя
    new_user = User(phone_number=phone)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user.id  # Возвращается реальный ID из БД
```

## Устранение неполадок

### 1. Ошибка подключения

**Ошибка:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Решение:**

1. Проверьте, что PostgreSQL запущен:
   ```bash
   # Windows
   pg_ctl status -D "C:\Program Files\PostgreSQL\15\data"

   # Linux/Mac
   sudo systemctl status postgresql
   ```

2. Проверьте настройки в `.env` файле

3. Убедитесь, что PostgreSQL принимает подключения:
   - Проверьте `pg_hba.conf`
   - Проверьте `postgresql.conf` (параметр `listen_addresses`)

### 2. База данных не существует

**Ошибка:**
```
FATAL: database "nomus" does not exist
```

**Решение:**
```bash
psql -U postgres
CREATE DATABASE nomus;
\q
```

### 3. Ошибки прав доступа

**Ошибка:**
```
FATAL: password authentication failed for user "postgres"
```

**Решение:**

1. Проверьте правильность пароля в `.env`
2. Сбросьте пароль PostgreSQL если нужно:
   ```bash
   psql -U postgres
   ALTER USER postgres PASSWORD 'newpassword';
   ```

3. Предоставьте права на базу данных:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE nomus TO postgres;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
   ```

### 4. Таблицы не создаются

**Решение:**

Создайте таблицы вручную:
```bash
psql -U postgres -d nomus -f scripts/init_db.sql
```

Или добавьте startup event в `main.py`:
```python
from .database import init_db

@app.on_event("startup")
async def startup():
    await init_db()
```

### 5. Миграции и обновление схемы

Для production рекомендуется использовать Alembic:

```bash
# Установка
poetry add alembic

# Инициализация
poetry run alembic init alembic

# Создание миграции
poetry run alembic revision --autogenerate -m "Create users table"

# Применение миграции
poetry run alembic upgrade head
```

## Рекомендации для production

1. **Используйте connection pooling:**
   ```python
   engine = create_async_engine(
       settings.database_url,
       pool_size=20,
       max_overflow=10,
   )
   ```

2. **Настройте backup:**
   ```bash
   # Ежедневный бэкап
   pg_dump -U postgres nomus > backup_$(date +%Y%m%d).sql
   ```

3. **Мониторинг:**
   - Логируйте медленные запросы
   - Отслеживайте размер БД
   - Мониторьте количество подключений

4. **Безопасность:**
   - Используйте сильные пароли
   - Ограничьте доступ по IP (`pg_hba.conf`)
   - Используйте SSL для удалённых подключений
   - Храните пароли в переменных окружения или secrets manager

5. **Индексы:**
   - Добавляйте индексы для часто используемых полей
   - Регулярно проверяйте неиспользуемые индексы

## См. также

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI with Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## Контакты

При возникновении проблем создайте issue на GitHub с логами и описанием окружения.
