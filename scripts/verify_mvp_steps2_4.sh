#!/bin/bash
# =============================================================================
# MVP Verification Script: Steps 2-4
# Run on: dm@id (192.168.1.191)
# From:   ~/dev/python/NMservices
# Usage:  bash scripts/verify_mvp_steps2_4.sh
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

DB_NAME="nomus"
DB_USER="postgres"

pass_count=0
fail_count=0

check_pass() {
    echo -e "  ${GREEN}✅ PASS:${NC} $1"
    ((pass_count++))
}

check_fail() {
    echo -e "  ${RED}❌ FAIL:${NC} $1"
    ((fail_count++))
}

separator() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# =============================================================================
# STEP 2: Verify DB structure via psql
# =============================================================================
separator
echo -e "${BOLD}${YELLOW}STEP 2: Проверка структуры БД через psql${NC}"
separator

# 2a. Check alembic_version
echo -e "${BOLD}2a. Текущая версия Alembic:${NC}"
result=$(psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "SELECT version_num FROM alembic_version;" 2>&1)
echo "    version_num = $result"
if [ "$result" = "d4e5f6a7b8c9" ]; then
    check_pass "Alembic version is d4e5f6a7b8c9 (seed_services_data)"
else
    check_fail "Expected d4e5f6a7b8c9, got: $result"
fi

echo ""

# 2b. Check services table exists and has correct structure
echo -e "${BOLD}2b. Структура таблицы services:${NC}"
psql -U "$DB_USER" -d "$DB_NAME" -c "\d services"
echo ""

# Verify columns exist
for col in id name description base_price duration_minutes is_active created_at updated_at; do
    exists=$(psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
        SELECT count(*) FROM information_schema.columns
        WHERE table_name='services' AND column_name='$col';
    ")
    if [ "$exists" = "1" ]; then
        check_pass "Column services.$col exists"
    else
        check_fail "Column services.$col NOT FOUND"
    fi
done

echo ""

# 2c. Check orders table new columns
echo -e "${BOLD}2c. Новые колонки в таблице orders:${NC}"
psql -U "$DB_USER" -d "$DB_NAME" -c "\d orders"
echo ""

for col in service_id address_text scheduled_at; do
    exists=$(psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
        SELECT count(*) FROM information_schema.columns
        WHERE table_name='orders' AND column_name='$col';
    ")
    if [ "$exists" = "1" ]; then
        check_pass "Column orders.$col exists"
    else
        check_fail "Column orders.$col NOT FOUND"
    fi
done

echo ""

# 2d. Check foreign key on orders.service_id
echo -e "${BOLD}2d. Foreign key orders.service_id -> services.id:${NC}"
fk_exists=$(psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
    SELECT count(*) FROM information_schema.table_constraints
    WHERE constraint_name='fk_orders_service_id' AND table_name='orders';
")
if [ "$fk_exists" = "1" ]; then
    check_pass "FK fk_orders_service_id exists"
else
    check_fail "FK fk_orders_service_id NOT FOUND"
fi

echo ""

# 2e. Check indexes
echo -e "${BOLD}2e. Индексы:${NC}"
idx_active=$(psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
    SELECT count(*) FROM pg_indexes
    WHERE tablename='services' AND indexname='idx_services_is_active';
")
if [ "$idx_active" = "1" ]; then
    check_pass "Index idx_services_is_active exists"
else
    check_fail "Index idx_services_is_active NOT FOUND"
fi

idx_service=$(psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
    SELECT count(*) FROM pg_indexes
    WHERE tablename='orders' AND indexname='idx_orders_service_id';
")
if [ "$idx_service" = "1" ]; then
    check_pass "Index idx_orders_service_id exists"
else
    check_fail "Index idx_orders_service_id NOT FOUND"
fi

echo ""

# 2f. Check seed data
echo -e "${BOLD}2f. Seed данные (services):${NC}"
psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT id, name, base_price, duration_minutes, is_active FROM services ORDER BY id;"

seed_count=$(psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "SELECT count(*) FROM services;")
if [ "$seed_count" -ge "4" ]; then
    check_pass "Found $seed_count services (expected >= 4)"
else
    check_fail "Found $seed_count services (expected >= 4)"
fi

# =============================================================================
# STEP 2 SUMMARY
# =============================================================================
separator
echo -e "${BOLD}${YELLOW}STEP 2 SUMMARY:${NC} ${GREEN}$pass_count passed${NC}, ${RED}$fail_count failed${NC}"
separator

# =============================================================================
# STEP 4: Run pytest
# =============================================================================
echo -e "${BOLD}${YELLOW}STEP 4: Запуск pytest${NC}"
separator

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}ERROR: pyproject.toml not found. Run this script from the project root.${NC}"
    echo -e "  cd ~/dev/python/NMservices && bash scripts/verify_mvp_steps2_4.sh"
    exit 1
fi

# Check if poetry/venv is available
if command -v poetry &> /dev/null; then
    echo -e "${CYAN}Running: poetry run pytest${NC}"
    echo ""
    poetry run pytest
    pytest_exit=$?
elif [ -d ".venv" ]; then
    echo -e "${CYAN}Running: .venv/bin/pytest${NC}"
    echo ""
    .venv/bin/pytest
    pytest_exit=$?
else
    echo -e "${CYAN}Running: pytest (system)${NC}"
    echo ""
    pytest
    pytest_exit=$?
fi

separator
if [ $pytest_exit -eq 0 ]; then
    echo -e "${GREEN}${BOLD}STEP 4: pytest PASSED ✅${NC}"
else
    echo -e "${RED}${BOLD}STEP 4: pytest FAILED ❌ (exit code: $pytest_exit)${NC}"
fi

# =============================================================================
# FINAL SUMMARY
# =============================================================================
separator
echo -e "${BOLD}${YELLOW}═══════════════════════════════════${NC}"
echo -e "${BOLD}${YELLOW}  FINAL VERIFICATION SUMMARY${NC}"
echo -e "${BOLD}${YELLOW}═══════════════════════════════════${NC}"
echo -e "  Step 2 (DB structure): ${GREEN}$pass_count checks passed${NC}, ${RED}$fail_count checks failed${NC}"
echo -e "  Step 3 (db_cli.py):    ⏭️  Interactive — run manually (see below)"
echo -e "  Step 4 (pytest):       $([ $pytest_exit -eq 0 ] && echo -e "${GREEN}PASSED ✅${NC}" || echo -e "${RED}FAILED ❌${NC}")"
echo ""
echo -e "${BOLD}For Step 3 (db_cli.py interactive test), run:${NC}"
echo -e "  ${CYAN}poetry run python scripts/db_cli.py${NC}"
echo -e "  Then: Menu 3 → 3a (list services) → verify 4 services shown"
echo -e "  Then: Menu 2 → 2c (create order) → enter user_id, service_id=1"
separator
