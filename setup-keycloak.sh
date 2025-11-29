#!/bin/bash

# Keycloak Setup Script for Aigualba
# This script helps set up Keycloak for the Aigualba water quality management system

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

# Start Keycloak with docker-compose
echo "🚀 Starting Keycloak..."
docker-compose -f docker-compose.keycloak.yml up -d

echo "⏳ Waiting for Keycloak to start..."
sleep 30

# Check if Keycloak is running
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Keycloak is running"
else
    echo "⚠️  Keycloak might still be starting. This can take a few minutes."
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
echo "  - Check logs: docker-compose -f docker-compose.keycloak.yml logs"
echo "  - Restart: docker-compose -f docker-compose.keycloak.yml restart"
echo ""
echo "✨ Setup complete! Happy water quality monitoring!"