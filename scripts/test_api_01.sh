#!/bin/bash

# NMservices API Remote Testing Script
# This script tests all API endpoints remotely using curl
# Usage: ./test_api.sh [OPTIONS]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_HOST="127.0.0.1"
DEFAULT_PORT="8000"
DEFAULT_API_KEY="test_secret"
DEFAULT_TIMEOUT=10

# Parse command line arguments
HOST="${HOST:-$DEFAULT_HOST}"
PORT="${PORT:-$DEFAULT_PORT}"
API_KEY="${API_KEY:-$DEFAULT_API_KEY}"
TIMEOUT="${TIMEOUT:-$DEFAULT_TIMEOUT}"
VERBOSE=false

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Remote API testing script for NMservices.

OPTIONS:
    -h, --host HOST         API host (default: $DEFAULT_HOST)
    -p, --port PORT         API port (default: $DEFAULT_PORT)
    -k, --key API_KEY       X-API-Key header value (default: $DEFAULT_API_KEY)
    -t, --timeout SECONDS   Request timeout (default: $DEFAULT_TIMEOUT)
    -v, --verbose           Enable verbose output
    --help                  Show this help message

ENVIRONMENT VARIABLES:
    HOST                    API host
    PORT                    API port
    API_KEY                 X-API-Key value
    TIMEOUT                 Request timeout

EXAMPLES:
    # Test local server with defaults
    $0

    # Test remote server
    $0 --host api.example.com --port 443 --key "your_api_key"

    # Using environment variables
    HOST=192.168.1.100 PORT=8080 API_KEY=secret123 $0

    # Verbose mode
    $0 -v

EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -k|--key)
            API_KEY="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            ;;
    esac
done

# Build base URL
BASE_URL="http://${HOST}:${PORT}"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Print header
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  NMservices API Remote Testing${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "Base URL:     ${YELLOW}${BASE_URL}${NC}"
    echo -e "API Key:      ${YELLOW}${API_KEY:0:4}****${NC}"
    echo -e "Timeout:      ${YELLOW}${TIMEOUT}s${NC}"
    echo ""
}

# Print test result
print_result() {
    local test_name="$1"
    local status="$2"
    local message="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if [ "$status" = "PASS" ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo -e "${GREEN}✓${NC} ${test_name}"
        [ "$VERBOSE" = true ] && echo -e "  ${message}"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "${RED}✗${NC} ${test_name}"
        echo -e "  ${RED}${message}${NC}"
    fi
}

# Print footer
print_footer() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "Total tests:  ${TOTAL_TESTS}"
    echo -e "Passed:       ${GREEN}${PASSED_TESTS}${NC}"
    echo -e "Failed:       ${RED}${FAILED_TESTS}${NC}"
    echo -e "${BLUE}========================================${NC}"

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}

# Make HTTP request
make_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local use_auth="$4"

    local url="${BASE_URL}${endpoint}"
    local curl_args=(-s -w "\n%{http_code}" -m "$TIMEOUT")

    if [ "$VERBOSE" = true ]; then
        curl_args+=(-v)
    fi

    if [ "$method" = "POST" ]; then
        curl_args+=(-X POST)
        curl_args+=(-H "Content-Type: application/json")
        if [ -n "$data" ]; then
            curl_args+=(-d "$data")
        fi
    fi

    if [ "$use_auth" = "true" ]; then
        curl_args+=(-H "X-API-Key: ${API_KEY}")
    fi

    curl_args+=("$url")

    curl "${curl_args[@]}" 2>&1
}

# Test 1: Health check (public endpoint)
test_health_check() {
    echo ""
    echo -e "${YELLOW}[1/6]${NC} Testing health check endpoint..."

    response=$(make_request "GET" "/" "" "false")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"message".*"NoMus API is running"'; then
            print_result "GET / - Health check" "PASS" "API is running"
        else
            print_result "GET / - Health check" "FAIL" "Unexpected response body: $body"
        fi
    else
        print_result "GET / - Health check" "FAIL" "HTTP $http_code (expected 200)"
    fi
}

# Test 2: Register without auth (should fail)
test_register_no_auth() {
    echo ""
    echo -e "${YELLOW}[2/6]${NC} Testing security - register without auth..."

    local data='{"phone_number": "+998900000000"}'
    response=$(make_request "POST" "/register" "$data" "false")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "403" ]; then
        if echo "$body" | grep -q '"detail".*"Could not validate credentials"'; then
            print_result "POST /register - No auth" "PASS" "Correctly rejected (403)"
        else
            print_result "POST /register - No auth" "FAIL" "Wrong error message: $body"
        fi
    else
        print_result "POST /register - No auth" "FAIL" "HTTP $http_code (expected 403)"
    fi
}

# Test 3: Register with wrong auth (should fail)
test_register_wrong_auth() {
    echo ""
    echo -e "${YELLOW}[3/6]${NC} Testing security - register with wrong auth..."

    local data='{"phone_number": "+998900000000"}'
    local old_api_key="$API_KEY"
    API_KEY="wrong_password"

    response=$(make_request "POST" "/register" "$data" "true")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    API_KEY="$old_api_key"

    if [ "$http_code" = "403" ]; then
        if echo "$body" | grep -q '"detail".*"Could not validate credentials"'; then
            print_result "POST /register - Wrong auth" "PASS" "Correctly rejected (403)"
        else
            print_result "POST /register - Wrong auth" "FAIL" "Wrong error message: $body"
        fi
    else
        print_result "POST /register - Wrong auth" "FAIL" "HTTP $http_code (expected 403)"
    fi
}

# Test 4: Register with valid auth (should succeed)
test_register_success() {
    echo ""
    echo -e "${YELLOW}[4/6]${NC} Testing user registration (legacy endpoint)..."

    local data='{"phone_number": "+998901234567"}'
    response=$(make_request "POST" "/register" "$data" "true")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"status".*"ok"' && echo "$body" | grep -q '"user_id"'; then
            local user_id=$(echo "$body" | grep -o '"user_id":[0-9]*' | grep -o '[0-9]*')
            print_result "POST /register - Success" "PASS" "User registered with ID: $user_id"
        else
            print_result "POST /register - Success" "FAIL" "Invalid response structure: $body"
        fi
    else
        print_result "POST /register - Success" "FAIL" "HTTP $http_code (expected 200). Body: $body"
    fi
}

# Test 5: Register validation error
test_register_validation() {
    echo ""
    echo -e "${YELLOW}[5/6]${NC} Testing validation - empty request body..."

    local data='{}'
    response=$(make_request "POST" "/register" "$data" "true")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "422" ]; then
        print_result "POST /register - Validation error" "PASS" "Correctly rejected invalid data (422)"
    else
        print_result "POST /register - Validation error" "FAIL" "HTTP $http_code (expected 422)"
    fi
}

# Test 6: Create order (should succeed)
test_create_order() {
    echo ""
    echo -e "${YELLOW}[6/6]${NC} Testing order creation (legacy endpoint)..."

    local data='{"user_id": 101, "tariff_code": "standard_300"}'
    response=$(make_request "POST" "/create_order" "$data" "true")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"status".*"ok"' && echo "$body" | grep -q '"order_id"'; then
            local order_id=$(echo "$body" | grep -o '"order_id":[0-9]*' | grep -o '[0-9]*')
            print_result "POST /create_order - Success" "PASS" "Order created with ID: $order_id"
        else
            print_result "POST /create_order - Success" "FAIL" "Invalid response structure: $body"
        fi
    else
        print_result "POST /create_order - Success" "FAIL" "HTTP $http_code (expected 200). Body: $body"
    fi
}

# Check if curl is available
check_curl() {
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}Error: curl is not installed${NC}"
        echo "Please install curl:"
        echo "  Ubuntu/Debian: sudo apt-get install curl"
        echo "  CentOS/RHEL:   sudo yum install curl"
        echo "  macOS:         brew install curl"
        exit 1
    fi
}

# Main execution
main() {
    check_curl
    print_header

    # Run all tests
    test_health_check
    test_register_no_auth
    test_register_wrong_auth
    test_register_success
    test_register_validation
    test_create_order

    print_footer
}

# Run main function
main
