# CORS Setup - Краткая инструкция

**Дата:** 2026-01-25
**Статус:** ✅ Реализовано

---

## ✅ Что сделано

CORS (Cross-Origin Resource Sharing) middleware добавлен в NMservices Backend для поддержки Admin Panel.

---

## 📝 Измененные файлы

1. **src/nms/config.py** - добавлен параметр `cors_origins`
2. **src/nms/main.py** - добавлен CORS middleware
3. **.env.example** - добавлен пример `CORS_ORIGINS`
4. **scripts/test_cors.sh** - скрипт для тестирования CORS
5. **CHANGELOG_CORS.md** - детальная документация
6. **README.md** - обновлен раздел тестирования

---

## 🚀 Как использовать

### Development (локально)

1. **Создать/обновить .env файл:**
   ```bash
   cp .env.example .env
   ```

2. **Убедиться что есть строка:**
   ```bash
   CORS_ORIGINS=http://localhost:5173
   ```

3. **Запустить backend:**
   ```bash
   poetry run nms
   ```

4. **Проверить CORS:**
   ```bash
   ./scripts/test_cors.sh
   ```

---

### Production (сервер 192.168.1.191)

1. **Обновить .env на сервере:**
   ```bash
   # Добавить строку в .env
   CORS_ORIGINS=https://admin.nmservices.uz

   # Или для нескольких доменов
   CORS_ORIGINS=https://admin.nmservices.uz,https://admin-staging.nmservices.uz
   ```

2. **Перезапустить сервис:**
   ```bash
   pkill -f uvicorn
   cd /path/to/NMservices
   nohup poetry run nms > nms.log 2>&1 &
   ```

3. **Проверить CORS:**
   ```bash
   ./scripts/test_cors.sh http://192.168.1.191:8000 https://admin.nmservices.uz
   ```

---

## 🧪 Проверка работы

### Вариант 1: Скрипт (рекомендуется)

```bash
./scripts/test_cors.sh http://localhost:8000 http://localhost:5173 admin_secret
```

Ожидаемый результат:
```
✅ CORS headers present
✅ CORS works for actual request
✅ API response valid
```

### Вариант 2: Curl вручную

```bash
# Preflight request
curl -X OPTIONS http://localhost:8000/admin/stats \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Должны быть заголовки:
# Access-Control-Allow-Origin: http://localhost:5173
# Access-Control-Allow-Credentials: true
```

### Вариант 3: Browser Console

```javascript
// Открыть http://localhost:5173 (любая страница)
// В консоли браузера:
fetch('http://localhost:8000/admin/stats', {
  headers: { 'X-Admin-Key': 'admin_secret' }
})
  .then(r => r.json())
  .then(console.log);

// Должно вернуть статистику без CORS ошибки
```

---

## 🔒 Безопасность

### ✅ Правильно (Production):
```bash
CORS_ORIGINS=https://admin.nmservices.uz
```

### ❌ Неправильно (небезопасно):
```bash
CORS_ORIGINS=*  # Разрешает все домены!
```

### ✅ Несколько доменов:
```bash
CORS_ORIGINS=https://admin.nmservices.uz,https://admin-dev.nmservices.uz
```

---

## 🐛 Troubleshooting

### Проблема: CORS ошибка в браузере

```
Access to fetch at 'http://localhost:8000/admin/stats' from origin
'http://localhost:5173' has been blocked by CORS policy
```

**Решение:**

1. Проверить, что backend запущен
2. Проверить .env файл:
   ```bash
   cat .env | grep CORS_ORIGINS
   ```
3. Убедиться что origin в списке:
   ```bash
   CORS_ORIGINS=http://localhost:5173
   ```
4. Перезапустить backend

---

### Проблема: Preflight request возвращает 403

**Причина:** OPTIONS запрос проходит через auth middleware

**Решение:** Уже исправлено! CORS middleware добавлен ПЕРЕД роутерами, поэтому OPTIONS проходит без аутентификации.

---

### Проблема: CORS работает локально, но не на production

**Возможные причины:**

1. **В .env на сервере не добавлен CORS_ORIGINS**
   ```bash
   # На сервере
   echo "CORS_ORIGINS=https://admin.nmservices.uz" >> .env
   ```

2. **Не перезапущен сервис после изменения .env**
   ```bash
   pkill -f uvicorn
   nohup poetry run nms > nms.log 2>&1 &
   ```

3. **Использован http вместо https**
   ```bash
   # ❌ Неправильно
   CORS_ORIGINS=http://admin.nmservices.uz

   # ✅ Правильно
   CORS_ORIGINS=https://admin.nmservices.uz
   ```

---

## 📋 Чеклист готовности к frontend разработке

- [x] CORS middleware добавлен в backend
- [x] .env.example обновлен
- [x] Документация создана (CHANGELOG_CORS.md)
- [x] Тестовый скрипт создан (test_cors.sh)
- [x] README обновлен
- [ ] .env файл настроен (локально или на сервере)
- [ ] Backend запущен
- [ ] CORS проверен и работает

---

## 🎯 Следующие шаги

После того как CORS работает:

1. ✅ **Создать frontend репозиторий** (NMservices-Admin)
2. ✅ **Настроить React Admin** с dataProvider
3. ✅ **Добавить сортировку в backend** (опционально, следующая задача)
4. ✅ **Деплой frontend** на Vercel/Netlify

---

## 📚 Дополнительные ресурсы

- `CHANGELOG_CORS.md` - Детальная документация CORS
- `ADMIN_PANEL_TECH_SPEC_SEPARATE.md` - ТЗ для Admin Panel
- `docs/ARCHITECTURE_QUESTIONS_ANSWERS.md` - Ответы на вопросы архитектора
- [FastAPI CORS Docs](https://fastapi.tiangolo.com/tutorial/cors/)

---

**Готов к frontend разработке!** 🚀
