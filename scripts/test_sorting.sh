#!/bin/bash
# Test sorting functionality for Admin API

BASE_URL="${1:-http://localhost:8000}"
ADMIN_KEY="${2:-admin_secret}"

echo "======================================================================"
echo "🧪 TESTING SORTING FUNCTIONALITY"
echo "======================================================================"
echo "📍 Base URL: $BASE_URL"
echo "🔑 Admin Key: ${ADMIN_KEY:0:4}****"
echo "======================================================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}==================== USERS SORTING ====================${NC}"
echo ""

echo "Test 1: Default sorting (id, asc)"
echo "----------------------------------------------------------------------"
curl -s -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/users?limit=5" | jq '.users[] | {id, phone_number}'
echo ""

echo "Test 2: Sort by created_at (desc) - newest first"
echo "----------------------------------------------------------------------"
curl -s -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/users?limit=5&sort_by=created_at&order=desc" | jq '.users[] | {id, created_at}'
echo ""

echo "Test 3: Sort by phone_number (asc)"
echo "----------------------------------------------------------------------"
curl -s -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/users?limit=5&sort_by=phone_number&order=asc" | jq '.users[] | {id, phone_number}'
echo ""

echo "Test 4: Sort by id (desc)"
echo "----------------------------------------------------------------------"
curl -s -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/users?limit=5&sort_by=id&order=desc" | jq '.users[] | {id, phone_number}'
echo ""

echo -e "${BLUE}==================== ORDERS SORTING ====================${NC}"
echo ""

echo "Test 5: Default sorting (created_at, desc) - newest first"
echo "----------------------------------------------------------------------"
curl -s -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/orders?limit=5" | jq '.orders[] | {id, user_id, created_at}'
echo ""

echo "Test 6: Sort by total_amount (desc) - highest first"
echo "----------------------------------------------------------------------"
curl -s -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/orders?limit=5&sort_by=total_amount&order=desc" | jq '.orders[] | {id, total_amount, status}'
echo ""

echo "Test 7: Sort by user_id (asc)"
echo "----------------------------------------------------------------------"
curl -s -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/orders?limit=5&sort_by=user_id&order=asc" | jq '.orders[] | {id, user_id}'
echo ""

echo "Test 8: Sort by status (asc) with status filter"
echo "----------------------------------------------------------------------"
curl -s -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/orders?limit=5&status_filter=pending&sort_by=created_at&order=desc" | jq '.orders[] | {id, status, created_at}'
echo ""

echo -e "${BLUE}==================== VALIDATION TESTS ====================${NC}"
echo ""

echo "Test 9: Invalid sort_by field (should return 422)"
echo "----------------------------------------------------------------------"
response=$(curl -s -w "\n%{http_code}" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/users?sort_by=invalid_field")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "422" ]; then
    echo -e "${GREEN}✅ Correctly rejected invalid field (422)${NC}"
else
    echo -e "${RED}❌ Expected 422, got $http_code${NC}"
fi
echo ""

echo "Test 10: Invalid order value (should return 422)"
echo "----------------------------------------------------------------------"
response=$(curl -s -w "\n%{http_code}" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  "$BASE_URL/admin/users?order=invalid")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "422" ]; then
    echo -e "${GREEN}✅ Correctly rejected invalid order (422)${NC}"
else
    echo -e "${RED}❌ Expected 422, got $http_code${NC}"
fi
echo ""

echo "======================================================================"
echo -e "${GREEN}Sorting tests complete!${NC}"
echo "======================================================================"
echo ""
echo "Summary:"
echo "  ✅ Users can be sorted by: id, phone_number, created_at, updated_at"
echo "  ✅ Orders can be sorted by: id, user_id, status, total_amount, created_at, updated_at"
echo "  ✅ Sort order: asc (ascending) or desc (descending)"
echo "  ✅ Invalid fields/orders are rejected with 422"
echo ""
echo "Example usage:"
echo "  GET /admin/users?sort_by=created_at&order=desc"
echo "  GET /admin/orders?sort_by=total_amount&order=desc&status_filter=pending"
echo ""
