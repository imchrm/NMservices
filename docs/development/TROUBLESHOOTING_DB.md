# Записи не сохраняются в PostgreSQL

## Симптомы

При выполнении запроса регистрации:
```bash
curl -X POST http://127.0.0.1:8000/users/register \
  -H 'X-API-Key: your_api_key' \
  -H 'Content-Type: application/json' \
  -d '{"phone_number": "+998901234567"}'
```

## Диагностика

### Шаг 1: Быстрая диагностика

Запустите скрипт диагностики:

```bash
poetry run python scripts/diagnose_db_issue.py
```

Этот скрипт проверит:
1. Структуру таблицы users
2. Попытается вставить записи через ORM и SQL
3. Покажет все записи в таблице
4. Выявит проблему

### Шаг 2: Проверка структуры через psql

Подключитесь к базе:
```bash
psql -U postgres -d nomus
```

Проверьте структуру таблицы:
```sql
\d+ users
```

**Ожидаемая структура** (должна быть такой):
```
Column       | Type                        | Nullable | Default
-------------+-----------------------------+----------+----------------------------------
id           | integer                     | not null | nextval('users_id_seq'::regclass)
phone_number | character varying(20)       | not null |
created_at   | timestamp without time zone | not null |
updated_at   | timestamp without time zone | not null |

Indexes:
    "users_pkey" PRIMARY KEY, btree (id)
    "users_phone_number_key" UNIQUE CONSTRAINT, btree (phone_number)
    "ix_users_phone_number" btree (phone_number)
```

## Решение 1: Пересоздание таблиц через SQLAlchemy (РЕКОМЕНДУЕТСЯ)

Это самый надежный способ.

### Шаг 1: Сделайте бэкап данных (если есть важные данные)

```bash
pg_dump -U postgres -d nomus -t users > users_backup.sql
```

### Шаг 2: Запустите скрипт пересоздания

```bash
poetry run python scripts/recreate_database.py
```

Скрипт:
1. Покажет текущую структуру таблицы
2. Попросит подтверждение
3. Удалит таблицу users
4. Создаст её заново из модели SQLAlchemy
5. Протестирует вставку записи

### Шаг 3: Проверьте работу API

```bash
curl -X POST http://127.0.0.1:8000/users/register \
  -H 'X-API-Key: your_api_key' \
  -H 'Content-Type: application/json' \
  -d '{"phone_number": "+998901234567"}'
```

Затем проверьте в базе:
```sql
SELECT * FROM users;
```

Должна появиться запись!

## Решение 2: Ручное создание таблицы с правильной структурой

Если не хотите использовать скрипт, создайте таблицу вручную:

```sql
-- Удалите старую таблицу (если есть)
DROP TABLE IF EXISTS users;

-- Создайте sequence для автоинкремента
CREATE SEQUENCE users_id_seq;

-- Создайте таблицу
CREATE TABLE users (
    id INTEGER PRIMARY KEY DEFAULT nextval('users_id_seq'),
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Создайте индекс
CREATE INDEX ix_users_phone_number ON users(phone_number);

-- Свяжите sequence с таблицей
ALTER SEQUENCE users_id_seq OWNED BY users.id;
```

## Решение 3: Использование init_db() из кода

Альтернативный способ через Python:

```bash
poetry run python -c "import asyncio; from nms.database import init_db; asyncio.run(init_db())"
```

Этот метод создаст все таблицы согласно моделям SQLAlchemy.

## Проверка результата

После любого из решений проверьте:

1. **Структура таблицы корректна:**
   ```sql
   \d+ users
   ```

2. **API работает:**
   ```bash
   curl -X POST http://127.0.0.1:8000/users/register \
     -H 'X-API-Key: your_api_key' \
     -H 'Content-Type: application/json' \
     -d '{"phone_number": "+998901234567"}'
   ```

3. **Запись в базе:**
   ```sql
   SELECT * FROM users;
   ```

4. **Повторная регистрация возвращает существующий ID:**
   ```bash
   # Повторный запрос должен вернуть тот же user_id
   curl -X POST http://127.0.0.1:8000/users/register \
     -H 'X-API-Key: your_api_key' \
     -H 'Content-Type: application/json' \
     -d '{"phone_number": "+998901234567"}'
   ```

   В логах должно быть:
   ```
   [DB] User +998901234567 already exists with ID 1
   ```

## Дополнительная диагностика

### Проверка активных транзакций

```sql
SELECT pid, usename, state, query
FROM pg_stat_activity
WHERE datname = 'nomus' AND state != 'idle';
```

### Проверка sequence

```sql
SELECT last_value FROM users_id_seq;
```

### Включение подробного логирования SQLAlchemy

В `src/nms/database.py:11` измените `echo` на `True`:

```python
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Включить логирование всех SQL запросов
    future=True,
)
```

Затем в логах сервера вы увидите все SQL запросы, которые выполняются.

## Возможные ошибки и решения

### Ошибка: "relation 'users' does not exist"

**Решение:** Таблица не создана. Запустите `scripts/recreate_database.py`

### Ошибка: "duplicate key value violates unique constraint"

**Решение:** Пользователь с таким номером уже существует. Это нормально, API вернет существующий user_id.

### Ошибка: "permission denied for table users"

**Решение:** Проверьте права доступа:
```sql
GRANT ALL PRIVILEGES ON TABLE users TO postgres;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO postgres;
```

## Следующие шаги

После исправления проблемы:
1. Протестируйте регистрацию через API
2. Протестируйте через Telegram-бота (см. `NETWORK_TESTING.md`)
3. Проверьте корректность всех операций с БД
