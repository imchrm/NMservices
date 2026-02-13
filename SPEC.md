# ТЗ Backend — NMservices

## Общие сведения

- **Репозиторий:** NMservices
- **Стек:** FastAPI + SQLAlchemy (async) + PostgreSQL
- **Ветка:** `claude/review-admin-panel-context-u8OxO`

---

## Задача 1: Фильтрация по диапазону дат

### Цель
Добавить query-параметры `date_from` и `date_to` в существующие endpoint'ы списков для фильтрации записей по полю `created_at`.

### Затрагиваемые файлы

| Файл | Что меняется |
|---|---|
| `src/nms/api/admin/orders.py` | Функция `list_orders()` — новые параметры `date_from`, `date_to` |
| `src/nms/api/admin/services.py` | Функция `list_services()` — новые параметры `date_from`, `date_to` |
| `src/nms/api/admin/users.py` | Функция `list_users()` — новые параметры `date_from`, `date_to` |

### Спецификация

#### Новые query-параметры (одинаковые для всех трёх endpoint'ов)

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|---|---|---|---|---|
| `date_from` | `datetime` (ISO 8601) | Нет | `None` | Начало диапазона (включительно) |
| `date_to` | `datetime` (ISO 8601) | Нет | `None` | Конец диапазона (включительно) |

#### Логика фильтрации

```python
# Добавить в query и count_query:
if date_from is not None:
    query = query.where(Model.created_at >= date_from)
    count_query = count_query.where(Model.created_at >= date_from)

if date_to is not None:
    query = query.where(Model.created_at <= date_to)
    count_query = count_query.where(Model.created_at <= date_to)
```

#### Примеры запросов

```
GET /admin/orders?date_from=2025-01-01T00:00:00&date_to=2025-01-31T23:59:59
GET /admin/services?date_from=2025-06-01T00:00:00
GET /admin/users?date_to=2025-12-31T23:59:59
```

#### Валидация
- Если `date_from > date_to` — валидация не требуется на уровне backend (результат будет пустым списком)
- Если указан только один параметр — фильтрация работает как "от даты" или "до даты"

---

## Задача 2: Добавить `total_services` в `/admin/stats`

### Цель
Расширить существующий endpoint `/admin/stats`, чтобы он возвращал количество активных сервисов. Это позволит Dashboard получать все данные одним запросом.

### Затрагиваемые файлы

| Файл | Что меняется |
|---|---|
| `src/nms/models/admin.py` | Модель `AdminStatsResponse` — новое поле `total_services` |
| `src/nms/api/admin/orders.py` | Функция `get_stats()` — подсчёт сервисов |

### Спецификация

#### Изменение Pydantic-модели (`AdminStatsResponse`)

```python
class AdminStatsResponse(BaseModel):
    total_users: int
    total_orders: int
    total_services: int          # <-- НОВОЕ ПОЛЕ
    orders_by_status: dict[str, int]
```

#### Изменение endpoint'а `get_stats()`

Добавить запрос подсчёта активных сервисов:

```python
from nms.models.db_models import User, Order, Service  # добавить Service

# Total active services
services_count = await db.execute(
    select(func.count(Service.id)).where(Service.is_active == True)
)
total_services = services_count.scalar_one()
```

#### Новый формат ответа

```json
{
    "total_users": 42,
    "total_orders": 128,
    "total_services": 7,
    "orders_by_status": {
        "pending": 15,
        "completed": 100,
        "cancelled": 13
    }
}
```

> **Примечание:** считаются только активные сервисы (`is_active = True`), чтобы соответствовать бизнес-логике Dashboard.
