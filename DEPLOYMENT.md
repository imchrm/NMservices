# Deployment Guide for NMservices

## После обновления кода на Linux-машине (192.168.1.191)

### 1. Остановить текущий сервис
```bash
# Найти процесс uvicorn/NMservices
ps aux | grep uvicorn
# или
ps aux | grep nms

# Остановить (замените PID на реальный ID процесса)
kill <PID>
```

### 2. Перейти в директорию проекта
```bash
cd /path/to/NMservices
```

### 3. Обновить код из git
```bash
git pull origin pensive-joliot
```

### 4. Установить зависимости (если обновились)
```bash
poetry install
```

### 5. Запустить сервис
```bash
# Вариант 1: через poetry
poetry run nms

# Вариант 2: напрямую через uvicorn
poetry run uvicorn nms.main:app --host 0.0.0.0 --port 8000

# Вариант 3: в фоновом режиме с логами
nohup poetry run nms > nms.log 2>&1 &
```

### 6. Проверить запуск
```bash
# Health check
curl http://localhost:8000/

# Проверить создание заказа (user_id=6 должен существовать!)
curl -X POST \
  -H "X-API-Key: troxivasine23" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 6, "tariff_code": "standard_300"}' \
  http://localhost:8000/create_order
```

### 7. Проверить запись в БД
```bash
# Подключиться к PostgreSQL
psql -U postgres -d nomus

# Проверить таблицу orders
SELECT * FROM orders ORDER BY id DESC LIMIT 5;
```

## Важно!

### Проверка пользователей
Перед созданием заказа убедитесь, что пользователь существует:
```sql
SELECT id, phone_number FROM users WHERE id = 6;
```

Если пользователя нет, создайте его через API:
```bash
curl -X POST \
  -H "X-API-Key: troxivasine23" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+998901234567"}' \
  http://localhost:8000/users/register
```

## Логирование

Сервис использует стандартное логирование Python:
- `[DB]` - операции с базой данных
- `[PAYMENT-STUB]` - заглушка платежного шлюза
- `[NOTIFY-STUB]` - заглушка системы уведомлений

Просмотр логов:
```bash
# Если запущен через nohup
tail -f nms.log

# Если запущен как systemd service
journalctl -u nms -f
```

## Endpoints

### Legacy endpoint (deprecated)
```bash
POST /create_order
```

### New endpoint (recommended)
```bash
POST /orders
```

Оба эндпоинта работают одинаково и теперь реально сохраняют данные в БД.

## Troubleshooting

### Ошибка "User with ID X does not exist"
Пользователь не существует в таблице `users`. Создайте его через `/users/register` или `/register`.

### Ошибка подключения к БД
Проверьте `.env` файл и `DATABASE_URL`:
```bash
cat .env | grep DATABASE_URL
```

### Заказ не появляется в таблице
1. Проверьте, что сервис перезапущен после обновления кода
2. Проверьте логи на наличие ошибок
3. Убедитесь, что используете правильный API ключ
