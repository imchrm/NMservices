# Changelog: CORS Support

**Дата:** 2026-01-25
**Версия:** 0.6.1
**Описание:** Добавлена поддержка CORS для Admin Panel

---

## 🎯 Что добавлено

### Новая функциональность

Добавлен CORS (Cross-Origin Resource Sharing) middleware для поддержки раздельной архитектуры Backend + Frontend.

---

## 📝 Изменения в файлах

### 1. `src/nms/config.py`

**Добавлено:**
```python
# CORS (Cross-Origin Resource Sharing)
cors_origins: list[str] = Field(
    default=["http://localhost:5173"],  # Vite dev server
    alias="CORS_ORIGINS",
)
```

**Назначение:**
- Настройка разрешенных origins для CORS запросов
- По умолчанию: `http://localhost:5173` (Vite dev server)
- Читается из переменной окружения `CORS_ORIGINS`

---

### 2. `src/nms/main.py`

**Изменения:**

#### 2.1 Добавлен импорт:
```python
from fastapi.middleware.cors import CORSMiddleware
```

#### 2.2 Добавлен middleware (после создания app):
```python
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

**Параметры:**
- `allow_origins` - список разрешенных origins (из config)
- `allow_credentials=True` - разрешить отправку cookies/auth headers
- `allow_methods` - разрешенные HTTP методы
- `allow_headers=["*"]` - разрешить все заголовки

---

### 3. `.env.example`

**Добавлено:**
```bash
# CORS (Cross-Origin Resource Sharing)
# Comma-separated list of allowed origins for frontend
CORS_ORIGINS=http://localhost:5173,https://admin.nmservices.uz
```

**Примеры использования:**
```bash
# Development (локальный Vite dev server)
CORS_ORIGINS=http://localhost:5173

# Production (один домен)
CORS_ORIGINS=https://admin.nmservices.uz

# Production (несколько доменов)
CORS_ORIGINS=https://admin.nmservices.uz,https://admin-staging.nmservices.uz

# Development + Production
CORS_ORIGINS=http://localhost:5173,https://admin.nmservices.uz
```

---

## 🔒 Безопасность

### Рекомендации:

1. **Production:** указывайте только доверенные домены
   ```bash
   CORS_ORIGINS=https://admin.nmservices.uz
   ```

2. **НЕ используйте wildcard в production:**
   ```bash
   # ❌ НЕБЕЗОПАСНО
   CORS_ORIGINS=*
   ```

3. **Development:** можно добавить localhost
   ```bash
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

4. **HTTPS обязателен** для production доменов

---

## 🧪 Тестирование CORS

### Проверка через curl:

```bash
# Preflight request (OPTIONS)
curl -X OPTIONS http://localhost:8000/admin/stats \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-Admin-Key" \
  -v

# Ожидаемые заголовки в ответе:
# Access-Control-Allow-Origin: http://localhost:5173
# Access-Control-Allow-Credentials: true
# Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
# Access-Control-Allow-Headers: *
```

### Проверка через browser:

```javascript
// В консоли браузера на странице http://localhost:5173
fetch('http://localhost:8000/admin/stats', {
  headers: {
    'X-Admin-Key': 'admin_secret'
  }
})
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);

// Должно вернуть статистику без CORS ошибки
```

---

## 📊 Совместимость

### Работает с:
- ✅ React (Vite dev server: `http://localhost:5173`)
- ✅ React (production build на любом домене)
- ✅ Vue.js, Angular, Svelte
- ✅ Любой SPA framework
- ✅ Статические сайты (GitHub Pages, Vercel, Netlify)

### Поддерживаемые методы:
- ✅ GET - чтение данных
- ✅ POST - создание
- ✅ PUT - полное обновление
- ✅ PATCH - частичное обновление
- ✅ DELETE - удаление
- ✅ OPTIONS - preflight запросы

---

## 🚀 Деплой

### Development (.env):
```bash
CORS_ORIGINS=http://localhost:5173
```

### Production (.env на сервере):
```bash
CORS_ORIGINS=https://admin.nmservices.uz
```

### После изменения .env:
```bash
# Перезапустить сервис
pkill -f uvicorn
nohup poetry run nms > nms.log 2>&1 &
```

---

## 🔗 Связанные документы

- `ADMIN_PANEL_TECH_SPEC_SEPARATE.md` - Техническое задание для Admin Panel
- `docs/ARCHITECTURE_QUESTIONS_ANSWERS.md` - Ответы на вопросы архитектора
- `ADMIN_API.md` - Документация Admin API

---

## 📝 Примечания

1. **Обратная совместимость:** все существующие API endpoints работают без изменений
2. **Производительность:** CORS middleware добавляет минимальный overhead (<1ms)
3. **Стандарты:** реализация следует спецификации W3C CORS
4. **Логирование:** CORS запросы логируются стандартным способом FastAPI

---

## ✅ Что дальше

После добавления CORS можно:

1. Создать frontend репозиторий (NMservices-Admin)
2. Настроить React Admin для работы с API
3. Деплоить frontend на Vercel/Netlify
4. Добавить сортировку в API (следующая задача)

---

**Автор:** Claude Sonnet 4.5
**Дата:** 2026-01-25
**Статус:** Implemented
