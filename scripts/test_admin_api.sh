#!/bin/bash
# Test script for Admin API endpoints using curl

BASE_URL="${1:-http://192.168.1.191:8000}"
ADMIN_KEY="${2:-admin_secret}"

echo "======================================================================"
echo "🧪 TESTING ADMIN API"
echo "======================================================================"
echo "📍 Base URL: $BASE_URL"
echo "🔑 Admin Key: ${ADMIN_KEY:0:4}****"
echo "======================================================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Helper function to run test
run_test() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"

    echo -n "📝 $name... "

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "X-Admin-Key: $ADMIN_KEY" \
            -H "Content-Type: application/json" \
            "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "X-Admin-Key: $ADMIN_KEY" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✅ PASSED${NC} (HTTP $http_code)"
        ((PASSED++))
        echo "$body"
    else
        echo -e "${RED}❌ FAILED${NC} (HTTP $http_code)"
        ((FAILED++))
        echo "$body"
    fi
    echo ""
}

echo ""
echo "Starting tests..."
echo ""

# Test 1: Health check
run_test "Health Check" "GET" "/"

# Test 2: Get statistics
run_test "Get Statistics" "GET" "/admin/stats"

# Test 3: List users
run_test "List Users" "GET" "/admin/users"

# Test 4: Create user
echo "📝 Creating test user..."
USER_RESPONSE=$(curl -s -X POST \
    -H "X-Admin-Key: $ADMIN_KEY" \
    -H "Content-Type: application/json" \
    -d '{"phone_number":"+998901234567"}' \
    "$BASE_URL/admin/users")

if echo "$USER_RESPONSE" | grep -q '"id"'; then
    USER_ID=$(echo "$USER_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    echo -e "${GREEN}✅ PASSED${NC} - Created user ID: $USER_ID"
    ((PASSED++))
elif echo "$USER_RESPONSE" | grep -q "already exists"; then
    # Get existing user
    USERS_LIST=$(curl -s -H "X-Admin-Key: $ADMIN_KEY" "$BASE_URL/admin/users?limit=100")
    USER_ID=$(echo "$USERS_LIST" | grep -o '"phone_number":"+998901234567"' -A 5 | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
    echo -e "${YELLOW}⚠️  Using existing user ID: $USER_ID${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAILED${NC}"
    ((FAILED++))
fi
echo ""

# Test 5: Get user by ID
if [ -n "$USER_ID" ]; then
    run_test "Get User by ID" "GET" "/admin/users/$USER_ID"
fi

# Test 6: Create order
if [ -n "$USER_ID" ]; then
    echo "📝 Creating test order..."
    ORDER_RESPONSE=$(curl -s -X POST \
        -H "X-Admin-Key: $ADMIN_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\":$USER_ID,\"status\":\"pending\",\"total_amount\":300.00,\"notes\":\"Test order\"}" \
        "$BASE_URL/admin/orders")

    if echo "$ORDER_RESPONSE" | grep -q '"id"'; then
        ORDER_ID=$(echo "$ORDER_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
        echo -e "${GREEN}✅ PASSED${NC} - Created order ID: $ORDER_ID"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((FAILED++))
    fi
    echo ""
fi

# Test 7: Get order by ID
if [ -n "$ORDER_ID" ]; then
    run_test "Get Order by ID" "GET" "/admin/orders/$ORDER_ID"
fi

# Test 8: List orders
run_test "List Orders" "GET" "/admin/orders"

# Test 9: Get user's orders
if [ -n "$USER_ID" ]; then
    run_test "Get User's Orders" "GET" "/admin/users/$USER_ID/orders"
fi

# Test 10: Update order
if [ -n "$ORDER_ID" ]; then
    run_test "Update Order" "PATCH" "/admin/orders/$ORDER_ID" \
        '{"status":"completed","total_amount":350.00,"notes":"Updated"}'
fi

# Test 11: List orders with filter
run_test "List Completed Orders" "GET" "/admin/orders?status_filter=completed"

# Test 12: Delete order
if [ -n "$ORDER_ID" ]; then
    run_test "Delete Order" "DELETE" "/admin/orders/$ORDER_ID"
fi

# Test 13: Delete user
if [ -n "$USER_ID" ]; then
    run_test "Delete User (CASCADE)" "DELETE" "/admin/users/$USER_ID"
fi

# Test 14: Verify deletion
if [ -n "$USER_ID" ]; then
    echo -n "📝 Verify User Deletion... "
    response=$(curl -s -w "\n%{http_code}" \
        -H "X-Admin-Key: $ADMIN_KEY" \
        "$BASE_URL/admin/users/$USER_ID")
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" = "404" ]; then
        echo -e "${GREEN}✅ PASSED${NC} (User correctly deleted)"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC} (User still exists)"
        ((FAILED++))
    fi
    echo ""
fi

# Final statistics
run_test "Final Statistics" "GET" "/admin/stats"

# Summary
echo "======================================================================"
echo -e "📊 RESULTS: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo "======================================================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed!${NC}"
    exit 1
fi
