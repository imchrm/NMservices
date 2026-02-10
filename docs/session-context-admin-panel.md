# Контекст сессии: Задача 2 — Admin Panel

## Задача

Реализация полной Admin Panel для проекта NMservices согласно `docs/tasks/MVP_PLAN.md` → Задача 2.

---

## Проект NMservices — текущее состояние

### Что уже сделано (Задача 1 — Backend ✅)

Backend полностью реализован и верифицирован (2026-02-10):
- FastAPI + SQLAlchemy 2 (async) + PostgreSQL
- Таблицы: `users`, `orders`, `services`
- API endpoints: CRUD для услуг, создание заказов, регистрация пользователей
- Admin API: полный CRUD для пользователей, заказов + статистика
- Тесты: 30/30 passed
- Версия: 0.6.0

### Инфраструктура

| Компонент | Детали |
|-----------|--------|
| Сервер | `dm@id` (192.168.1.191), Linux |
| Клиент/Разработка | `zum@zu` (Windows) |
| БД | PostgreSQL на dm@id, база `nomus`, user: `postgres` |
| Backend | Python 3.11+, FastAPI, uvicorn, порт 8000 |
| Backend путь (сервер) | `~/dev/python/NMservices` |
| Backend путь (Windows) | `C:\Users\zum\dev\python\NMservices` |
| Admin Panel путь (Windows) | `C:\Users\zum\dev\js\NMservices-Admin` |
| Репозиторий Backend | `imchrm/NMservices` |
| Репозиторий Admin | `NMservices-Admin` (создать) |

### Аутентификация

Два независимых механизма через заголовки:

| Тип | Заголовок | Env-переменная | Для чего |
|-----|-----------|----------------|----------|
| API Key | `X-API-Key` | `API_SECRET_KEY` | Клиентские endpoints (/users, /orders, /services) |
| Admin Key | `X-Admin-Key` | `ADMIN_SECRET_KEY` | Админские endpoints (/admin/*) |

Реальные ключи на сервере указаны в `.env` файле проекта NMservices.

### CORS

Настройка в `src/nms/config.py`:
```
CORS_ORIGINS=http://localhost:5173    # Vite dev server (по умолчанию)
```
Разрешённые методы: GET, POST, PUT, PATCH, DELETE, OPTIONS. Headers: все.

**Важно:** для разработки Admin Panel может потребоваться добавить URL в `CORS_ORIGINS` на сервере.

---

## Полная карта API endpoints

### Health Check
| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | `/` | Нет | `{"message": "NoMus API is running"}` |

### Users (X-API-Key)
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/users/register` | `{phone_number, telegram_id?, language_code?}` | `{status, message, user_id}` |
| GET | `/users/by-telegram/{telegram_id}` | — | `{id, phone_number, telegram_id, language_code, created_at, updated_at}` |
| PATCH | `/users/{user_id}/language` | `{language_code}` | `{status}` |

### Services (X-API-Key)
| Method | Path | Request | Response | Status |
|--------|------|---------|----------|--------|
| GET | `/services?include_inactive=false` | — | `{services: [...], total}` | 200 |
| GET | `/services/{service_id}` | — | `{id, name, description, base_price, duration_minutes, is_active}` | 200 |
| POST | `/services` | `{name, description?, base_price?, duration_minutes?, is_active?}` | ServiceResponse | 201 |
| PATCH | `/services/{service_id}` | `{name?, description?, base_price?, duration_minutes?, is_active?}` | ServiceResponse | 200 |
| DELETE | `/services/{service_id}` | — | — (soft delete: is_active=false) | 204 |

### Orders (X-API-Key)
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/orders` | `{user_id, service_id, address_text?, scheduled_at?, notes?}` | `{status, order_id, message}` |

### Admin Users (X-Admin-Key)
| Method | Path | Query params | Request | Response |
|--------|------|-------------|---------|----------|
| GET | `/admin/users` | `skip=0, limit=100, sort_by=[id\|phone_number\|created_at\|updated_at], order=[asc\|desc]` | — | `{users: [...], total}` |
| POST | `/admin/users` | — | `{phone_number, telegram_id?, language_code?}` | AdminUserResponse (201) |
| GET | `/admin/users/{user_id}` | — | — | AdminUserResponse |
| DELETE | `/admin/users/{user_id}` | — | — | `{status, message, orders_deleted}` |
| GET | `/admin/users/{user_id}/orders` | — | — | `[AdminOrderResponse, ...]` |

### Admin Orders (X-Admin-Key)
| Method | Path | Query params | Request | Response |
|--------|------|-------------|---------|----------|
| GET | `/admin/orders` | `skip=0, limit=100, status_filter?, sort_by=[id\|user_id\|status\|total_amount\|created_at\|updated_at], order=[asc\|desc]` | — | `{orders: [...], total}` |
| POST | `/admin/orders` | — | `{user_id, status?, total_amount?, notes?}` | AdminOrderResponse (201) |
| GET | `/admin/orders/{order_id}` | — | — | AdminOrderWithUserResponse (includes nested user object) |
| PATCH | `/admin/orders/{order_id}` | — | `{status?, total_amount?, notes?}` | AdminOrderResponse |
| DELETE | `/admin/orders/{order_id}` | — | — | `{status, message}` |

### Admin Stats (X-Admin-Key)
| Method | Path | Response |
|--------|------|----------|
| GET | `/admin/stats` | `{total_users, total_orders, orders_by_status: {"pending": N, ...}}` |

### Legacy (deprecated)
| Method | Path | Note |
|--------|------|------|
| POST | `/register` | Использовать `/users/register` |
| POST | `/create_order` | Использовать `/orders` |

---

## Схема БД (актуальная, реализованная)

### users
| Поле | Тип | Ограничения |
|------|-----|-------------|
| id | SERIAL | PK |
| phone_number | VARCHAR(20) | UNIQUE NOT NULL |
| telegram_id | BIGINT | UNIQUE, nullable |
| language_code | VARCHAR(5) | nullable |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL, auto-update |

### services
| Поле | Тип | Ограничения |
|------|-----|-------------|
| id | SERIAL | PK |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| base_price | DECIMAL(10,2) | nullable |
| duration_minutes | INTEGER | nullable |
| is_active | BOOLEAN | NOT NULL, default true |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL, auto-update |

### orders
| Поле | Тип | Ограничения |
|------|-----|-------------|
| id | SERIAL | PK |
| user_id | INTEGER | NOT NULL, FK → users.id ON DELETE CASCADE |
| service_id | INTEGER | nullable, FK → services.id ON DELETE SET NULL |
| status | VARCHAR(50) | NOT NULL, default 'pending' |
| total_amount | DECIMAL(10,2) | nullable |
| address_text | TEXT | nullable |
| scheduled_at | TIMESTAMP | nullable |
| notes | TEXT | nullable |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL, auto-update |

**Статусы заказов:** pending, confirmed, in_progress, completed, cancelled

### Текущие данные в БД
- **users:** 22+ записей
- **services:** 4 записи (Классический массаж 150000, Спортивный 180000, Спины 100000, Антицеллюлитный 200000)
- **orders:** 22+ записей

---

## Что нужно сделать (Задача 2)

### 2.1. Инициализация проекта
- Создать проект: Vite + React + TypeScript
- Установить react-admin и зависимости
- Настроить dataProvider для API (http://192.168.1.191:8000)
- Настроить authProvider (X-Admin-Key)

### 2.2. Dashboard
- Статистика: кол-во пользователей, заказов, услуг (GET /admin/stats)
- Заказы по статусам

### 2.3. Услуги (services)
- Список (таблица с фильтрацией и сортировкой)
- Просмотр (детальная карточка)
- Создание (форма)
- Редактирование
- Деактивация (soft delete)

### 2.4. Заказы (orders)
- Список (таблица с фильтрацией по статусу, дате)
- Просмотр (детали: пользователь, услуга, адрес, статус)
- Редактирование (смена статуса, notes)
- Создание (ручное администратором)

### 2.5. Пользователи (users)
- Список (таблица)
- Просмотр (профиль + история заказов)

---

## Особенности API для react-admin dataProvider

### Пагинация
API использует `skip` / `limit` (не page/perPage). DataProvider должен конвертировать:
```
react-admin: { page: 2, perPage: 25 }  →  API: { skip: 25, limit: 25 }
```

### Сортировка
API принимает `sort_by` и `order`:
```
react-admin: { field: 'created_at', order: 'DESC' }  →  API: { sort_by: 'created_at', order: 'desc' }
```

### Фильтрация
Заказы поддерживают `status_filter`:
```
react-admin: { status: 'pending' }  →  API: { status_filter: 'pending' }
```

### Ответы — формат обёртки
API возвращает данные в обёртке:
```json
// GET /admin/users → { "users": [...], "total": 5 }
// GET /admin/orders → { "orders": [...], "total": 10 }
// GET /services → { "services": [...], "total": 4 }
```
DataProvider должен извлекать массив из обёртки и возвращать `{ data: [...], total: N }`.

### Услуги используют другой auth-заголовок
- `/services/*` — использует `X-API-Key` (не X-Admin-Key)
- `/admin/*` — использует `X-Admin-Key`
- DataProvider должен отправлять правильный заголовок в зависимости от endpoint

---

## Связанные документы

- `docs/tasks/MVP_PLAN.md` — глобальный план (Задача 2)
- `docs/tasks/MVP_services_table.md` — ТЗ на Backend (Задача 1, завершена)
- `docs/development/database-schema-mvp.md` — полная схема БД
- `docs/session-context-mvp-services.md` — контекст предыдущей сессии (Задача 1)
- `docs/tasks/TODO_pydantic_v2_config.md` — мелкий рефакторинг (не блокирует)

---

## Известные нюансы

1. **CORS:** по умолчанию разрешён только `http://localhost:5173`. Если Admin Panel запускается на другом порту — добавить в `CORS_ORIGINS` на сервере (в `.env`)
2. **Два ключа авторизации:** `/services` и `/orders` используют `X-API-Key`, а `/admin/*` использует `X-Admin-Key`. Admin Panel должна знать оба ключа
3. **Сервер запускать из корня:** `cd ~/dev/python/NMservices && poetry run uvicorn nms.main:app --host 0.0.0.0 --port 8000` (не из поддиректории, иначе `.env` не найдётся)
4. **psql доступ:** `sudo -u postgres psql -d nomus` (peer auth, не по паролю)
5. **Swagger UI:** доступен по `http://192.168.1.191:8000/docs` — можно тестировать API интерактивно
6. **Admin Order Create** (`POST /admin/orders`): не принимает `service_id` — это ограничение текущего admin API. Для создания заказа с услугой используется `POST /orders` (с X-API-Key)
