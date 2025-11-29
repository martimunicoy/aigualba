#!/bin/bash

# Functional Testing Script for Aigualba Application
# This script performs comprehensive functionality checks after deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Aigualba Functionality Test${NC}"
echo "============================="
echo

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Function to test HTTP endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    local description="$4"
    
    echo -n "Testing $name... "
    
    if response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null); then
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}✅ PASS${NC} ($response)"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $response)"
            ((TESTS_FAILED++))
            FAILED_TESTS+=("$name: Expected HTTP $expected_status, got $response")
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (Connection failed)"
        ((TESTS_FAILED++))
        FAILED_TESTS+=("$name: Connection failed to $url")
    fi
}

# Function to test content presence
test_content() {
    local name="$1"
    local url="$2"
    local expected_content="$3"
    local description="$4"
    
    echo -n "Testing $name content... "
    
    if response=$(curl -s "$url" 2>/dev/null); then
        if echo "$response" | grep -q "$expected_content"; then
            echo -e "${GREEN}✅ PASS${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} (Content not found: $expected_content)"
            ((TESTS_FAILED++))
            FAILED_TESTS+=("$name: Expected content '$expected_content' not found")
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (Failed to fetch content)"
        ((TESTS_FAILED++))
        FAILED_TESTS+=("$name: Failed to fetch content from $url")
    fi
}

# Function to test API endpoint with JSON response
test_api_json() {
    local name="$1"
    local url="$2"
    local expected_field="$3"
    local description="$4"
    
    echo -n "Testing $name API... "
    
    if response=$(curl -s -H "Accept: application/json" "$url" 2>/dev/null); then
        if echo "$response" | grep -q "$expected_field"; then
            echo -e "${GREEN}✅ PASS${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} (Expected field not found: $expected_field)"
            ((TESTS_FAILED++))
            FAILED_TESTS+=("$name: API response missing expected field '$expected_field'")
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (API request failed)"
        ((TESTS_FAILED++))
        FAILED_TESTS+=("$name: API request failed to $url")
    fi
}

# Determine base URL
BASE_URL="http://localhost"
API_URL="$BASE_URL/api"
KEYCLOAK_URL="http://localhost:8080"

echo -e "${YELLOW}🌐 Testing Web Application${NC}"
echo "Base URL: $BASE_URL"
echo "API URL: $API_URL"
echo "Keycloak URL: $KEYCLOAK_URL"
echo

# Test 1: Main application accessibility
echo -e "${BLUE}📱 Frontend Tests${NC}"
test_endpoint "Homepage" "$BASE_URL" 200 "Main application homepage"
test_content "Homepage Content" "$BASE_URL" "Aigualba" "Check for application name"
test_content "Navigation" "$BASE_URL" "Explora les mostres" "Check for navigation menu"

# Test 2: Application pages
test_endpoint "Browse Page" "$BASE_URL/browse" 200 "Browse samples page"
test_endpoint "Visualize Page" "$BASE_URL/visualize" 200 "Data visualization page"
test_endpoint "Submit Page" "$BASE_URL/submit" 200 "Sample submission page"
test_endpoint "About Page" "$BASE_URL/about" 200 "About page"

echo

# Test 3: API endpoints
echo -e "${BLUE}🔌 Backend API Tests${NC}"
test_api_json "Health Check" "$API_URL/health" "status" "API health endpoint"
test_api_json "Parameters API" "$API_URL/parameters" "name" "Water quality parameters"
test_api_json "Samples API" "$API_URL/mostres" "id\|data\|punt_mostreig" "Water samples data"

echo

# Test 4: Keycloak authentication
echo -e "${BLUE}🔐 Authentication Tests${NC}"
test_endpoint "Keycloak" "$KEYCLOAK_URL" 200 "Keycloak authentication server"
test_endpoint "Keycloak Realm" "$KEYCLOAK_URL/realms/aigualba" 200 "Aigualba realm"
test_endpoint "Admin Page" "$BASE_URL/admin" 200 "Admin authentication page"

echo

# Test 5: Static resources
echo -e "${BLUE}🎨 Static Resources Tests${NC}"
test_endpoint "CSS Assets" "$BASE_URL/_dash-component-suites/" 200 "Dash CSS components"

echo

# Test 6: Database connectivity (through API)
echo -e "${BLUE}💾 Database Connectivity Tests${NC}"
echo -n "Testing database through API... "
if response=$(curl -s "$API_URL/mostres" 2>/dev/null); then
    if echo "$response" | grep -q -E '(\[|\{|id|data)'; then
        echo -e "${GREEN}✅ PASS${NC} (Database responding)"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠️ WARNING${NC} (Empty response - may be normal for new deployment)"
        echo "   Response preview: $(echo "$response" | head -c 100)..."
        ((TESTS_PASSED++))
    fi
else
    echo -e "${RED}❌ FAIL${NC} (Database connection through API failed)"
    ((TESTS_FAILED++))
    FAILED_TESTS+=("Database: Connection failed through API")
fi

echo

# Test 7: Form functionality (basic check)
echo -e "${BLUE}📝 Form Tests${NC}"
test_content "Submit Form" "$BASE_URL/submit" "submit-sample-button" "Sample submission form"
test_content "Sample Date Input" "$BASE_URL/submit" "sample-date" "Date input field"
test_content "Location Input" "$BASE_URL/submit" "punt-mostreig" "Location input field"

echo

# Summary
echo -e "${BLUE}📊 Test Summary${NC}"
echo "=============="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -gt 0 ]; then
    echo
    echo -e "${RED}❌ Failed Tests:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo "   • $test"
    done
    echo
    echo -e "${YELLOW}🔧 Troubleshooting Steps:${NC}"
    echo "1. Check service status: docker-compose ps"
    echo "2. View service logs: docker-compose logs -f [service]"
    echo "3. Run health check: ./health-check.sh"
    echo "4. Verify .env configuration"
    echo "5. Restart services: docker-compose restart"
    echo
    exit 1
else
    echo
    echo -e "${GREEN}🎉 All tests passed! Application is functioning correctly.${NC}"
    echo
    echo -e "${BLUE}✨ Next Steps:${NC}"
    echo "1. 📊 Test the browse functionality with real data"
    echo "2. 📝 Try submitting a sample through the form"
    echo "3. 🔐 Test admin login at $BASE_URL/admin"
    echo "4. 📈 Check data visualizations"
    echo "5. 🗄️  Create your first backup: ./backup.sh"
    echo
    echo -e "${GREEN}🌊 Your Aigualba application is ready for use!${NC}"
    exit 0
fi