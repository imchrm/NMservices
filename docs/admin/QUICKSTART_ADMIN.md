# Quick Start: Admin API

Быстрое руководство по использованию Admin API для удаленного управления базой данных NMservices.

## 🚀 Быстрый старт

### 1. Настройка

Добавьте в `.env` файл на сервере:

```bash
ADMIN_SECRET_KEY=your_secure_admin_key_here
```

### 2. Перезапустите сервис

```bash
# Остановить текущий процесс
pkill -f uvicorn

# Запустить снова
cd /path/to/NMservices
nohup poetry run nms > nms.log 2>&1 &
```

### 3. Проверьте работу

```bash
curl -H "X-Admin-Key: your_secure_admin_key_here" \
  http://127.0.0.1:8000/admin/stats
```

## 📋 Основные операции

### Просмотр статистики

```bash
curl -H "X-Admin-Key: admin_secret" \
  http://127.0.0.1:8000/admin/stats
```

Ответ:
```json
{
  "total_users": 10,
  "total_orders": 25,
  "orders_by_status": {
    "pending": 15,
    "completed": 10
  }
}
```

### Список пользователей

```bash
curl -H "X-Admin-Key: admin_secret" \
  http://127.0.0.1:8000/admin/users
```

### Создать пользователя

```bash
curl -X POST \
  -H "X-Admin-Key: admin_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+998901234567",
    "telegram_id": 123456789,
    "language_code": "ru"
  }' \
  http://127.0.0.1:8000/admin/users
```

### Получить пользователя по ID

```bash
curl -H "X-Admin-Key: admin_secret" \
  http://127.0.0.1:8000/admin/users/1
```

### Получить заказы пользователя

```bash
curl -H "X-Admin-Key: admin_secret" \
  http://127.0.0.1:8000/admin/users/1/orders
```

### Список заказов

```bash
# Все заказы
curl -H "X-Admin-Key: admin_secret" \
  http://127.0.0.1:8000/admin/orders

# Только pending
curl -H "X-Admin-Key: admin_secret" \
  "http://127.0.0.1:8000/admin/orders?status_filter=pending"

# С пагинацией
curl -H "X-Admin-Key: admin_secret" \
  "http://127.0.0.1:8000/admin/orders?skip=0&limit=10"
```

### Создать заказ

```bash
curl -X POST \
  -H "X-Admin-Key: admin_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "status": "pending",
    "total_amount": 300.00,
    "notes": "Manual order"
  }' \
  http://127.0.0.1:8000/admin/orders
```

### Обновить заказ

```bash
curl -X PATCH \
  -H "X-Admin-Key: admin_secret" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed", "total_amount": 350.00}' \
  http://127.0.0.1:8000/admin/orders/1
```

### Удалить заказ

```bash
curl -X DELETE \
  -H "X-Admin-Key: admin_secret" \
  http://127.0.0.1:8000/admin/orders/1
```

### Удалить пользователя (с заказами)

```bash
curl -X DELETE \
  -H "X-Admin-Key: admin_secret" \
  http://127.0.0.1:8000/admin/users/1
```

⚠️ **ВНИМАНИЕ:** Удаление пользователя автоматически удалит все его заказы (CASCADE)!

## 🧪 Автоматическое тестирование

### Python-версия (рекомендуется)

```bash
# На локальной машине
poetry run python scripts/test_admin_api.py http://127.0.0.1:8000 admin_secret
```

Этот скрипт:
- ✅ Создает тестового пользователя
- ✅ Создает тестовый заказ
- ✅ Обновляет заказ
- ✅ Проверяет фильтрацию
- ✅ Удаляет тестовые данные
- ✅ Проверяет статистику

### Bash-версия (Linux/macOS)

```bash
chmod +x scripts/test_admin_api.sh
./scripts/test_admin_api.sh http://127.0.0.1:8000 admin_secret
```

## 📱 Использование из приложений

### Python (httpx)

```python
import httpx

BASE_URL = "http://127.0.0.1:8000"
ADMIN_KEY = "admin_secret"
headers = {"X-Admin-Key": ADMIN_KEY}

async with httpx.AsyncClient() as client:
    # Получить статистику
    response = await client.get(f"{BASE_URL}/admin/stats", headers=headers)
    stats = response.json()
    print(f"Users: {stats['total_users']}, Orders: {stats['total_orders']}")

    # Создать пользователя
    response = await client.post(
        f"{BASE_URL}/admin/users",
        headers=headers,
        json={"phone_number": "+998901234567"}
    )
    user = response.json()
    print(f"Created user ID: {user['id']}")
```

### JavaScript/Node.js (axios)

```javascript
const axios = require('axios');

const BASE_URL = 'http://127.0.0.1:8000';
const ADMIN_KEY = 'admin_secret';

const headers = {
  'X-Admin-Key': ADMIN_KEY,
  'Content-Type': 'application/json'
};

// Получить статистику
const stats = await axios.get(`${BASE_URL}/admin/stats`, { headers });
console.log(`Users: ${stats.data.total_users}, Orders: ${stats.data.total_orders}`);

// Создать пользователя
const user = await axios.post(
  `${BASE_URL}/admin/users`,
  { phone_number: '+998901234567' },
  { headers }
);
console.log(`Created user ID: ${user.data.id}`);
```

## 🔒 Безопасность

1. **Используйте сложный admin ключ:**
   ```bash
   # Генерация сложного ключа (Linux/macOS)
   openssl rand -hex 32

   # Или (Python)
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Ограничьте доступ к Admin API:**
   - Настройте firewall для доступа только с доверенных IP
   - Используйте VPN для доступа к админке
   - Рассмотрите использование HTTPS (reverse proxy через nginx)

3. **Храните ключи безопасно:**
   - Никогда не коммитьте `.env` в git
   - Используйте секреты в CI/CD
   - Регулярно меняйте admin ключ

## 🌐 Swagger UI

Для удобного тестирования через веб-интерфейс:

1. Откройте http://127.0.0.1:8000/docs
2. Нажмите кнопку "Authorize"
3. В поле "X-Admin-Key" введите ваш admin ключ
4. Теперь можно тестировать все admin эндпоинты прямо из браузера!

## 📖 Дополнительная документация

- `ADMIN_API.md` - Полная документация Admin API
- `DEPLOYMENT.md` - Руководство по развертыванию
- `scripts/README.md` - Документация по скриптам
