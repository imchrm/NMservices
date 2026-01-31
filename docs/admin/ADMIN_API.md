# Admin API Documentation

## Overview

Admin API provides remote database administration capabilities for NMservices. All admin endpoints require authentication via `X-Admin-Key` header.

## Authentication

All admin endpoints require the `X-Admin-Key` header:

```bash
curl -H "X-Admin-Key: your_admin_secret_key" http://localhost:8000/admin/users
```

Set `ADMIN_SECRET_KEY` in your `.env` file.

## Endpoints

### User Management

#### List All Users
```bash
GET /admin/users?skip=0&limit=100&sort_by=created_at&order=desc
```

**Query Parameters:**
- `skip` (integer, default: 0) - Number of records to skip
- `limit` (integer, default: 100) - Number of records to return
- `sort_by` (string, default: "id") - Field to sort by: `id`, `phone_number`, `created_at`, `updated_at`
- `order` (string, default: "asc") - Sort order: `asc` or `desc`

Response:
```json
{
  "users": [
    {
      "id": 1,
      "phone_number": "+998901234567",
      "created_at": "2024-01-24T10:00:00",
      "updated_at": "2024-01-24T10:00:00"
    }
  ],
  "total": 1
}
```

> **Note:** Although the user model in the database has a `telegram_id` field, the current Admin API response model `AdminUserResponse` does not include it yet.

#### Create User
```bash
POST /admin/users
Content-Type: application/json

{
  "phone_number": "+998901234567"
}
```

Response:
```json
{
  "id": 1,
  "phone_number": "+998901234567",
  "created_at": "2024-01-24T10:00:00",
  "updated_at": "2024-01-24T10:00:00"
}
```

#### Get User by ID
```bash
GET /admin/users/{user_id}
```

#### Delete User by ID
```bash
DELETE /admin/users/{user_id}
```

Deletes user and all their orders (CASCADE).

Response:
```json
{
  "status": "ok",
  "message": "User 1 deleted",
  "orders_deleted": 5
}
```

#### Get User's Orders
```bash
GET /admin/users/{user_id}/orders
```

### Order Management

#### List All Orders
```bash
GET /admin/orders?skip=0&limit=100&status_filter=pending&sort_by=created_at&order=desc
```

**Query Parameters:**
- `skip` (integer, default: 0) - Number of records to skip
- `limit` (integer, default: 100) - Number of records to return
- `status_filter` (string, optional) - Filter by status: `pending`, `completed`, etc.
- `sort_by` (string, default: "created_at") - Field to sort by: `id`, `user_id`, `status`, `total_amount`, `created_at`, `updated_at`
- `order` (string, default: "desc") - Sort order: `asc` or `desc`

Response:
```json
{
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "status": "pending",
      "total_amount": "300.00",
      "notes": "Tariff: standard_300",
      "created_at": "2024-01-24T10:00:00",
      "updated_at": "2024-01-24T10:00:00"
    }
  ],
  "total": 1
}
```

#### Create Order
```bash
POST /admin/orders
Content-Type: application/json

{
  "user_id": 1,
  "status": "pending",
  "total_amount": 300.00,
  "notes": "Test order"
}
```

#### Get Order by ID
```bash
GET /admin/orders/{order_id}
```

Returns order with user details:
```json
{
  "id": 1,
  "user_id": 1,
  "status": "pending",
  "total_amount": "300.00",
  "notes": "Tariff: standard_300",
  "created_at": "2024-01-24T10:00:00",
  "updated_at": "2024-01-24T10:00:00",
  "user": {
    "id": 1,
    "phone_number": "+998901234567",
    "created_at": "2024-01-24T10:00:00",
    "updated_at": "2024-01-24T10:00:00"
  }
}
```

#### Update Order
```bash
PATCH /admin/orders/{order_id}
Content-Type: application/json

{
  "status": "completed",
  "total_amount": 350.00,
  "notes": "Updated notes"
}
```

All fields are optional.

#### Delete Order
```bash
DELETE /admin/orders/{order_id}
```

### Statistics

#### Get Database Statistics
```bash
GET /admin/stats
```

Response:
```json
{
  "total_users": 10,
  "total_orders": 25,
  "orders_by_status": {
    "pending": 15,
    "completed": 8,
    "cancelled": 2
  }
}
```

## Example Usage

### List users
```bash
curl -H "X-Admin-Key: admin_secret" http://localhost:8000/admin/users
```

### Create a user
```bash
curl -X POST \
  -H "X-Admin-Key: admin_secret" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+998901234567"}' \
  http://localhost:8000/admin/users
```

### Delete user
```bash
curl -X DELETE \
  -H "X-Admin-Key: admin_secret" \
  http://localhost:8000/admin/users/1
```

### List orders with status filter
```bash
curl -H "X-Admin-Key: admin_secret" \
  "http://localhost:8000/admin/orders?status_filter=pending&limit=10"
```

### Update order status
```bash
curl -X PATCH \
  -H "X-Admin-Key: admin_secret" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}' \
  http://localhost:8000/admin/orders/1
```

### Get statistics
```bash
curl -H "X-Admin-Key: admin_secret" http://localhost:8000/admin/stats
```

## Comparison with db_cli.py

The Admin API mirrors the functionality of `scripts/db_cli.py`:

| db_cli.py | Admin API |
|-----------|-----------|
| 1a - показать всех пользователей | GET /admin/users |
| 1b - показать всех с заказами | GET /admin/users + GET /admin/users/{id}/orders |
| 1c - создать нового | POST /admin/users |
| 1d - удалить по ID | DELETE /admin/users/{id} |
| 2a - показать все заказы | GET /admin/orders |
| 2b - создать новый | POST /admin/orders |
| 2c - обновить | PATCH /admin/orders/{id} |
| 2d - удалить по ID | DELETE /admin/orders/{id} |

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

You can test all admin endpoints directly from the Swagger UI by clicking "Authorize" and entering your admin key.
