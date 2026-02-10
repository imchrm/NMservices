# Контекст сессии: MVP Services (lucid-beaver)

## Дата сессии: 2026-02-03 / 2026-02-04
## Ветка: lucid-beaver (смержена в main)
## Сессия ID: 04711798-072e-495a-81a6-5b0d8f999bc0

---

## Главная задача сессии

Реализация второго этапа MVP проекта NMservices -- каталог услуг (таблица `services`) и расширение таблицы заказов (`orders`). Техническое задание описано в `docs/tasks/MVP_services_table.md`.

---

## Принятые ключевые решения

| Вопрос | Решение | Обоснование |
|--------|---------|-------------|
| `total_amount` при создании заказа | **Вариант C** -- копируем `base_price` из услуги в `total_amount` при создании заказа + храним `service_id` для истории | Фиксируем цену на момент заказа, если цена услуги изменится позже |
| Удаление услуг | **Мягкое удаление** (`is_active = false`) | Целостность данных, аудит, восстановление, отчётность |
| `tariff_code` в OrderCreateRequest | **Удалить**, заменить на `service_id` | MVP, обратная совместимость пока не критична |
| `Numeric(10, 2)` для `base_price` | Достаточно для цен в сумах (до 99 999 999.99) | Подтверждено пользователем |
| `service_id` в OrderCreateRequest | **Обязательное поле** (`Field(...)`) | Подтверждено пользователем |
| Фильтрация GET /services | Да, параметр `include_inactive=true` для админов | Удобно для управления |
| Стратегия коммитов | Логические группы (5 групп) | Каждый коммит -- рабочее состояние |
| Версия проекта | `0.5.2` -> `0.6.0` | Minor version bump, новый функционал без breaking changes |

---

## Что было реализовано (все 5 групп завершены)

### Группа 1: Миграции + SQLAlchemy модели
**Коммит:** `feat: add Service model and extend Order for MVP`

- Создана миграция `b2c3d4e5f6a7_add_services_table.py` -- таблица `services` с полями: id, name, description, base_price, duration_minutes, is_active, created_at, updated_at + индекс по is_active
- Создана миграция `c3d4e5f6a7b8_extend_orders_table.py` -- расширение `orders`: service_id (FK -> services.id, ON DELETE SET NULL), address_text, scheduled_at + индекс по service_id
- Обновлена модель `Service` в `src/nms/models/db_models.py` (SQLAlchemy)
- Обновлена модель `Order` -- добавлены поля service_id, address_text, scheduled_at + relationship к Service

### Группа 2: Pydantic модели + API services
**Коммит:** `feat: add Pydantic models and API for services`

- Создан файл `src/nms/models/service.py` -- ServiceResponse, ServiceCreateRequest, ServiceUpdateRequest
- Обновлен `src/nms/models/order.py` -- OrderCreateRequest: заменен `tariff_code` на `service_id`, добавлены `address_text`, `scheduled_at`. Добавлен OrderDetailResponse
- Обновлен `src/nms/models/__init__.py` -- экспорт новых моделей
- Создан `src/nms/api/services.py` -- полный CRUD:
  - `GET /services` -- список активных услуг (с фильтром `include_inactive`)
  - `GET /services/{service_id}` -- детали услуги
  - `POST /services` -- создание услуги
  - `PATCH /services/{service_id}` -- обновление услуги
  - `DELETE /services/{service_id}` -- мягкое удаление (деактивация)

### Группа 3: OrderService + main.py
**Коммит:** `feat: update OrderService and integrate services router`

- Обновлен `src/nms/services/order.py` -- `create_order` теперь принимает `service_id` вместо `tariff_code`, валидирует услугу, копирует цену
- Обновлен `src/nms/api/orders.py` -- новые параметры запроса
- Обновлен `src/nms/main.py` -- подключен services router, обновлен legacy endpoint `/create_order`

### Группа 4: Seed данные + CLI
**Коммит:** `feat: add seed data migration and services menu in CLI`

- Создана миграция `d4e5f6a7b8c9_seed_services_data.py` -- 4 начальных услуги:
  - Классический массаж (150 000 сум, 60 мин)
  - Спортивный массаж (180 000 сум, 60 мин)
  - Массаж спины (100 000 сум, 30 мин)
  - Антицеллюлитный массаж (200 000 сум, 45 мин)
- Обновлен `scripts/db_cli.py`:
  - Переименован `OrderManager` -> `DatabaseManager`
  - Добавлено меню "3. Услуги" (3a -- показать все, 3b -- создать, 3c -- обновить, 3d -- деактивировать)
  - Обновлено создание заказов -- теперь требует service_id
  - Обновлено отображение заказов -- показывает service_id и address

### Группа 5: Тесты + документация
**Коммит:** `test: add services tests and update docs for MVP`

- Создан `tests/test_services.py` -- 13 тестов для services API
- Обновлен `tests/test_main.py` -- использует `service_id` вместо `tariff_code`
- Обновлен `tests/conftest.py` -- добавлена фикстура `test_service`
- Обновлен `docs/development/database-schema-mvp.md` -- добавлены новые поля orders

### Дополнительно
**Коммит:** `chore: bump version to 0.6.0 for MVP release`
- Обновлена версия в `pyproject.toml`: `0.5.2` -> `0.6.0`

---

## Полная цепочка коммитов (в порядке создания)

```
f980336 feat: add Service model and extend Order for MVP
8a41956 feat: add Pydantic models and API for services
cb18761 feat: update OrderService and integrate services router
a9a05b5 feat: add seed data migration and services menu in CLI
76089b7 test: add services tests and update docs for MVP
b43cfa8 chore: bump version to 0.6.0 for MVP release
```

Все коммиты смержены в main.

---

## Цепочка миграций Alembic

```
6f83ab8ac77e (initial_schema)
  -> 5f637e23bc5d (add_telegram_id_to_users)
    -> a1b2c3d4e5f6 (add_language_code_to_users)
      -> b2c3d4e5f6a7 (add_services_table)        <-- NEW
        -> c3d4e5f6a7b8 (extend_orders_table)      <-- NEW
          -> d4e5f6a7b8c9 (seed_services_data)      <-- NEW
```

---

## Файлы, которые были созданы/изменены

### Созданные файлы:
- `alembic/versions/b2c3d4e5f6a7_add_services_table.py`
- `alembic/versions/c3d4e5f6a7b8_extend_orders_table.py`
- `alembic/versions/d4e5f6a7b8c9_seed_services_data.py`
- `src/nms/models/service.py`
- `src/nms/api/services.py`
- `tests/test_services.py`

### Измененные файлы:
- `src/nms/models/db_models.py` -- добавлена модель Service, расширена модель Order
- `src/nms/models/order.py` -- заменен tariff_code на service_id
- `src/nms/models/__init__.py` -- экспорт новых моделей
- `src/nms/api/orders.py` -- обновлен endpoint создания заказа
- `src/nms/services/order.py` -- обновлен OrderService
- `src/nms/main.py` -- подключен services router
- `scripts/db_cli.py` -- добавлено меню услуг
- `tests/conftest.py` -- добавлена фикстура test_service
- `tests/test_main.py` -- обновлены тесты заказов
- `docs/development/database-schema-mvp.md` -- обновлена документация
- `pyproject.toml` -- версия 0.6.0

---

## Где сессия остановилась и текущий прогресс верификации

Вся реализация MVP Задачи 1 (Backend) завершена и смержена в main. План верификации на реальных серверах:

| # | Шаг | Машина | Статус |
|---|-----|--------|--------|
| 1 | Миграция БД (`alembic upgrade head`) | dm@id | ✅ Выполнено (2026-02-10) |
| 2 | Проверка структуры БД через psql | dm@id | ❌ Не выполнено |
| 3 | Протестировать db_cli.py | dm@id | ❌ Не выполнено |
| 4 | Запустить pytest на сервере | dm@id | ❌ Не выполнено |
| 5 | Запустить удалённые тесты (curl/httpx к API) | zum@zu | ❌ Не выполнено |
| 6 | Проверить API услуг (GET/POST /services) | zum@zu | ❌ Не выполнено |
| 7 | Создание заказа с услугой (POST /orders с service_id) | zum@zu | ❌ Не выполнено |

### Результат миграции БД (шаг 1):
```
INFO  [alembic.runtime.migration] Running upgrade a1b2c3d4e5f6 -> b2c3d4e5f6a7, add_services_table
INFO  [alembic.runtime.migration] Running upgrade b2c3d4e5f6a7 -> c3d4e5f6a7b8, extend_orders_table
INFO  [alembic.runtime.migration] Running upgrade c3d4e5f6a7b8 -> d4e5f6a7b8c9, seed_services_data
```

Все 3 миграции применены успешно на PostgreSQL (dm@id).

---

## Незавершённые задачи / Что делать дальше

Согласно глобальному плану `docs/tasks/MVP_PLAN.md`:

### Задача 1 (Backend) -- ЗАВЕРШЕНА (код написан, верификация в процессе)
- [x] Применить миграции на продакшн/стейджинг БД
- [ ] Проверить структуру БД через psql (шаг 2)
- [ ] Протестировать db_cli.py (шаг 3)
- [ ] Запустить pytest на сервере (шаг 4)
- [ ] Проверить работу API на реальном сервере (шаги 5-8)

### Задача 2 (Telegram-бот: флоу заказа) -- НЕ НАЧАТА
- Интеграция с API услуг
- Экран выбора услуги (inline-кнопки)
- Ввод адреса
- Подтверждение заказа
- Отправка заказа в API

### Задача 3 (Telegram-бот: уведомления о статусе) -- НЕ НАЧАТА
- Webhook/polling для событий статуса
- Отправка уведомлений по telegram_id

### Задача 4 (Admin Panel: управление услугами) -- НЕ НАЧАТА
- CRUD для services в Admin Panel (React, react-admin)
- Отдельный репозиторий: `NMservices-Admin`

### Задача 5 (Admin Panel: управление заказами) -- НЕ НАЧАТА
### Задача 6 (Admin Panel: просмотр пользователей) -- НЕ НАЧАТА
### Задача 7 (Интеграция и тестирование) -- НЕ НАЧАТА

---

## Структура проекта (актуальная)

```
NMservices/
  src/nms/
    api/
      __init__.py
      dependencies.py
      users.py
      orders.py
      services.py          <-- NEW
      admin/
        users.py
        orders.py
    models/
      __init__.py
      db_models.py          (User, Order, Service)
      user.py
      order.py              (OrderCreateRequest с service_id)
      service.py            <-- NEW
    services/
      auth.py
      order.py              (OrderService -- service_id вместо tariff_code)
    config.py
    database.py
    main.py
  scripts/
    db_cli.py               (DatabaseManager, меню услуг)
  alembic/versions/
    6f83ab8ac77e_initial_schema.py
    5f637e23bc5d_add_telegram_id_to_users.py
    a1b2c3d4e5f6_add_language_code_to_users.py
    b2c3d4e5f6a7_add_services_table.py         <-- NEW
    c3d4e5f6a7b8_extend_orders_table.py        <-- NEW
    d4e5f6a7b8c9_seed_services_data.py         <-- NEW
  tests/
    conftest.py
    test_main.py
    test_services.py        <-- NEW
  docs/
    tasks/
      MVP_PLAN.md
      MVP_services_table.md
      MVP+_extend_schema.md
    development/
      database-schema-mvp.md
```

---

## Технический стек

- Python 3.11+
- FastAPI 0.123.x
- SQLAlchemy 2.x (async, asyncpg)
- Alembic (миграции)
- Pydantic 2.x
- PostgreSQL
- Poetry (управление зависимостями)
- pytest + pytest-asyncio (тесты с aiosqlite in-memory)
- Версия: 0.6.0

---

## Окружение

- Разработка: Windows (`zum@zu`), git worktrees
- Сервер: Linux (`dm@id`, IP: 192.168.1.191)
- БД: PostgreSQL на сервере `dm@id`
- Ветка разработки: `lucid-beaver` (смержена в main)

---

## Следующий этап (MVP+)

Документ: `docs/tasks/MVP+_extend_schema.md`

Планируется разделение на:
- `tariffs` -- варианты тарифов для одной услуги (30/60/90 мин)
- `order_items` -- несколько услуг в одном заказе
- `addresses` -- сохранённые адреса пользователя
- `order_addresses` -- копия адреса на момент создания заказа
