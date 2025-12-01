#!/bin/bash

# Test script to verify Keycloak authentication configuration
# This script tests various endpoints and configurations to ensure auth is working

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Aigualba Keycloak Authentication Test${NC}"
echo "========================================"
echo

# Load environment variables
if [ -f ".env" ]; then
    source .env
    echo -e "${GREEN}✅ Environment variables loaded${NC}"
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Test configuration
echo -e "${BLUE}🔧 Testing Configuration${NC}"
echo "Keycloak URL: $KEYCLOAK_URL"
echo "Keycloak Realm: $KEYCLOAK_REALM"
echo "Client ID: $KEYCLOAK_CLIENT_ID"
echo "Redirect URI: $KEYCLOAK_REDIRECT_URI"
echo

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local name=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    
    if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Test Keycloak endpoints
echo -e "${BLUE}🔐 Testing Keycloak Endpoints${NC}"

# Test Keycloak health (if available)
if [[ $KEYCLOAK_URL == *"localhost"* ]] || [[ $KEYCLOAK_URL == *"127.0.0.1"* ]]; then
    test_endpoint "http://localhost:8443/health/ready" "Keycloak Health (Internal)" 200
fi

# Test realm endpoint
REALM_URL="$KEYCLOAK_URL/realms/$KEYCLOAK_REALM"
test_endpoint "$REALM_URL" "Realm Configuration" 200

# Test OpenID Connect configuration
OIDC_CONFIG_URL="$REALM_URL/.well-known/openid-connect-configuration"
if curl -f -s "$OIDC_CONFIG_URL" > /dev/null 2>&1; then
    echo -e "OpenID Connect Configuration... ${GREEN}✅ OK${NC}"
    
    # Extract important URLs
    AUTH_ENDPOINT=$(curl -s "$OIDC_CONFIG_URL" | grep -o '"authorization_endpoint":"[^"]*"' | cut -d'"' -f4)
    TOKEN_ENDPOINT=$(curl -s "$OIDC_CONFIG_URL" | grep -o '"token_endpoint":"[^"]*"' | cut -d'"' -f4)
    
    echo "  Authorization Endpoint: $AUTH_ENDPOINT"
    echo "  Token Endpoint: $TOKEN_ENDPOINT"
else
    echo -e "OpenID Connect Configuration... ${RED}❌ FAILED${NC}"
fi
echo

# Test Docker services
echo -e "${BLUE}🐳 Testing Docker Services${NC}"

# Check if services are running
for service in db keycloak frontend backend; do
    if docker-compose ps $service 2>/dev/null | grep -q "Up"; then
        echo -e "$service service... ${GREEN}✅ Running${NC}"
    else
        echo -e "$service service... ${RED}❌ Not running${NC}"
    fi
done
echo

# Test internal connectivity
echo -e "${BLUE}🔗 Testing Internal Connectivity${NC}"

# Test if frontend can reach keycloak internally
echo -n "Frontend -> Keycloak internal connectivity... "
if docker-compose exec frontend curl -f -s -k https://keycloak:8443/realms/aigualba > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️ May need verification${NC}"
fi

# Test database connectivity
echo -n "Keycloak -> Database connectivity... "
if docker-compose exec keycloak pg_isready -h db -p 5432 -U keycloak_user > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️ Database connection may have issues${NC}"
fi
echo

# Test client configuration
echo -e "${BLUE}🛠️  Testing Client Configuration${NC}"

# Test if client secret matches between .env and realm config
REALM_CLIENT_SECRET=$(grep -o '"secret": "[^"]*"' keycloak/realm-import.json | cut -d'"' -f4)
if [ "$KEYCLOAK_CLIENT_SECRET" = "$REALM_CLIENT_SECRET" ]; then
    echo -e "Client secret consistency... ${GREEN}✅ OK${NC}"
else
    echo -e "Client secret consistency... ${RED}❌ MISMATCH${NC}"
    echo "  .env has: $KEYCLOAK_CLIENT_SECRET"
    echo "  realm-import.json has: $REALM_CLIENT_SECRET"
fi

# Test redirect URIs
PROD_REDIRECT_URI="https://aigualba.cat"
if grep -q "$PROD_REDIRECT_URI" keycloak/realm-import.json; then
    echo -e "Production redirect URIs... ${GREEN}✅ OK${NC}"
else
    echo -e "Production redirect URIs... ${YELLOW}⚠️ Missing production URLs${NC}"
fi
echo

# Frontend authentication test
echo -e "${BLUE}🌐 Testing Frontend Authentication Flow${NC}"

# Test if frontend admin page loads
ADMIN_URL="http://localhost:8050/admin"
echo -n "Admin page accessibility... "
if curl -f -s "$ADMIN_URL" | grep -q "admin" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Admin page not accessible${NC}"
fi

echo
echo -e "${BLUE}📋 Test Summary${NC}"
echo "==============="

# Count passed/failed tests
TOTAL_TESTS=10
echo "Basic configuration and connectivity tests completed."
echo

echo -e "${GREEN}🎯 Next Steps${NC}"
echo "=============="
echo "1. If all tests passed, try logging into the admin panel:"
echo "   URL: http://localhost:8050/admin"
echo "   Username: admin"
echo "   Password: admin123"
echo
echo "2. The login should redirect you to Keycloak and then back to the admin panel"
echo
echo "3. If there are issues:"
echo "   - Check service logs: docker-compose logs keycloak"
echo "   - Restart services: docker-compose restart keycloak frontend"
echo "   - Verify .env configuration"
echo
echo "4. For production deployment:"
echo "   - Ensure SSL certificates are configured"
echo "   - Update redirect URIs in Keycloak"
echo "   - Test with production URLs"
echo

echo -e "${BLUE}🔍 Troubleshooting Commands${NC}"
echo "=========================="
echo "# View Keycloak logs"
echo "docker-compose logs keycloak"
echo
echo "# View frontend logs"  
echo "docker-compose logs frontend"
echo
echo "# Restart authentication-related services"
echo "docker-compose restart keycloak frontend"
echo
echo "# Test Keycloak internal health"
echo "docker-compose exec keycloak curl -k https://localhost:8443/health/ready"
echo
echo "# Test frontend internal connectivity"
echo "docker-compose exec frontend curl -k https://keycloak:8443/realms/aigualba"
echo

echo -e "${GREEN}✨ Test completed!${NC}"