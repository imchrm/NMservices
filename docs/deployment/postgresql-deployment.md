# Инструкция по разворачиванию PostgreSQL на удаленном хосте

## Системные требования

- **ОС:** Debian GNU/Linux 12 (bookworm)
- **Доступ:** SSH с правами root
- **PostgreSQL версия:** 14 (устанавливается по умолчанию)

## Подключение к серверу

```bash
ssh -p 2251 root@94.158.50.119
```

## 1. Обновление системы

```bash
apt update && apt upgrade -y
```

## 2. Установка PostgreSQL

```bash
apt install postgresql postgresql-contrib -y
```

На Debian 12 по умолчанию устанавливается PostgreSQL 14.

## 3. Проверка установки

```bash
# Проверить версию
ls /etc/postgresql/
# Должно показать: 14

# Проверить статус службы
systemctl status postgresql

# Включить автозапуск при загрузке
systemctl enable postgresql
```

## 4. Настройка PostgreSQL для удаленного доступа

### 4.1. Настройка postgresql.conf

```bash
nano /etc/postgresql/14/main/postgresql.conf
```

Найти строку `listen_addresses` (Ctrl+W для поиска) и изменить на:

```conf
listen_addresses = '*'
```

**Сохранить:** Ctrl+O, Enter, Ctrl+X

### 4.2. Настройка pg_hba.conf

```bash
nano /etc/postgresql/14/main/pg_hba.conf
```

Убедиться, что в начале файла (после комментариев) есть следующие строки:

```conf
# Local connections
local   all             postgres                                peer
local   all             all                                     peer

# IPv4 local connections:
host    all             all             127.0.0.1/32            scram-sha-256

# IPv6 local connections:
host    all             all             ::1/128                 scram-sha-256
```

Добавить в конец файла для удаленного доступа:

```conf
# Remote connections
host    all             all             0.0.0.0/0               scram-sha-256
```

> **⚠️ Важно для продакшена:** Рекомендуется ограничить доступ конкретными IP-адресами вместо `0.0.0.0/0`.

**Сохранить:** Ctrl+O, Enter, Ctrl+X

## 5. Настройка файрвола

### 5.1. Добавить правило для порта 5432

```bash
iptables -I INPUT -p tcp --dport 5432 -j ACCEPT
```

### 5.2. Установить iptables-persistent для сохранения правил

```bash
apt install iptables-persistent -y
```

При установке выбрать **"Yes"** для сохранения текущих правил.

### 5.3. Сохранить правила

```bash
netfilter-persistent save
```

### 5.4. Проверить правила

```bash
iptables -L INPUT -n --line-numbers | grep 5432
```

Должно показать правило для порта 5432.

## 6. Перезапуск PostgreSQL

```bash
systemctl restart postgresql
```

## 7. Проверка доступности

### 7.1. Проверить, что PostgreSQL слушает на всех интерфейсах

```bash
ss -tlnp | grep 5432
```

Ожидаемый результат:

```
LISTEN 0      244          0.0.0.0:5432      0.0.0.0:*
LISTEN 0      244             [::]:5432         [::]:*
```

## 8. Создание пользователя и базы данных для приложения

### 8.1. Подключиться к PostgreSQL

```bash
sudo -u postgres psql
```

### 8.2. Создать пользователя и базу данных

```sql
CREATE USER nmservices_user WITH PASSWORD 'your_secure_password_here';
CREATE DATABASE nmservices_db OWNER nmservices_user;
GRANT ALL PRIVILEGES ON DATABASE nmservices_db TO nmservices_user;
\q
```

> **⚠️ Важно:** Замените `your_secure_password_here` на надежный пароль.

## 9. Проверка работоспособности

### 9.1. Локально на сервере

```bash
sudo -u postgres psql
```

Выполнить тестовые SQL команды:

```sql
-- Создать тестовую таблицу
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставить тестовые записи
INSERT INTO test_table (name) VALUES ('Первая запись');
INSERT INTO test_table (name) VALUES ('Вторая запись');

-- Показать все записи
SELECT * FROM test_table;

-- Удалить тестовую таблицу
DROP TABLE test_table;

-- Выйти
\q
```

### 9.2. С локальной машины

```bash
# Проверить доступность порта
telnet 94.158.50.119 5432
# или
nc -zv 94.158.50.119 5432

# Подключиться через psql (если установлен)
psql -h 94.158.50.119 -p 5432 -U nmservices_user -d nmservices_db
```

## 10. Параметры подключения для приложения

Используйте следующие параметры в переменных окружения вашего приложения:

```env
DB_HOST=94.158.50.119
DB_PORT=5432
DB_NAME=nmservices_db
DB_USER=nmservices_user
DB_PASSWORD=your_secure_password_here
```

## Полезные команды для управления PostgreSQL

### Управление службой

```bash
# Статус службы
systemctl status postgresql

# Перезапуск
systemctl restart postgresql

# Остановка
systemctl stop postgresql

# Запуск
systemctl start postgresql

# Просмотр логов
journalctl -u postgresql -f
```

### Подключение к PostgreSQL

```bash
# Подключение к psql
sudo -u postgres psql

# Подключение к конкретной БД
sudo -u postgres psql -d nmservices_db
```

## Команды psql (внутри интерактивной оболочки)

| Команда | Описание |
|---------|----------|
| `\l` | Список баз данных |
| `\c dbname` | Подключиться к базе данных |
| `\dt` | Список таблиц |
| `\d tablename` | Структура таблицы |
| `\du` | Список пользователей |
| `\q` | Выход |

## Рекомендации по безопасности

1. **Используйте сильные пароли** для пользователей БД
   - Минимум 16 символов, включая буквы, цифры и специальные символы

2. **Ограничьте доступ по IP** в pg_hba.conf
   - Замените `0.0.0.0/0` на конкретные IP-адреса
   - Пример: `host all all 192.168.1.100/32 scram-sha-256`

3. **Настройте SSL/TLS** для шифрования соединений
   - Редактируйте `postgresql.conf`: `ssl = on`
   - Настройте SSL-сертификаты

4. **Регулярно обновляйте** PostgreSQL и систему
   ```bash
   apt update && apt upgrade -y
   ```

5. **Настройте резервное копирование**
   ```bash
   # Пример бэкапа с помощью pg_dump
   sudo -u postgres pg_dump nmservices_db > backup_$(date +%Y%m%d).sql
   ```

6. **Используйте fail2ban** для защиты от брутфорса
   ```bash
   apt install fail2ban -y
   ```

7. **Мониторьте логи** на подозрительную активность
   ```bash
   tail -f /var/log/postgresql/postgresql-14-main.log
   ```

## Решение типичных проблем

### PostgreSQL слушает только на localhost

**Проблема:** `ss -tlnp | grep 5432` показывает `127.0.0.1:5432`

**Решение:** Проверьте `listen_addresses = '*'` в `postgresql.conf` и перезапустите службу.

### Ошибка аутентификации

**Проблема:** `password authentication failed`

**Решение:** Проверьте настройки в `pg_hba.conf` и используйте правильный метод аутентификации (`peer` для локальных, `scram-sha-256` для удаленных подключений).

### Порт недоступен извне

**Проблема:** Не удается подключиться с локальной машины

**Решение:**
1. Проверьте правила файрвола: `iptables -L | grep 5432`
2. Убедитесь, что правила сохранены: `netfilter-persistent save`
3. Проверьте настройки хостинг-провайдера (облачный файрвол, security groups)

## Пограничные условия и их преодоление (локальная разработка)

### 1. Ошибка "Peer authentication failed"

**Проблема:** При попытке подключения через `psql -U postgres -d postgres` возникает ошибка:
```
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  Peer authentication failed for user "postgres"
```

**Причина:** PostgreSQL по умолчанию использует `peer` аутентификацию для локальных подключений. Она проверяет соответствие имени пользователя Linux и пользователя БД. Если вы работаете под пользователем `dm`, а пытаетесь подключиться как `postgres` - доступ будет запрещен.

**Решение 1 (временное, для разработки):** Используйте `sudo` для переключения на пользователя postgres:
```bash
sudo -u postgres psql
```

**Решение 2 (постоянное):** Измените метод аутентификации на парольный:

1. Откройте файл конфигурации:
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

2. Найдите строки:
```conf
local   all             postgres                                peer
local   all             all                                     peer
```

3. Измените `peer` на `md5`:
```conf
local   all             postgres                                md5
local   all             all                                     md5
```

4. Сохраните файл (Ctrl+O, Enter, Ctrl+X)

5. Установите пароль для пользователя postgres:
```bash
sudo -u postgres psql
```

В консоли psql:
```sql
ALTER USER postgres WITH PASSWORD 'postgres';
\q
```

6. Перезапустите PostgreSQL:
```bash
sudo systemctl restart postgresql
```

7. Проверьте подключение с паролем:
```bash
psql -U postgres -d postgres -h localhost
```

**Важно:** Флаг `-h localhost` заставляет использовать TCP/IP соединение вместо Unix socket, что требует парольной аутентификации.

### 2. База данных не существует

**Проблема:** Тесты падают с ошибкой подключения к несуществующей базе `nomus`.

**Причина:** База данных не была создана после установки PostgreSQL.

**Решение:**

1. Подключитесь к PostgreSQL:
```bash
sudo -u postgres psql
```

2. Создайте базу данных:
```sql
CREATE DATABASE nomus;
```

**⚠️ Важно:** Команда в SQL **обязательно** должна заканчиваться точкой с запятой `;`. Без неё команда считается незавершенной.

3. Проверьте создание базы:
```sql
\l
```

Вы должны увидеть `nomus` в списке баз данных.

4. Подключитесь к базе и создайте таблицы:
```sql
\c nomus
```

5. Выполните скрипт инициализации:
```bash
\i /полный/путь/к/проекту/scripts/init_db.sql
```

**Альтернатива:** Если возникают проблемы с правами доступа к файлу, выполните команды вручную:

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 3. Отсутствует файл .env

**Проблема:** Приложение использует настройки по умолчанию из кода, которые могут не соответствовать вашей локальной конфигурации.

**Решение:**

1. Создайте файл `.env` в корне проекта:
```bash
cp .env.example .env
```

2. Проверьте и измените настройки подключения к БД:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/nomus
```

Формат строки подключения:
```
postgresql+asyncpg://ПОЛЬЗОВАТЕЛЬ:ПАРОЛЬ@ХОСТ:ПОРТ/ИМЯ_БАЗЫ
```

### 4. Команда SQL не выполняется

**Проблема:** Вы пишете команду в `psql`, но ничего не происходит. Приглашение меняется на `postgres-#` или `postgres(#`.

**Причина:** Команда не завершена. PostgreSQL ожидает точку с запятой `;`.

**Пример неправильно:**
```sql
CREATE DATABASE nomus
-- psql покажет: postgres-#
-- и будет ждать продолжения команды
```

**Пример правильно:**
```sql
CREATE DATABASE nomus;
-- psql выполнит команду и покажет: CREATE DATABASE
```

**Решение:** Всегда завершайте SQL команды точкой с запятой `;`.

### 5. Permission denied при выполнении \i в psql

**Проблема:** При попытке выполнить `\i /home/dm/scripts/init_db.sql` возникает ошибка "Permission denied".

**Причина:** Пользователь `postgres` в Linux не имеет прав на чтение файлов в домашней директории другого пользователя (`/home/dm/`).

**Решение 1:** Дайте права на чтение файла:
```bash
chmod +r /home/dm/dev/python/NMservices/scripts/init_db.sql
```

**Решение 2 (рекомендуется):** Скопируйте и вставьте содержимое скрипта непосредственно в консоль `psql`.

**Решение 3:** Переместите скрипт в доступное место:
```bash
sudo cp scripts/init_db.sql /tmp/
sudo -u postgres psql -d nomus -f /tmp/init_db.sql
```

### 6. Проверка успешной настройки

После выполнения всех настроек проверьте:

1. **PostgreSQL запущен:**
```bash
systemctl status postgresql
```
Должно быть: `Active: active`

2. **База данных существует:**
```bash
sudo -u postgres psql -c "\l" | grep nomus
```
Должна быть строка с `nomus`

3. **Таблицы созданы:**
```bash
sudo -u postgres psql -d nomus -c "\dt"
```
Должна быть таблица `users`

4. **Парольная аутентификация работает:**
```bash
psql -U postgres -d nomus -h localhost
```
Должен запросить пароль и подключиться

5. **Тесты проходят:**
```bash
poetry run pytest -v
```
Все 6 тестов должны пройти успешно

---

**PostgreSQL успешно развернут и готов к использованию!**

## Дополнительные ресурсы

- [Официальная документация PostgreSQL](https://www.postgresql.org/docs/)
- [PostgreSQL на Debian Wiki](https://wiki.debian.org/PostgreSql)
- [Руководство по безопасности PostgreSQL](https://www.postgresql.org/docs/current/security.html)
