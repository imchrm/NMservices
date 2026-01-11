# Scripts for NMservices

Коллекция скриптов для тестирования, диагностики и развёртывания NMservices API.

## 📋 Содержание

### Тестирование API
- `test_api.sh` - bash-скрипт для тестирования API (Linux/macOS)
- `test_api.ps1` - PowerShell-скрипт для тестирования API (Windows)
- `test_registration.py` - Python-скрипт для тестирования регистрации пользователей

### Диагностика базы данных
- `diagnose_db_issue.py` - Быстрая диагностика проблем с сохранением данных в PostgreSQL
- `recreate_database.py` - Пересоздание таблиц через SQLAlchemy
- `check_database.sql` - SQL-скрипт для проверки структуры БД

### Развёртывание
- `deploy.sh` - bash-скрипт для развёртывания на удалённом сервере

### Документация
- `README.md` - этот файл

## 🚀 Быстрый старт

### Диагностика проблемы с базой данных

Если записи не сохраняются в PostgreSQL, запустите диагностику:

```bash
poetry run python scripts/diagnose_db_issue.py
```

Для полного решения проблемы:

```bash
poetry run python scripts/recreate_database.py
```

См. подробную документацию: `docs/development/TROUBLESHOOTING_DB.md`

### Тестирование регистрации пользователей

```bash
# Отредактируйте API_BASE_URL в scripts/test_registration.py
poetry run python scripts/test_registration.py
```

См. документацию по сетевому тестированию: `docs/development/NETWORK_TESTING.md`

### Тестирование API (Linux/macOS)

```bash
# Сделать скрипт исполняемым
chmod +x scripts/test_api.sh

# Запустить с параметрами по умолчанию
./scripts/test_api.sh

# Запустить с кастомными параметрами
./scripts/test_api.sh --host 192.168.1.100 --port 8080 --key "your_api_key"
```

### Windows (PowerShell)

```powershell
# Запустить с параметрами по умолчанию
.\scripts\test_api.ps1

# Запустить с кастомными параметрами
.\scripts\test_api.ps1 -Host "192.168.1.100" -Port 8080 -ApiKey "your_api_key"
```

## 📖 Использование

### Bash Script (test_api.sh)

#### Опции командной строки

```bash
./test_api.sh [OPTIONS]

OPTIONS:
    -h, --host HOST         API host (default: 127.0.0.1)
    -p, --port PORT         API port (default: 8000)
    -k, --key API_KEY       X-API-Key header value (default: test_secret)
    -t, --timeout SECONDS   Request timeout (default: 10)
    -v, --verbose           Enable verbose output
    --help                  Show help message
```

#### Переменные окружения

```bash
# Через переменные окружения
export HOST=192.168.1.100
export PORT=8080
export API_KEY=your_secret_key
./scripts/test_api.sh

# Или в одной строке
HOST=192.168.1.100 PORT=8080 API_KEY=secret ./scripts/test_api.sh
```

#### Примеры использования

```bash
# Локальный сервер (по умолчанию)
./scripts/test_api.sh

# Удалённый сервер
./scripts/test_api.sh --host api.example.com --key "prod_api_key_123"

# С verbose режимом для отладки
./scripts/test_api.sh -v

# Увеличенный таймаут для медленных соединений
./scripts/test_api.sh --timeout 30

# Docker контейнер
./scripts/test_api.sh --host localhost --port 8000

# Production сервер
./scripts/test_api.sh \
  --host api.nomus.uz \
  --port 443 \
  --key "${PRODUCTION_API_KEY}"
```

### PowerShell Script (test_api.ps1)

#### Параметры

```powershell
.\test_api.ps1 [OPTIONS]

OPTIONS:
    -Host <host>         API host (default: 127.0.0.1)
    -Port <port>         API port (default: 8000)
    -ApiKey <key>        X-API-Key header value (default: test_secret)
    -Timeout <seconds>   Request timeout (default: 10)
    -Verbose             Enable verbose output
    -Help                Show help message
```

#### Примеры использования

```powershell
# Локальный сервер (по умолчанию)
.\scripts\test_api.ps1

# Удалённый сервер
.\scripts\test_api.ps1 -Host "api.example.com" -ApiKey "prod_api_key_123"

# С verbose режимом
.\scripts\test_api.ps1 -Verbose

# Docker контейнер
.\scripts\test_api.ps1 -Host "localhost" -Port 8000

# Production сервер
$ApiKey = $env:PRODUCTION_API_KEY
.\scripts\test_api.ps1 -Host "api.nomus.uz" -Port 443 -ApiKey $ApiKey
```

## ✅ Выполняемые тесты

Скрипты выполняют те же тесты, что и `tests/test_main.py`:

### 1. Health Check (публичный эндпоинт)
```http
GET /
```
Проверяет доступность API без аутентификации.

### 2. Security: Register без аутентификации
```http
POST /register
```
Проверяет, что эндпоинт отклоняет запросы без API ключа (должен вернуть 403).

### 3. Security: Register с неверным ключом
```http
POST /register
X-API-Key: wrong_password
```
Проверяет, что неверный API ключ отклоняется (должен вернуть 403).

### 4. User Registration (успешная)
```http
POST /register
X-API-Key: <valid_key>
Content-Type: application/json

{
  "phone_number": "+998901234567"
}
```
Проверяет успешную регистрацию пользователя (должен вернуть 200 с user_id).

### 5. Validation: Некорректные данные
```http
POST /register
X-API-Key: <valid_key>
Content-Type: application/json

{}
```
Проверяет валидацию запроса (должен вернуть 422).

### 6. Order Creation (успешное)
```http
POST /create_order
X-API-Key: <valid_key>
Content-Type: application/json

{
  "user_id": 101,
  "tariff_code": "standard_300"
}
```
Проверяет создание заказа (должен вернуть 200 с order_id).

## 📊 Формат вывода

### Успешный запуск

```
========================================
  NMservices API Remote Testing
========================================

Base URL:     http://127.0.0.1:8000
API Key:      test****
Timeout:      10s

[1/6] Testing health check endpoint...
✓ GET / - Health check

[2/6] Testing security - register without auth...
✓ POST /register - No auth

[3/6] Testing security - register with wrong auth...
✓ POST /register - Wrong auth

[4/6] Testing user registration (legacy endpoint)...
✓ POST /register - Success

[5/6] Testing validation - empty request body...
✓ POST /register - Validation error

[6/6] Testing order creation (legacy endpoint)...
✓ POST /create_order - Success

========================================
Total tests:  6
Passed:       6
Failed:       0
========================================
All tests passed!
```

### Неудачный запуск

```
[1/6] Testing health check endpoint...
✗ GET / - Health check
  HTTP 0 (expected 200)

========================================
Total tests:  6
Passed:       5
Failed:       1
========================================
Some tests failed!
```

## 🔧 Требования

### Bash Script

- **curl** - для HTTP запросов
- **bash** 4.0+ - для выполнения скрипта
- **grep, awk, sed** - стандартные утилиты Unix

Установка curl:
```bash
# Ubuntu/Debian
sudo apt-get install curl

# CentOS/RHEL
sudo yum install curl

# macOS (обычно уже установлен)
brew install curl
```

### PowerShell Script

- **PowerShell** 5.1+ или PowerShell Core 7+
- **Invoke-RestMethod** - встроенный cmdlet (доступен по умолчанию)

## 🐳 Использование с Docker

```bash
# Запуск сервиса в Docker
docker run -d -p 8000:8000 --name nms-api nms:latest

# Тестирование
./scripts/test_api.sh --host localhost --port 8000

# Остановка
docker stop nms-api
```

## 🌐 Использование в CI/CD

### GitHub Actions

```yaml
- name: Test API
  run: |
    ./scripts/test_api.sh \
      --host ${{ secrets.API_HOST }} \
      --port 8000 \
      --key ${{ secrets.API_KEY }}
```

### GitLab CI

```yaml
test:api:
  script:
    - chmod +x scripts/test_api.sh
    - ./scripts/test_api.sh --host $API_HOST --key $API_KEY
```

### Jenkins

```groovy
stage('API Tests') {
    steps {
        sh """
            chmod +x scripts/test_api.sh
            ./scripts/test_api.sh \
              --host ${API_HOST} \
              --key ${API_KEY}
        """
    }
}
```

## 🔍 Отладка

### Включение verbose режима

**Bash:**
```bash
./scripts/test_api.sh -v
```

**PowerShell:**
```powershell
.\scripts\test_api.ps1 -Verbose
```

Verbose режим показывает:
- Полные HTTP запросы
- Заголовки запросов
- Тела ответов
- Curl команды (bash)

### Проверка доступности API

```bash
# Проверка что сервер доступен
curl -v http://localhost:8000/

# Проверка с API ключом
curl -H "X-API-Key: test_secret" http://localhost:8000/register
```

### Типичные проблемы

#### 1. Connection refused
```
Error: curl: (7) Failed to connect to localhost port 8000
```
**Решение:** Убедитесь что API сервер запущен

#### 2. Timeout
```
Error: curl: (28) Operation timed out
```
**Решение:** Увеличьте таймаут или проверьте сетевое подключение

#### 3. 403 Forbidden на всех запросах
```
✗ POST /register - Success
  HTTP 403 (expected 200)
```
**Решение:** Проверьте правильность API ключа

## 📝 Расширение скриптов

### Добавление нового теста (Bash)

```bash
# Добавьте функцию
test_new_endpoint() {
    echo ""
    echo -e "${YELLOW}[7/7]${NC} Testing new endpoint..."

    local data='{"field": "value"}'
    response=$(make_request "POST" "/new_endpoint" "$data" "true")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        print_result "POST /new_endpoint" "PASS" "Success"
    else
        print_result "POST /new_endpoint" "FAIL" "HTTP $http_code"
    fi
}

# Добавьте вызов в main()
main() {
    # ... existing tests ...
    test_new_endpoint
    print_footer
}
```

### Добавление нового теста (PowerShell)

```powershell
function Test-NewEndpoint {
    Write-Host ""
    Write-Host "[7/7] Testing new endpoint..." -ForegroundColor Yellow

    $body = @{
        field = "value"
    }

    $response = Invoke-ApiRequest -Method "POST" -Endpoint "/new_endpoint" -Body $body -UseAuth $true

    if ($response.StatusCode -eq 200) {
        Print-Result "POST /new_endpoint" "PASS" "Success"
    }
    else {
        Print-Result "POST /new_endpoint" "FAIL" "HTTP $($response.StatusCode)"
    }
}

# Добавьте вызов в конце скрипта
Test-NewEndpoint
```

## 🔐 Безопасность

### Защита API ключей

**Не передавайте секретные ключи в командной строке напрямую!**

Используйте переменные окружения:

```bash
# Bash
export API_KEY=$(cat /secure/path/api_key.txt)
./scripts/test_api.sh

# PowerShell
$env:API_KEY = Get-Content -Path "C:\secure\path\api_key.txt"
.\scripts\test_api.ps1 -ApiKey $env:API_KEY
```

Или файлы конфигурации:

```bash
# .env файл
API_HOST=api.example.com
API_KEY=secret_key_here

# Загрузка в bash
source .env
./scripts/test_api.sh --host $API_HOST --key $API_KEY
```

## 📚 Дополнительные ресурсы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [curl Manual](https://curl.se/docs/manual.html)
- [PowerShell Invoke-RestMethod](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod)

## 🤝 Вклад в разработку

При добавлении новых эндпоинтов в API, обновите тесты:

1. Добавьте тест-функцию
2. Обновите счётчик тестов в выводе
3. Обновите этот README
4. Добавьте пример использования

## 📞 Поддержка

При возникновении проблем:

1. Проверьте verbose вывод (`-v` или `-Verbose`)
2. Убедитесь что API сервер доступен
3. Проверьте правильность параметров
4. Создайте issue на GitHub с логами

## 🚀 Deployment Script (deploy.sh)

Скрипт для автоматизированного развёртывания на удалённом сервере.

### Требования

- SSH доступ к удалённому серверу
- Python 3.11+, git, poetry установлены на сервере

### Использование

```bash
# Сделать исполняемым
chmod +x scripts/deploy.sh

# Подключиться к серверу
./scripts/deploy.sh connect -u username

# Задеплоить приложение
./scripts/deploy.sh deploy -u username

# Проверить статус
./scripts/deploy.sh status -u username

# Просмотр логов
./scripts/deploy.sh logs -u username

# Остановить сервис
./scripts/deploy.sh stop -u username

# Перезапустить сервис
./scripts/deploy.sh restart -u username

# Тестировать API
API_KEY=secret ./scripts/deploy.sh test -u username
```

### Команды

| Команда | Описание |
|---------|----------|
| `connect` | Подключиться к серверу через SSH |
| `deploy` | Задеплоить приложение (клонирование, установка, запуск) |
| `status` | Проверить статус сервиса |
| `logs` | Просмотр логов в реальном времени |
| `stop` | Остановить сервис |
| `restart` | Перезапустить сервис |
| `test` | Запустить удалённые тесты |
| `help` | Показать справку |

### Параметры

```bash
-u, --user USER     Remote username (обязательно)
-h, --host HOST     Remote host (default: 94.158.50.119)
-p, --port PORT     SSH port (default: 2251)
-s, --service PORT  Service port (default: 9800)
```

### Переменные окружения

```bash
REMOTE_USER=myuser
REMOTE_HOST=94.158.50.119
REMOTE_PORT=2251
SERVICE_PORT=9800
API_KEY=your_api_key
```

### Примеры

```bash
# Полный деплой с нуля
./scripts/deploy.sh deploy -u myuser

# Проверить что сервис работает
./scripts/deploy.sh status -u myuser

# Посмотреть логи
./scripts/deploy.sh logs -u myuser

# Протестировать API
export API_KEY=my_secret_key
./scripts/deploy.sh test -u myuser

# Перезапустить после обновления кода
./scripts/deploy.sh restart -u myuser

# Кастомный порт
./scripts/deploy.sh deploy -u myuser -s 9801
```

### Что делает команда deploy

1. Проверяет окружение на сервере (python, git, poetry)
2. Клонирует репозиторий (или обновляет если уже есть)
3. Устанавливает зависимости через poetry
4. Создаёт `.env` файл с секретным ключом
5. Останавливает старый процесс (если есть)
6. Запускает сервис в фоне с nohup
7. Проверяет что сервис запустился

### См. также

- `DEPLOYMENT.md` - полное руководство по развёртыванию
- `QUICKSTART_DEPLOY.md` - быстрая шпаргалка

---

**Версия:** 1.0.0
**Дата:** 2025-12-04
