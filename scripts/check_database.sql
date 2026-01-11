-- Скрипт для диагностики таблицы users в PostgreSQL
-- Запустите: psql -U postgres -d nomus -f scripts/check_database.sql

-- 1. Проверка структуры таблицы users
\echo '=== СТРУКТУРА ТАБЛИЦЫ users ==='
\d+ users

-- 2. Проверка всех записей в таблице
\echo ''
\echo '=== ВСЕ ЗАПИСИ В ТАБЛИЦЕ users ==='
SELECT * FROM users;

-- 3. Подсчет количества записей
\echo ''
\echo '=== КОЛИЧЕСТВО ЗАПИСЕЙ ==='
SELECT COUNT(*) as total_users FROM users;

-- 4. Проверка последовательности (sequence) для автоинкремента
\echo ''
\echo '=== ПРОВЕРКА SEQUENCE ДЛЯ ID ==='
SELECT
    c.relname as sequence_name,
    last_value,
    is_called
FROM pg_class c
JOIN pg_depend d ON d.objid = c.oid
WHERE c.relkind = 'S'
  AND d.refobjid = 'users'::regclass;

-- 5. Проверка активных транзакций
\echo ''
\echo '=== АКТИВНЫЕ ТРАНЗАКЦИИ ==='
SELECT
    pid,
    usename,
    application_name,
    state,
    query_start,
    state_change,
    query
FROM pg_stat_activity
WHERE datname = 'nomus'
  AND state != 'idle';

-- 6. Проверка прав доступа к таблице
\echo ''
\echo '=== ПРАВА ДОСТУПА К ТАБЛИЦЕ users ==='
\dp users
