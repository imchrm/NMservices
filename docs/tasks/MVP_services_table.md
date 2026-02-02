# Техническое задание: MVP — Таблица services и расширение orders

## Контекст

Это **второй этап разработки (MVP)**:

| Этап | Название | Статус |
|------|----------|--------|
| 1 | MVP-0 (базовый) | ✅ Готово |
| 2 | **MVP** (текущий) | 🔄 В работе |
| 3 | MVP+ | 📋 Планируется |

---

## Цель

Реализовать минимальный функционал каталога услуг для запуска MVP. Пользователь должен иметь возможность выбрать услугу из каталога и создать заказ с указанием адреса.

---

## Концепция

На этом этапе **одна услуга = один тариф** (в одной таблице `services`).

Примеры записей в `services`:
- "Классический массаж 30 мин" — 100 000 сум
- "Классический массаж 60 мин" — 150 000 сум
- "Спортивный массаж 60 мин" — 180 000 сум

На этапе MVP+ будет разделение на `services` + `tariffs` для большей гибкости.

---

## Текущее состояние

**Реализовано:**
- Таблица `users` (id, phone_number, telegram_id, language_code, created_at, updated_at)
- Таблица `orders` (id, user_id, status, total_amount, notes, created_at, updated_at)
- API endpoints для пользователей и заказов
- CLI утилита `scripts/db_cli.py`

**Не реализовано:**
- Каталог услуг
- Привязка заказа к конкретной услуге
- Адрес выполнения услуги
- Время выполнения услуги

---

## Задачи

### 1. Создать таблицу `services`

**Миграция Alembic:**

```sql
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price DECIMAL(10, 2),
    duration_minutes INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_services_is_active ON services(is_active);
```

**Модель SQLAlchemy:** `src/nms/models/db_models.py`

```python
class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Numeric(10, 2), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

---

### 2. Расширить таблицу `orders`

**Миграция Alembic — добавить поля:**

```sql
ALTER TABLE orders ADD COLUMN service_id INTEGER REFERENCES services(id) ON DELETE SET NULL;
ALTER TABLE orders ADD COLUMN address_text TEXT;
ALTER TABLE orders ADD COLUMN scheduled_at TIMESTAMP;

CREATE INDEX idx_orders_service_id ON orders(service_id);
```

**Обновить модель Order:** `src/nms/models/db_models.py`

```python
service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
address_text = Column(Text, nullable=True)
scheduled_at = Column(DateTime, nullable=True)

service = relationship("Service", backref="orders")
```

---

### 3. Pydantic модели

**Файл:** `src/nms/models/service.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime

class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    base_price: float | None = None
    duration_minutes: int | None = None
    is_active: bool

    model_config = {"from_attributes": True}

class ServiceCreateRequest(BaseModel):
    name: str = Field(..., description="Название услуги")
    description: str | None = Field(None, description="Описание услуги")
    base_price: float | None = Field(None, description="Базовая цена")
    duration_minutes: int | None = Field(None, description="Длительность в минутах")
    is_active: bool = Field(True, description="Активна ли услуга")
```

**Обновить:** `src/nms/models/order.py`

```python
class OrderCreateRequest(BaseModel):
    user_id: int = Field(..., description="User ID")
    service_id: int = Field(..., description="Service ID")
    address_text: str | None = Field(None, description="Адрес выполнения")
    scheduled_at: datetime | None = Field(None, description="Запланированное время")
```

> **Примечание:** Поле `tariff_code` удаляется — теперь используется `service_id`.

---

### 4. API endpoints для услуг

**Файл:** `src/nms/api/services.py`

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/services` | Список активных услуг |
| GET | `/services/{service_id}` | Детали услуги |
| POST | `/services` | Создать услугу (admin) |
| PATCH | `/services/{service_id}` | Обновить услугу (admin) |
| DELETE | `/services/{service_id}` | Деактивировать услугу (admin) |

**Пример ответа GET /services:**

```json
[
  {
    "id": 1,
    "name": "Классический массаж",
    "description": "Расслабляющий массаж всего тела",
    "base_price": 150000.00,
    "duration_minutes": 60,
    "is_active": true
  }
]
```

---

### 5. Обновить CLI утилиту

**Файл:** `scripts/db_cli.py`

Добавить меню:
```
3. Услуги
   a. показать все
   b. создать новую
   c. обновить
   d. деактивировать
```

---

### 6. Начальные данные (seed)

Создать скрипт или миграцию с базовыми услугами:

```sql
INSERT INTO services (name, description, base_price, duration_minutes, is_active) VALUES
('Классический массаж', 'Расслабляющий массаж всего тела', 150000.00, 60, true),
('Спортивный массаж', 'Массаж для восстановления после тренировок', 180000.00, 60, true),
('Массаж спины', 'Массаж спины и шейно-воротниковой зоны', 100000.00, 30, true),
('Антицеллюлитный массаж', 'Массаж проблемных зон', 200000.00, 45, true);
```

---

## Критерии приёмки

- [ ] Таблица `services` создана и содержит начальные данные
- [ ] Таблица `orders` расширена полями `service_id`, `address_text`, `scheduled_at`
- [ ] API endpoint `GET /services` возвращает список активных услуг
- [ ] API endpoint `POST /orders` принимает `service_id` и `address_text`
- [ ] CLI утилита позволяет управлять услугами
- [ ] Написаны тесты для новых endpoints
- [ ] Документация `database-schema-mvp.md` обновлена

---

## Файлы для изменения

| Файл | Действие |
|------|----------|
| `alembic/versions/xxx_add_services_table.py` | Создать |
| `alembic/versions/xxx_extend_orders_table.py` | Создать |
| `src/nms/models/db_models.py` | Изменить |
| `src/nms/models/service.py` | Создать |
| `src/nms/models/order.py` | Изменить |
| `src/nms/models/__init__.py` | Изменить |
| `src/nms/api/services.py` | Создать |
| `src/nms/main.py` | Изменить (подключить router) |
| `scripts/db_cli.py` | Изменить |
| `tests/test_services.py` | Создать |
| `docs/database-schema-mvp.md` | Изменить |

---

## Порядок выполнения

1. Создать миграцию для таблицы `services`
2. Создать миграцию для расширения `orders`
3. Обновить SQLAlchemy модели
4. Создать Pydantic модели для services
5. Создать API router для services
6. Подключить router в main.py
7. Добавить seed данные
8. Обновить CLI утилиту
9. Написать тесты
10. Обновить документацию

---

## Следующий этап (MVP+)

После завершения текущего этапа планируется:

| Таблица | Назначение |
|---------|------------|
| `tariffs` | Варианты тарифов для одной услуги (30/60/90 мин) |
| `order_items` | Несколько услуг в одном заказе |
| `addresses` | Сохранённые адреса пользователя |
| `order_addresses` | Копия адреса на момент создания заказа |

Это позволит:
- Разделить услугу и её тарифы (гибкость)
- Добавлять несколько услуг в один заказ
- Сохранять адреса пользователей для повторного использования
