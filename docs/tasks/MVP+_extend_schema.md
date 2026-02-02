# Техническое задание: MVP+ — Расширение схемы БД

## Контекст

Это **третий этап разработки (MVP+)**:

| Этап | Название | Статус |
|------|----------|--------|
| 1 | MVP-0 (базовый) | ✅ Готово |
| 2 | MVP | ✅ Готово |
| 3 | **MVP+** (текущий) | 📋 Планируется |

---

## Цель

Расширить схему БД для поддержки:
- Гибких тарифов для услуг
- Нескольких услуг в одном заказе
- Сохранённых адресов пользователей
- Истории адресов в заказах

---

## Текущее состояние (после MVP)

**Реализовано:**
- Таблица `users` (id, phone_number, telegram_id, language_code, created_at, updated_at)
- Таблица `orders` (id, user_id, service_id, status, total_amount, address_text, scheduled_at, notes, created_at, updated_at)
- Таблица `services` (id, name, description, base_price, duration_minutes, is_active, created_at, updated_at)
- API endpoints для пользователей, заказов, услуг
- CLI утилита `scripts/db_cli.py`

**Ограничения текущей реализации:**
- Одна услуга = один тариф (нет вариаций 30/60/90 мин)
- Один заказ = одна услуга
- Адрес хранится как текст, не переиспользуется
- При изменении адреса пользователя теряется история

---

## Задачи

### 1. Создать таблицу `tariffs`

Варианты тарифов для каждой услуги.

**Миграция Alembic:**

```sql
CREATE TABLE tariffs (
    id SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    duration_minutes INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tariffs_service_id ON tariffs(service_id);
CREATE INDEX idx_tariffs_code ON tariffs(code);
CREATE INDEX idx_tariffs_is_active ON tariffs(is_active);
```

**Модель SQLAlchemy:** `src/nms/models/db_models.py`

```python
class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    service = relationship("Service", back_populates="tariffs")
```

**Обновить модель Service:**

```python
class Service(Base):
    # ... существующие поля ...
    tariffs = relationship("Tariff", back_populates="service", cascade="all, delete-orphan")
```

**Примеры данных:**

```sql
-- Услуга: Классический массаж (id=1)
INSERT INTO tariffs (service_id, code, name, price, duration_minutes, is_active) VALUES
(1, 'classic_30', '30 минут', 100000.00, 30, true),
(1, 'classic_60', '60 минут', 150000.00, 60, true),
(1, 'classic_90', '90 минут', 200000.00, 90, true);

-- Услуга: Спортивный массаж (id=2)
INSERT INTO tariffs (service_id, code, name, price, duration_minutes, is_active) VALUES
(2, 'sport_60', '60 минут', 180000.00, 60, true),
(2, 'sport_90', '90 минут', 250000.00, 90, true);
```

---

### 2. Создать таблицу `order_items`

Позволяет добавлять несколько услуг/тарифов в один заказ.

**Миграция Alembic:**

```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    tariff_id INTEGER NOT NULL REFERENCES tariffs(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL DEFAULT 1,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_tariff_id ON order_items(tariff_id);
```

**Модель SQLAlchemy:**

```python
class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    tariff_id = Column(Integer, ForeignKey("tariffs.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)  # Цена на момент заказа
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="items")
    tariff = relationship("Tariff")
```

**Особенности:**
- `price` — фиксируется на момент заказа (не зависит от изменений в `tariffs`)
- `ON DELETE RESTRICT` — нельзя удалить тариф, если есть заказы с ним

---

### 3. Создать таблицу `addresses`

Сохранённые адреса пользователей для повторного использования.

**Миграция Alembic:**

```sql
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL DEFAULT 'Ташкент',
    district VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_default BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_addresses_user_id ON addresses(user_id);
```

**Модель SQLAlchemy:**

```python
class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False, default="Ташкент")
    district = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="addresses")
```

---

### 4. Создать таблицу `order_addresses`

Снимок адреса на момент создания заказа.

**Миграция Alembic:**

```sql
CREATE TABLE order_addresses (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE REFERENCES orders(id) ON DELETE CASCADE,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_addresses_order_id ON order_addresses(order_id);
```

**Модель SQLAlchemy:**

```python
class OrderAddress(Base):
    __tablename__ = "order_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="address")
```

**Особенности:**
- Связь один-к-одному с `orders` (UNIQUE на `order_id`)
- Копируется из `addresses` при создании заказа
- Не изменяется при обновлении адреса пользователя

---

### 5. Обновить таблицу `orders`

**Изменения:**
- Удалить `service_id` — заменяется на `order_items`
- Удалить `address_text` — заменяется на `order_addresses`
- Добавить связи с новыми таблицами

**Миграция Alembic:**

```sql
-- После миграции данных в order_items и order_addresses
ALTER TABLE orders DROP COLUMN service_id;
ALTER TABLE orders DROP COLUMN address_text;
```

**Обновить модель Order:**

```python
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending")
    total_amount = Column(Numeric(10, 2), nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    address = relationship("OrderAddress", back_populates="order", uselist=False, cascade="all, delete-orphan")
```

---

### 6. Обновить таблицу `services`

**Изменения:**
- Удалить `base_price` — цена теперь в `tariffs`
- Удалить `duration_minutes` — длительность теперь в `tariffs`
- Добавить связь с `tariffs`

**Миграция Alembic:**

```sql
-- После миграции данных в tariffs
ALTER TABLE services DROP COLUMN base_price;
ALTER TABLE services DROP COLUMN duration_minutes;
```

---

## Схема связей (MVP+)

```
users (1) ──< (N) addresses
  │
  └──< (N) orders (1) ──── (1) order_addresses
                │
                └──< (N) order_items ──> (1) tariffs ──> (1) services
```

---

## Pydantic модели

**Файл:** `src/nms/models/tariff.py`

```python
from pydantic import BaseModel, Field
from decimal import Decimal

class TariffResponse(BaseModel):
    id: int
    service_id: int
    code: str
    name: str
    price: Decimal
    duration_minutes: int | None = None
    is_active: bool

    model_config = {"from_attributes": True}

class TariffCreateRequest(BaseModel):
    service_id: int = Field(..., description="ID услуги")
    code: str = Field(..., description="Уникальный код тарифа")
    name: str = Field(..., description="Название тарифа")
    price: Decimal = Field(..., description="Цена")
    duration_minutes: int | None = Field(None, description="Длительность в минутах")
    is_active: bool = Field(True, description="Активен ли тариф")
```

**Файл:** `src/nms/models/address.py`

```python
from pydantic import BaseModel, Field
from decimal import Decimal

class AddressResponse(BaseModel):
    id: int
    user_id: int
    address_line1: str
    address_line2: str | None = None
    city: str
    district: str | None = None
    is_default: bool

    model_config = {"from_attributes": True}

class AddressCreateRequest(BaseModel):
    address_line1: str = Field(..., description="Основная строка адреса")
    address_line2: str | None = Field(None, description="Дополнительная строка")
    city: str = Field("Ташкент", description="Город")
    district: str | None = Field(None, description="Район")
    latitude: Decimal | None = Field(None, description="Широта")
    longitude: Decimal | None = Field(None, description="Долгота")
    is_default: bool = Field(False, description="Адрес по умолчанию")
```

**Обновить:** `src/nms/models/order.py`

```python
class OrderItemRequest(BaseModel):
    tariff_id: int = Field(..., description="ID тарифа")
    quantity: int = Field(1, description="Количество")

class OrderCreateRequest(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    items: list[OrderItemRequest] = Field(..., description="Позиции заказа")
    address_id: int | None = Field(None, description="ID сохранённого адреса")
    address_text: str | None = Field(None, description="Адрес текстом (если нет сохранённого)")
    scheduled_at: datetime | None = Field(None, description="Запланированное время")
    notes: str | None = Field(None, description="Примечания")
```

---

## API endpoints

### Тарифы

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/services/{service_id}/tariffs` | Список тарифов услуги |
| GET | `/tariffs/{tariff_id}` | Детали тарифа |
| POST | `/tariffs` | Создать тариф (admin) |
| PATCH | `/tariffs/{tariff_id}` | Обновить тариф (admin) |
| DELETE | `/tariffs/{tariff_id}` | Деактивировать тариф (admin) |

### Адреса

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/users/{user_id}/addresses` | Список адресов пользователя |
| POST | `/users/{user_id}/addresses` | Добавить адрес |
| PATCH | `/addresses/{address_id}` | Обновить адрес |
| DELETE | `/addresses/{address_id}` | Удалить адрес |
| POST | `/addresses/{address_id}/set-default` | Установить по умолчанию |

---

## Миграция данных

При переходе с MVP на MVP+ нужна миграция существующих данных:

```python
# Миграция services → tariffs
# Для каждой услуги создать один тариф с текущей ценой

# Миграция orders.service_id → order_items
# Для каждого заказа создать order_item с соответствующим тарифом

# Миграция orders.address_text → order_addresses
# Для каждого заказа создать order_address с текстом адреса
```

---

## Критерии приёмки

- [ ] Таблица `tariffs` создана, связана с `services`
- [ ] Таблица `order_items` создана, связана с `orders` и `tariffs`
- [ ] Таблица `addresses` создана, связана с `users`
- [ ] Таблица `order_addresses` создана, связана с `orders`
- [ ] Существующие данные мигрированы
- [ ] API endpoints для тарифов работают
- [ ] API endpoints для адресов работают
- [ ] Создание заказа работает с новой схемой
- [ ] CLI утилита обновлена
- [ ] Написаны тесты
- [ ] Документация обновлена

---

## Файлы для изменения

| Файл | Действие |
|------|----------|
| `alembic/versions/xxx_add_tariffs_table.py` | Создать |
| `alembic/versions/xxx_add_order_items_table.py` | Создать |
| `alembic/versions/xxx_add_addresses_table.py` | Создать |
| `alembic/versions/xxx_add_order_addresses_table.py` | Создать |
| `alembic/versions/xxx_migrate_data.py` | Создать |
| `alembic/versions/xxx_cleanup_orders_services.py` | Создать |
| `src/nms/models/db_models.py` | Изменить |
| `src/nms/models/tariff.py` | Создать |
| `src/nms/models/address.py` | Создать |
| `src/nms/models/order.py` | Изменить |
| `src/nms/models/__init__.py` | Изменить |
| `src/nms/api/tariffs.py` | Создать |
| `src/nms/api/addresses.py` | Создать |
| `src/nms/api/orders.py` | Изменить |
| `src/nms/main.py` | Изменить |
| `scripts/db_cli.py` | Изменить |
| `tests/test_tariffs.py` | Создать |
| `tests/test_addresses.py` | Создать |
| `docs/database-schema-mvp.md` | Изменить |

---

## Порядок выполнения

1. Создать миграцию для `tariffs`
2. Создать миграцию для `addresses`
3. Создать миграцию для `order_items`
4. Создать миграцию для `order_addresses`
5. Создать миграцию данных (перенос из старых полей)
6. Создать миграцию очистки (удаление старых полей)
7. Обновить SQLAlchemy модели
8. Создать Pydantic модели
9. Создать API routers
10. Обновить логику создания заказа
11. Обновить CLI утилиту
12. Написать тесты
13. Обновить документацию
