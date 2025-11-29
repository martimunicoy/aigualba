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
echo "🔧 Keycloak Configuration:"
echo "  - Admin Console: http://localhost:8080"
echo "  - Admin Username: admin"
echo "  - Admin Password: admin123"
echo "  - Realm: aigualba"
echo ""
echo "👤 Test Users:"
echo "  Admin User:"
echo "    - Username: admin"
echo "    - Password: admin123"
echo "  Regular User:"
echo "    - Username: user" 
echo "    - Password: user123"
echo ""
echo "🔗 Application URLs:"
echo "  - Aigualba Frontend: http://localhost:8051"
echo "  - Aigualba Backend API: http://localhost:8001"
echo "  - Admin Panel: http://localhost:8051/admin"
echo ""
echo "📝 Next Steps:"
echo "1. Access the admin console at http://localhost:8080"
echo "2. Login with admin/admin123"
echo "3. Verify the 'aigualba' realm is imported"
echo "4. Test the admin login at http://localhost:8051/admin"
echo ""
echo "🛠️  Troubleshooting:"
echo "  - If realm import fails, manually import keycloak/realm-import.json"
echo "  - Check logs: docker-compose -f $COMPOSE_FILE logs keycloak"
echo "  - Restart: docker-compose -f $COMPOSE_FILE restart keycloak"
echo "  - Full restart: docker-compose -f $COMPOSE_FILE down && docker-compose -f $COMPOSE_FILE up -d"
echo ""
echo "✨ Setup complete! Happy water quality monitoring!"