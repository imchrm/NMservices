# Схема базы данных NMServices (MVP)

## Обзор

Данный документ описывает минимальный набор таблиц для MVP (Minimum Viable Product) проекта NMServices - системы управления заказами услуг.

## Диаграмма связей

```
users (1) ----< (N) orders
services (1) ----< (N) orders
users (1) ----< (N) addresses       [MVP+]
orders (1) ----< (N) order_items    [MVP+]
orders (1) ----(1) order_addresses  [MVP+]
services (1) ----< (N) order_items  [MVP+]
```

**Примечание:** Таблицы с пометкой `[MVP+]` будут реализованы в следующем этапе.

## Таблицы

### 1. users (пользователи)

Хранит информацию о зарегистрированных пользователях системы.

**Поля:**

| Название | Тип | Ограничения | Описание |
|----------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор пользователя |
| `phone_number` | VARCHAR(20) | UNIQUE NOT NULL | Номер телефона (используется для авторизации) |
| `telegram_id` | BIGINT | UNIQUE | Telegram ID пользователя |
| `language_code` | VARCHAR(5) | - | Код языка интерфейса (`ru`, `uz`, `en`) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время регистрации |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время последнего обновления |

**Допустимые значения `language_code`:**
- `ru` - Русский
- `uz` - Узбекский
- `en` - English

**Индексы:**
- `idx_users_phone_number` на поле `phone_number`
- `ix_users_telegram_id` на поле `telegram_id` (UNIQUE)

**Особенности:**
- Автоматическое обновление `updated_at` через триггер
- Номер телефона является уникальным идентификатором пользователя
- `telegram_id` позволяет связать пользователя с Telegram-аккаунтом
- `language_code` сохраняет предпочтительный язык пользователя между сессиями

---

### 2. orders (заказы)

Основная таблица для хранения заказов пользователей.

**Поля:**

| Название | Тип | Ограничения | Описание |
|----------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор заказа |
| `user_id` | INTEGER | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | Ссылка на пользователя |
| `service_id` | INTEGER | REFERENCES services(id) ON DELETE SET NULL | Ссылка на услугу |
| `status` | VARCHAR(50) | NOT NULL, DEFAULT 'pending' | Статус заказа |
| `total_amount` | DECIMAL(10, 2) | - | Общая сумма заказа (копируется из услуги при создании) |
| `address_text` | TEXT | - | Адрес выполнения услуги |
| `scheduled_at` | TIMESTAMP | - | Запланированное время выполнения |
| `notes` | TEXT | - | Дополнительные примечания к заказу |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время создания заказа |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время последнего обновления |

**Возможные значения `status`:**
- `pending` - ожидает подтверждения
- `confirmed` - подтвержден
- `in_progress` - в процессе выполнения
- `completed` - завершен
- `cancelled` - отменен

**Индексы:**
- `idx_orders_user_id` на поле `user_id`
- `idx_orders_service_id` на поле `service_id`
- `idx_orders_status` на поле `status`
- `idx_orders_created_at` на поле `created_at`

**Особенности:**
- При удалении пользователя все его заказы также удаляются (CASCADE)
- При удалении услуги `service_id` устанавливается в NULL (SET NULL)
- `total_amount` копируется из `services.base_price` при создании заказа
- Автоматическое обновление `updated_at` через триггер

---

### 3. services (услуги)

Каталог доступных услуг (массаж, уборка и т.д.).

**Поля:**

| Название | Тип | Ограничения | Описание |
|----------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор услуги |
| `name` | VARCHAR(255) | NOT NULL | Название услуги |
| `description` | TEXT | - | Подробное описание услуги |
| `base_price` | DECIMAL(10, 2) | - | Базовая цена услуги |
| `duration_minutes` | INTEGER | - | Ожидаемая длительность выполнения (в минутах) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Активна ли услуга (доступна для заказа) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время создания записи |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время последнего обновления |

**Индексы:**
- `idx_services_is_active` на поле `is_active`

**Особенности:**
- Неактивные услуги (`is_active = false`) не отображаются пользователям
- Автоматическое обновление `updated_at` через триггер

---

### 4. order_items (позиции заказа)

Связывает заказы с услугами. Один заказ может содержать несколько услуг.

**Поля:**

| Название | Тип | Ограничения | Описание |
|----------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор позиции |
| `order_id` | INTEGER | NOT NULL, REFERENCES orders(id) ON DELETE CASCADE | Ссылка на заказ |
| `service_id` | INTEGER | NOT NULL, REFERENCES services(id) ON DELETE RESTRICT | Ссылка на услугу |
| `quantity` | INTEGER | NOT NULL, DEFAULT 1 | Количество единиц услуги |
| `price` | DECIMAL(10, 2) | NOT NULL | Цена услуги на момент создания заказа |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время добавления позиции |

**Индексы:**
- `idx_order_items_order_id` на поле `order_id`
- `idx_order_items_service_id` на поле `service_id`

**Особенности:**
- При удалении заказа все его позиции также удаляются (CASCADE)
- При попытке удалить услугу, на которую есть ссылки, удаление будет запрещено (RESTRICT)
- Цена сохраняется на момент заказа, чтобы изменения базовой цены услуги не влияли на старые заказы

---

### 5. addresses (адреса)

Адреса пользователей для доставки/выполнения услуг.

**Поля:**

| Название | Тип | Ограничения | Описание |
|----------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор адреса |
| `user_id` | INTEGER | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | Ссылка на пользователя |
| `address_line1` | VARCHAR(255) | NOT NULL | Основная строка адреса |
| `address_line2` | VARCHAR(255) | - | Дополнительная строка адреса (квартира, офис) |
| `city` | VARCHAR(100) | NOT NULL | Город |
| `postal_code` | VARCHAR(20) | - | Почтовый индекс |
| `country` | VARCHAR(100) | DEFAULT 'Узбекистан' | Страна |
| `latitude` | DECIMAL(10, 8) | - | Широта (для геолокации) |
| `longitude` | DECIMAL(11, 8) | - | Долгота (для геолокации) |
| `is_default` | BOOLEAN | DEFAULT false | Является ли адрес по умолчанию |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время создания записи |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время последнего обновления |

**Индексы:**
- `idx_addresses_user_id` на поле `user_id`

**Особенности:**
- Пользователь может иметь несколько сохраненных адресов
- Координаты (`latitude`, `longitude`) могут использоваться для расчета расстояния и стоимости доставки
- Автоматическое обновление `updated_at` через триггер

---

### 6. order_addresses (адреса заказов)

Хранит копию адреса на момент создания заказа. Необходима для сохранения исторических данных.

**Поля:**

| Название | Тип | Ограничения | Описание |
|----------|-----|-------------|----------|
| `id` | SERIAL | PRIMARY KEY | Уникальный идентификатор |
| `order_id` | INTEGER | NOT NULL, REFERENCES orders(id) ON DELETE CASCADE | Ссылка на заказ |
| `address_line1` | VARCHAR(255) | NOT NULL | Основная строка адреса |
| `address_line2` | VARCHAR(255) | - | Дополнительная строка адреса |
| `city` | VARCHAR(100) | NOT NULL | Город |
| `postal_code` | VARCHAR(20) | - | Почтовый индекс |
| `latitude` | DECIMAL(10, 8) | - | Широта |
| `longitude` | DECIMAL(11, 8) | - | Долгота |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время создания записи |

**Индексы:**
- `idx_order_addresses_order_id` на поле `order_id`

**Особенности:**
- Адрес копируется из таблицы `addresses` при создании заказа
- Если пользователь изменит или удалит свой адрес, это не повлияет на старые заказы
- Связь один-к-одному с таблицей `orders`

---

## Типовые запросы

### Получить все заказы пользователя

```sql
SELECT
    o.id,
    o.status,
    o.total_amount,
    o.created_at,
    oa.address_line1,
    oa.city
FROM orders o
LEFT JOIN order_addresses oa ON o.id = oa.order_id
WHERE o.user_id = ?
ORDER BY o.created_at DESC;
```

### Получить детали заказа со всеми услугами

```sql
SELECT
    o.id AS order_id,
    o.status,
    o.total_amount,
    s.name AS service_name,
    oi.quantity,
    oi.price,
    oi.quantity * oi.price AS item_total
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN services s ON oi.service_id = s.id
WHERE o.id = ?;
```

### Получить список активных услуг

```sql
SELECT
    id,
    name,
    description,
    base_price,
    duration_minutes
FROM services
WHERE is_active = true
ORDER BY name;
```

### Получить адреса пользователя

```sql
SELECT
    id,
    address_line1,
    address_line2,
    city,
    is_default
FROM addresses
WHERE user_id = ?
ORDER BY is_default DESC, created_at DESC;
```

---

## Бизнес-логика и ограничения

### Создание заказа

1. Пользователь выбирает услуги из каталога `services`
2. Создается запись в таблице `orders` со статусом `pending`
3. Для каждой выбранной услуги создается запись в `order_items` с текущей ценой
4. Адрес пользователя копируется в `order_addresses`
5. Рассчитывается `total_amount` как сумма всех позиций заказа

### Изменение статуса заказа

Переходы статусов:
```
pending → confirmed → in_progress → completed
   ↓
cancelled
```

- Из статуса `cancelled` или `completed` нельзя перейти в другие статусы
- При изменении статуса обновляется поле `updated_at`

### Удаление данных

- **Удаление пользователя**: удаляются все связанные заказы и адреса (CASCADE)
- **Удаление заказа**: удаляются все позиции заказа и адрес заказа (CASCADE)
- **Удаление услуги**: запрещено, если есть связанные позиции заказов (RESTRICT)
- **Решение**: вместо удаления услуги устанавливайте `is_active = false`

---

## Следующие шаги

После реализации MVP можно добавить дополнительные таблицы:

- **employees** - сотрудники, выполняющие услуги
- **order_assignments** - назначение заказов сотрудникам
- **payments** - история платежей
- **reviews** - отзывы пользователей
- **schedules** - планирование услуг на определенное время
- **notifications** - уведомления пользователей

---

## Ссылки

- [Скрипт инициализации БД](../scripts/init_db.sql)
- [Инструкция по развертыванию PostgreSQL](./postgresql-deployment.md)
