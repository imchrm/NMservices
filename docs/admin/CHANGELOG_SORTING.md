# Changelog: Sorting Support for Admin API

**Дата:** 2026-01-25
**Версия:** 0.6.2
**Описание:** Добавлена поддержка сортировки для Admin API endpoints

---

## 🎯 Что добавлено

### Новая функциональность

Добавлена динамическая сортировка для Admin API endpoints `GET /admin/users` и `GET /admin/orders`.

Теперь можно сортировать данные по любому полю и в любом порядке (ascending/descending).

---

## 📝 Изменения в файлах

### 1. `src/nms/api/admin/users.py`

**Добавлено:**

#### Импорты:
```python
from typing import Literal
from fastapi import Query
```

#### Новые параметры в `list_users`:
```python
@router.get("", response_model=AdminUserListResponse, dependencies=[Depends(get_admin_key)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    sort_by: Literal["id", "phone_number", "created_at", "updated_at"] = Query(
        default="id",
        description="Field to sort by"
    ),
    order: Literal["asc", "desc"] = Query(
        default="asc",
        description="Sort order (ascending or descending)"
    ),
    db: AsyncSession = Depends(get_db)
):
```

#### Логика сортировки:
```python
# Map sort_by to actual column
sort_columns = {
    "id": User.id,
    "phone_number": User.phone_number,
    "created_at": User.created_at,
    "updated_at": User.updated_at,
}

sort_column = sort_columns[sort_by]

# Apply sort order
if order == "desc":
    order_clause = sort_column.desc()
else:
    order_clause = sort_column.asc()

# Get users with sorting
result = await db.execute(
    select(User)
    .order_by(order_clause)
    .offset(skip)
    .limit(limit)
)
```

**Поддерживаемые поля для сортировки:**
- `id` - ID пользователя
- `phone_number` - Номер телефона
- `created_at` - Дата создания
- `updated_at` - Дата последнего обновления

---

### 2. `src/nms/api/admin/orders.py`

**Добавлено:**

#### Импорты:
```python
from typing import Literal
from fastapi import Query
```

#### Новые параметры в `list_orders`:
```python
@router.get("", response_model=AdminOrderListResponse, dependencies=[Depends(get_admin_key)])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = Query(
        default=None,
        description="Filter by order status (e.g., 'pending', 'completed')"
    ),
    sort_by: Literal["id", "user_id", "status", "total_amount", "created_at", "updated_at"] = Query(
        default="created_at",
        description="Field to sort by"
    ),
    order: Literal["asc", "desc"] = Query(
        default="desc",
        description="Sort order (ascending or descending)"
    ),
    db: AsyncSession = Depends(get_db)
):
```

#### Логика сортировки:
```python
# Map sort_by to actual column
sort_columns = {
    "id": Order.id,
    "user_id": Order.user_id,
    "status": Order.status,
    "total_amount": Order.total_amount,
    "created_at": Order.created_at,
    "updated_at": Order.updated_at,
}

sort_column = sort_columns[sort_by]

# Apply sort order
if order == "desc":
    order_clause = sort_column.desc()
else:
    order_clause = sort_column.asc()

# Build query with sorting
query = select(Order).order_by(order_clause)
```

**Поддерживаемые поля для сортировки:**
- `id` - ID заказа
- `user_id` - ID пользователя
- `status` - Статус заказа
- `total_amount` - Сумма заказа
- `created_at` - Дата создания (по умолчанию)
- `updated_at` - Дата последнего обновления

---

## 🚀 Использование

### Users

#### Сортировка по ID (по умолчанию, ascending):
```bash
GET /admin/users
GET /admin/users?sort_by=id&order=asc
```

#### Сортировка по дате создания (descending):
```bash
GET /admin/users?sort_by=created_at&order=desc
```

#### Сортировка по номеру телефона:
```bash
GET /admin/users?sort_by=phone_number&order=asc
```

#### С пагинацией:
```bash
GET /admin/users?skip=0&limit=25&sort_by=created_at&order=desc
```

---

### Orders

#### Сортировка по дате создания (по умолчанию, descending):
```bash
GET /admin/orders
GET /admin/orders?sort_by=created_at&order=desc
```

#### Сортировка по сумме (ascending):
```bash
GET /admin/orders?sort_by=total_amount&order=asc
```

#### Сортировка по статусу с фильтром:
```bash
GET /admin/orders?status_filter=pending&sort_by=created_at&order=desc
```

#### Сортировка по user_id:
```bash
GET /admin/orders?sort_by=user_id&order=asc
```

---

## 🧪 Примеры с curl

### Users

```bash
# Все пользователи, сортировка по дате (новые первые)
curl -H "X-Admin-Key: admin_secret" \
  "http://localhost:8000/admin/users?sort_by=created_at&order=desc"

# Первые 10 пользователей, сортировка по phone_number
curl -H "X-Admin-Key: admin_secret" \
  "http://localhost:8000/admin/users?skip=0&limit=10&sort_by=phone_number&order=asc"
```

### Orders

```bash
# Все заказы, сортировка по сумме (от большей к меньшей)
curl -H "X-Admin-Key: admin_secret" \
  "http://localhost:8000/admin/orders?sort_by=total_amount&order=desc"

# Pending заказы, сортировка по дате
curl -H "X-Admin-Key: admin_secret" \
  "http://localhost:8000/admin/orders?status_filter=pending&sort_by=created_at&order=desc"

# Сортировка по ID пользователя
curl -H "X-Admin-Key: admin_secret" \
  "http://localhost:8000/admin/orders?sort_by=user_id&order=asc"
```

---

## 💡 React Admin интеграция

С добавленной сортировкой React Admin будет работать "из коробки":

```typescript
// src/providers/dataProvider.ts
export const dataProvider: DataProvider = {
  getList: (resource, params) => {
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;

    const skip = (page - 1) * perPage;
    const limit = perPage;

    const url = `${API_URL}/${resource}?` +
      `skip=${skip}&` +
      `limit=${limit}&` +
      `sort_by=${field}&` +
      `order=${order.toLowerCase()}`;

    return httpClient(url).then(({ json }) => {
      const dataKey = resource.includes('users') ? 'users' : 'orders';
      return {
        data: json[dataKey] || [],
        total: json.total || 0,
      };
    });
  },
  // ... other methods
};
```

**Теперь в UI можно кликать на заголовки таблиц для сортировки!** ✅

---

## 📊 API Swagger Documentation

После этих изменений Swagger UI (`/docs`) автоматически покажет новые параметры:

**GET /admin/users:**
- `skip` (integer, default: 0)
- `limit` (integer, default: 100)
- `sort_by` (enum: id, phone_number, created_at, updated_at, default: id)
- `order` (enum: asc, desc, default: asc)

**GET /admin/orders:**
- `skip` (integer, default: 0)
- `limit` (integer, default: 100)
- `status_filter` (string, optional)
- `sort_by` (enum: id, user_id, status, total_amount, created_at, updated_at, default: created_at)
- `order` (enum: asc, desc, default: desc)

---

## 🔒 Безопасность

### Защита от SQL Injection

Используется **параметризованная сортировка** с маппингом:

```python
# ✅ Безопасно - используется whitelist
sort_columns = {
    "id": User.id,
    "phone_number": User.phone_number,
    # ...
}

sort_column = sort_columns[sort_by]  # sort_by ограничен Literal
```

### Валидация входных данных

- `sort_by` - ограничен `Literal` (только разрешенные значения)
- `order` - ограничен `Literal["asc", "desc"]`
- Невалидные значения вернут **422 Unprocessable Entity**

---

## ⚡ Производительность

### Индексы БД

Для оптимальной производительности убедитесь что в БД есть индексы:

```sql
-- Users
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_phone_number ON users(phone_number);

-- Orders
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_total_amount ON orders(total_amount);
```

**Большинство индексов уже созданы** через SQLAlchemy модели (`index=True`).

---

## 🐛 Troubleshooting

### Проблема: Сортировка не работает

**Симптом:**
```bash
GET /admin/users?sort_by=created_at&order=desc
# Возвращает данные не отсортированными
```

**Решение:**
1. Проверить что backend обновлен (перезапустить сервис)
2. Проверить логи backend на ошибки
3. Убедиться что параметры передаются правильно

### Проблема: 422 Unprocessable Entity

**Симптом:**
```bash
GET /admin/users?sort_by=email&order=desc
# 422 Error
```

**Причина:** `email` не в списке разрешенных полей

**Решение:** Использовать только разрешенные поля:
- Users: `id`, `phone_number`, `created_at`, `updated_at`
- Orders: `id`, `user_id`, `status`, `total_amount`, `created_at`, `updated_at`

---

## 📋 Обратная совместимость

### ✅ Полная обратная совместимость

Старые запросы **продолжают работать** без изменений:

```bash
# Работало раньше - работает сейчас (с дефолтной сортировкой)
GET /admin/users
GET /admin/orders
GET /admin/orders?status_filter=pending
```

**По умолчанию:**
- Users: сортировка по `id` (asc)
- Orders: сортировка по `created_at` (desc)

---

## 🔗 Связанные изменения

- [CHANGELOG_CORS.md](./CHANGELOG_CORS.md) - CORS middleware
- [ADMIN_API.md](./ADMIN_API.md) - Admin API документация
- [docs/ARCHITECTURE_QUESTIONS_ANSWERS.md](./docs/ARCHITECTURE_QUESTIONS_ANSWERS.md) - Вопрос 1

---

## ✅ Что дальше

После добавления сортировки:

1. ✅ Backend полностью готов для Admin Panel
2. ✅ Можно создавать React Admin frontend
3. ✅ Все основные вопросы архитектора решены
4. 🔜 Опционально: добавить дополнительные фильтры (user_id, amount range)

---

**Автор:** Claude Sonnet 4.5
**Дата:** 2026-01-25
**Статус:** Implemented
