#!/bin/bash
# Test CORS configuration for NMservices Admin API

BASE_URL="${1:-http://localhost:8000}"
ORIGIN="${2:-http://localhost:5173}"
ADMIN_KEY="${3:-admin_secret}"

echo "======================================================================"
echo "🧪 TESTING CORS CONFIGURATION"
echo "======================================================================"
echo "📍 Backend URL: $BASE_URL"
echo "🌐 Origin: $ORIGIN"
echo "🔑 Admin Key: ${ADMIN_KEY:0:4}****"
echo "======================================================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "Test 1: Preflight Request (OPTIONS)"
echo "----------------------------------------------------------------------"

response=$(curl -s -i -X OPTIONS "$BASE_URL/admin/stats" \
  -H "Origin: $ORIGIN" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-Admin-Key")

echo "$response"

if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✅ CORS headers present${NC}"
else
    echo -e "${RED}❌ CORS headers missing${NC}"
fi

echo ""
echo "Test 2: Actual Request (GET with Admin Key)"
echo "----------------------------------------------------------------------"

response=$(curl -s -i -X GET "$BASE_URL/admin/stats" \
  -H "Origin: $ORIGIN" \
  -H "X-Admin-Key: $ADMIN_KEY")

echo "$response"

if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✅ CORS works for actual request${NC}"
else
    echo -e "${RED}❌ CORS not working${NC}"
fi

if echo "$response" | grep -q "total_users"; then
    echo -e "${GREEN}✅ API response valid${NC}"
else
    echo -e "${YELLOW}⚠️  Check admin key or API endpoint${NC}"
fi

echo ""
echo "======================================================================"
echo "Test complete!"
echo "======================================================================"
