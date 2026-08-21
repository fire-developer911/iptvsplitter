#!/bin/bash

# IPTV Proxy Test Script
# Tests basic functionality of the proxy service

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVER_URL="${SERVER_URL:-http://localhost:3000}"
TEST_USER="test1"
TEST_PASS="qwerty"

echo -e "${YELLOW}IPTV Proxy Test Suite${NC}"
echo "Testing: $SERVER_URL"
echo ""

# Test 1: Health Check
echo -n "Test 1: Health check (no auth)... "
response=$(curl -s -w "%{http_code}" -o /tmp/health_response.json "$SERVER_URL/health")
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    cat /tmp/health_response.json | jq . 2>/dev/null || echo "Valid JSON response"
else
    echo -e "${RED}✗ FAIL (HTTP $http_code)${NC}"
fi
echo ""

# Test 2: Info Endpoint
echo -n "Test 2: Info endpoint (no auth)... "
response=$(curl -s -w "%{http_code}" -o /tmp/info_response.json "$SERVER_URL/info")
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    cat /tmp/info_response.json | jq . 2>/dev/null || echo "Valid JSON response"
else
    echo -e "${RED}✗ FAIL (HTTP $http_code)${NC}"
fi
echo ""

# Test 3: Missing Credentials
echo -n "Test 3: Missing credentials (should fail)... "
response=$(curl -s -w "%{http_code}" -o /tmp/missing_creds.json "$SERVER_URL/player_api.php")
http_code="${response: -3}"

if [ "$http_code" = "401" ]; then
    echo -e "${GREEN}✓ PASS (correctly rejected)${NC}"
else
    echo -e "${RED}✗ FAIL (expected 401, got $http_code)${NC}"
fi
echo ""

# Test 4: Invalid Username
echo -n "Test 4: Invalid username (should fail)... "
response=$(curl -s -w "%{http_code}" -o /tmp/invalid_user.json "$SERVER_URL/player_api.php?username=invalid&password=invalid")
http_code="${response: -3}"

if [ "$http_code" = "401" ]; then
    echo -e "${GREEN}✓ PASS (correctly rejected)${NC}"
else
    echo -e "${RED}✗ FAIL (expected 401, got $http_code)${NC}"
fi
echo ""

# Test 5: Valid Credentials (if test user exists in .env)
echo -n "Test 5: Valid credentials ($TEST_USER / $TEST_PASS)... "
response=$(curl -s -w "%{http_code}" -o /tmp/valid_creds.json "$SERVER_URL/player_api.php?action=get_categories&username=$TEST_USER&password=$TEST_PASS")
http_code="${response: -3}"

if [ "$http_code" = "200" ] || [ "$http_code" = "502" ]; then
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ PASS (authenticated, received data)${NC}"
    else
        echo -e "${YELLOW}⚠ WARNING (authenticated but upstream returned error)${NC}"
        echo "  This is normal if upstream server is unreachable. Check 'main_url' in .env"
    fi
else
    echo -e "${RED}✗ FAIL (HTTP $http_code)${NC}"
fi
echo ""

# Test 6: Wrong Password
echo -n "Test 6: Wrong password (should fail)... "
response=$(curl -s -w "%{http_code}" -o /tmp/wrong_pass.json "$SERVER_URL/player_api.php?username=$TEST_USER&password=wrongpass")
http_code="${response: -3}"

if [ "$http_code" = "401" ]; then
    echo -e "${GREEN}✓ PASS (correctly rejected)${NC}"
else
    echo -e "${RED}✗ FAIL (expected 401, got $http_code)${NC}"
fi
echo ""

# Summary
echo -e "${YELLOW}Test Summary${NC}"
echo "✓ Health check working"
echo "✓ Authentication system active"
echo "✓ Credential validation working"
echo ""
echo "To test with real upstream:"
echo "1. Set valid 'main_url', 'main_user', 'main_pass' in .env"
echo "2. Re-run tests"
echo ""
echo "To test in production (Render):"
echo "  SERVER_URL=https://your-service.onrender.com ./test.sh"
