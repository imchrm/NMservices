# 🧪 Тестирование NMservices API

Два способа тестирования API: локально с pytest и удалённо с bash/PowerShell скриптами.

## 🏠 Локальное тестирование (pytest)

Для разработки и CI/CD.

### Запуск

```bash
# Установить зависимости
poetry install

# Запустить все тесты
poetry run pytest

# С подробным выводом
poetry run pytest -v

# Конкретный тест
poetry run pytest tests/test_main.py::test_read_root
```

### Покрытие

```bash
# С coverage
poetry run pytest --cov=src --cov-report=html

# Открыть отчёт
open htmlcov/index.html
```

## 🌐 Удалённое тестирование (bash/PowerShell)

Для проверки деплоя, staging, production.

### Linux/macOS (bash)

```bash
# Локальный сервер
./scripts/test_api.sh

# Удалённый сервер
./scripts/test_api.sh \
  --host api.example.com \
  --port 443 \
  --key "your_api_key"

# Staging
./scripts/test_api.sh \
  --host staging.nomus.uz \
  --key "${STAGING_API_KEY}"

# Production
./scripts/test_api.sh \
  --host api.nomus.uz \
  --key "${PRODUCTION_API_KEY}"
```

### Windows (PowerShell)

```powershell
# Локальный сервер
.\scripts\test_api.ps1

# Удалённый сервер
.\scripts\test_api.ps1 `
  -Host "api.example.com" `
  -Port 443 `
  -ApiKey "your_api_key"

# Production
.\scripts\test_api.ps1 `
  -Host "api.nomus.uz" `
  -ApiKey $env:PRODUCTION_API_KEY
```

## 📋 Сравнение методов

| Характеристика | pytest | bash/PowerShell |
|---------------|--------|-----------------|
| **Где запускать** | Локально, CI/CD | Anywhere |
| **Требует** | Python, dependencies | curl / PowerShell |
| **Скорость** | Очень быстро | Быстро |
| **Использование** | Разработка | Production checks |
| **Покрытие кода** | ✅ Да | ❌ Нет |
| **Интеграция** | ✅ Глубокая | ❌ Поверхностная |
| **Удалённое тестирование** | ❌ Сложно | ✅ Легко |

## 🎯 Когда использовать что

### Используйте pytest:
- ✅ Во время разработки
- ✅ В pre-commit hooks
- ✅ В CI/CD pipeline
- ✅ Для unit/integration тестов
- ✅ Когда нужен coverage

### Используйте bash/PowerShell:
- ✅ Для проверки деплоя
- ✅ Smoke testing на production
- ✅ Мониторинг здоровья API
- ✅ Когда нет Python окружения
- ✅ Для быстрых проверок

## 🚀 Примеры использования

### 1. Локальная разработка

```bash
# Запустить сервер
poetry run nms

# В другом терминале - запустить тесты
poetry run pytest -v
```

### 2. Проверка после деплоя

```bash
# Задеплоили на staging
git push staging main

# Проверяем что всё работает
./scripts/test_api.sh \
  --host staging.example.com \
  --key "${STAGING_KEY}"
```

### 3. CI/CD Pipeline

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: poetry run pytest --cov

- name: Deploy to staging
  run: ./deploy.sh staging

- name: Smoke test staging
  run: |
    ./scripts/test_api.sh \
      --host ${{ secrets.STAGING_HOST }} \
      --key ${{ secrets.STAGING_KEY }}
```

### 4. Monitoring / Health checks

```bash
# Cron job для мониторинга
*/5 * * * * /path/to/scripts/test_api.sh --host api.nomus.uz --key "$API_KEY" || alert.sh
```

### 5. Docker тестирование

```bash
# Запустить контейнер
docker run -d -p 8000:8000 nms:latest

# Подождать готовности
sleep 5

# Протестировать
./scripts/test_api.sh --host localhost --port 8000
```

## 📖 Подробная документация

- **pytest тесты**: см. `tests/test_main.py`
- **Удалённые тесты**: см. `scripts/README.md`
- **Архитектура**: см. `doc/REFACTORING.md`

## 🔍 Отладка

### pytest не запускается

```bash
# Проверить окружение
poetry env info

# Переустановить зависимости
poetry install --sync

# Проверить импорты
poetry run python -c "from nms.main import app; print('OK')"
```

### Удалённые тесты не проходят

```bash
# Проверить доступность
curl -v http://api.example.com/

# Проверить API ключ
curl -H "X-API-Key: test_secret" http://api.example.com/

# Verbose режим
./scripts/test_api.sh -v
```

## 🎓 Best Practices

1. **Всегда запускайте pytest перед коммитом**
   ```bash
   git commit -m "..." && poetry run pytest || git reset HEAD~1
   ```

2. **Проверяйте production после каждого деплоя**
   ```bash
   ./scripts/test_api.sh --host api.nomus.uz --key "$PROD_KEY"
   ```

3. **Используйте переменные окружения для ключей**
   ```bash
   export API_KEY=$(cat /secure/api_key.txt)
   ```

4. **Настройте мониторинг**
   - Регулярные health checks
   - Алерты при падении тестов
   - Логирование результатов

---

**См. также:**
- `scripts/README.md` - полная документация по удалённым тестам
- `tests/test_main.py` - примеры pytest тестов
- `doc/DOCS_INDEX.md` - навигация по документации
