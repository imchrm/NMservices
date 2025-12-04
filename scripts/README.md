# Testing Scripts for NMservices API

Удалённые тесты API для проверки работы микросервисов на любом окружении.

## 📋 Содержание

- `test_api.sh` - bash-скрипт для Linux/macOS
- `test_api.ps1` - PowerShell-скрипт для Windows
- `README.md` - этот файл

## 🚀 Быстрый старт

### Linux/macOS

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

---

**Версия:** 1.0.0
**Дата:** 2025-12-04
