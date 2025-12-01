#!/bin/bash

# Keycloak Setup Script for Aigualba
# This script helps set up Keycloak for the Aigualba water quality management system
#
# Usage:
#   ./setup-keycloak.sh          # Auto-detects environment (production/development)
#   ./setup-keycloak.sh --dev    # Force development mode

echo "🌊 Aigualba Keycloak Setup"
echo "=========================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Create network if it doesn't exist
echo "🔌 Creating Docker network..."
docker network create aigualba_network 2>/dev/null || echo "Network already exists"

# Detect environment and use appropriate compose file
COMPOSE_FILE="docker-compose.yml"
if [ -f ".env" ] && grep -q "DASH_DEBUG=1" .env 2>/dev/null; then
    COMPOSE_FILE="docker-compose.dev.yml"
    echo "🔍 Development environment detected"
elif [ "$1" = "--dev" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    echo "🔍 Development mode forced"
else
    echo "🔍 Production environment detected"
fi

echo "📝 Using compose file: $COMPOSE_FILE"

# Check if database is already running
if docker-compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
    echo "✅ Database is already running"
    echo "🚀 Starting Keycloak service..."
    docker-compose -f "$COMPOSE_FILE" up -d keycloak
else
    echo "🚀 Starting database and Keycloak..."
    docker-compose -f "$COMPOSE_FILE" up -d db keycloak
fi

echo "⏳ Waiting for Keycloak to start..."
sleep 45

# Check if Keycloak is running
if curl -f http://localhost:8080/health/ready > /dev/null 2>&1; then
    echo "✅ Keycloak is running"
elif curl -f http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Keycloak is running (health endpoint not available yet)"
else
    echo "⚠️  Keycloak might still be starting. This can take a few minutes."
    echo "   You can check status with: docker-compose -f $COMPOSE_FILE logs keycloak"
fi

echo ""
# Read configuration from .env file
if [ -f ".env" ]; then
    KEYCLOAK_ADMIN_PASSWORD=$(grep "^KEYCLOAK_ADMIN_PASSWORD=" .env | cut -d'=' -f2)
    KEYCLOAK_CLIENT_SECRET=$(grep "^KEYCLOAK_CLIENT_SECRET=" .env | cut -d'=' -f2)
    KEYCLOAK_URL=$(grep "^KEYCLOAK_URL=" .env | cut -d'=' -f2)
    
    # Use default values if not found in .env
    KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD:-"admin123"}
    KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET:-"aigualba-frontend-secret-123"}
    KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
else
    echo "⚠️  .env file not found, using default values"
    KEYCLOAK_ADMIN_PASSWORD="admin123"
    KEYCLOAK_CLIENT_SECRET="aigualba-frontend-secret-123"
    KEYCLOAK_URL="http://localhost:8080"
fi

echo "🔧 Keycloak Configuration:"
echo "  - Admin Console: $KEYCLOAK_URL"
echo "  - Admin Username: admin"
echo "  - Admin Password: $KEYCLOAK_ADMIN_PASSWORD"
echo "  - Realm: aigualba"
echo "  - Client ID: aigualba-frontend"
echo "  - Client Secret: $KEYCLOAK_CLIENT_SECRET"
echo ""
echo "👤 Admin User Credentials:"
echo "  - Username: admin"
echo "  - Password: admin123 (configured in realm)"
echo ""
echo "🔗 Application URLs:"
if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
    echo "  - Aigualba Frontend: http://localhost:8050"
    echo "  - Aigualba Backend API: http://localhost:8000"
    echo "  - Admin Panel: http://localhost:8050/admin"
    echo "  - Keycloak Admin: http://localhost:8080"
else
    echo "  - Aigualba Frontend: https://aigualba.cat"
    echo "  - Aigualba Backend API: https://aigualba.cat/api"
    echo "  - Admin Panel: https://aigualba.cat/admin"
    echo "  - Keycloak Admin: https://auth.aigualba.cat (restricted to local/private networks)"
fi
echo ""
echo "🔒 Security Configuration:"
if [[ "$KEYCLOAK_URL" != *"localhost"* ]]; then
    echo "  - Keycloak admin console (auth.aigualba.cat) is restricted to:"
    echo "    * Localhost (127.0.0.1, ::1)"
    echo "    * Private networks (10.x.x.x, 172.16-31.x.x, 192.168.x.x)"
    echo "  - Authentication endpoint remains publicly accessible for user login"
    echo "  - External users will receive 403 Forbidden when accessing admin console"
fi
echo ""
echo "📝 Next Steps:"
echo "1. Access the Keycloak admin console at $KEYCLOAK_URL"
if [[ "$KEYCLOAK_URL" != *"localhost"* ]]; then
    echo "   NOTE: Admin console only accessible from local/private networks"
fi
echo "2. Login with admin/$KEYCLOAK_ADMIN_PASSWORD"
echo "3. Verify the 'aigualba' realm is imported with correct client secret"
if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
    echo "4. Test the admin login at http://localhost:8050/admin with admin/admin123"
else
    echo "4. Test the admin login at https://aigualba.cat/admin with admin/admin123"
fi
echo ""
echo "🛠️  Troubleshooting:"
echo "  - If realm import fails, manually import keycloak/realm-import.json"
echo "  - Check logs: docker-compose -f $COMPOSE_FILE logs keycloak"
echo "  - Restart: docker-compose -f $COMPOSE_FILE restart keycloak"
echo "  - Full restart: docker-compose -f $COMPOSE_FILE down && docker-compose -f $COMPOSE_FILE up -d"
echo ""
echo "✨ Setup complete! Happy water quality monitoring!"