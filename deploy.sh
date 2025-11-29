#!/bin/bash

# Production deployment script for Aigualba
# This script helps deploy Aigualba in production environments

set -e  # Exit on any error

echo "🚀 Aigualba Production Deployment Script"
echo "=========================================="
echo

# Check for required commands
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ Error: $1 is not installed. Please install $1 and try again."
        exit 1
    fi
}

echo "🔍 Checking prerequisites..."
check_command "docker"
check_command "docker-compose"
echo "✅ Prerequisites check passed"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "⚠️  IMPORTANT: Please edit the .env file with your production values before continuing!"
        echo "   - Set secure passwords for all services"
        echo "   - Update domain names and URLs"
        echo "   - Configure SSL certificates if using HTTPS"
        echo
        read -p "Press Enter after you have configured the .env file..."
    else
        echo "❌ Error: .env.example file not found. Cannot create .env file."
        exit 1
    fi
else
    echo "✅ .env file exists"
fi

# Check environment variables
echo "🔧 Validating environment variables..."
if ! grep -q "change_me_in_production" .env 2>/dev/null; then
    echo "✅ Default passwords appear to have been changed"
else
    echo "⚠️  WARNING: Some default passwords still contain 'change_me_in_production'"
    echo "   Please update all passwords in .env file for security!"
    read -p "Continue anyway? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        exit 1
    fi
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down || true

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose pull

# Build services
echo "🏗️  Building services..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
health_ok=true

services=("nginx" "db" "backend" "frontend" "keycloak")
for service in "${services[@]}"; do
    if docker-compose ps "$service" | grep -q "Up"; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Not running"
        health_ok=false
    fi
done

if [ "$health_ok" = false ]; then
    echo
    echo "❌ Some services are not running. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi

# Setup Keycloak if needed
echo
echo "🔐 Setting up Keycloak authentication..."
echo "⏳ Waiting for Keycloak to be ready..."
sleep 30

# Check if Keycloak is accessible and try to import realm
if curl -f http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Keycloak is accessible"
    # The realm should be imported automatically via the volume mount
    echo "✅ Keycloak realm should be imported automatically"
    echo "💡 If realm import fails, you can run: ./setup-keycloak.sh"
else
    echo "⚠️  Keycloak may still be starting. Please wait a few minutes."
    echo "💡 You can also run: ./setup-keycloak.sh to ensure proper setup"
fi

# Display deployment information
echo
echo "🎉 Deployment completed successfully!"
echo "====================================="
echo
echo "📊 Service Status:"
docker-compose ps
echo
echo "🌐 Application URLs:"
echo "   - Main Application: http://localhost"
echo "   - Admin Panel: http://localhost/admin"
echo "   - Backend API: http://localhost/api"
echo "   - Keycloak Admin: http://localhost:8080"
echo
echo "👤 Default Admin Credentials:"
echo "   - Username: admin"
echo "   - Password: admin123"
echo
echo "🔧 Useful Commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Restart services: docker-compose restart"
echo "   - Stop services: docker-compose down"
echo "   - Update application: git pull && docker-compose up --build -d"
echo
echo "📚 Additional Documentation:"
echo "   - Deployment Guide: DEPLOYMENT.md"
echo "   - Admin Setup: ADMIN_SETUP.md"
echo "   - Main README: README.md"
echo

# Security recommendations
echo "🔐 IMPORTANT SECURITY REMINDERS:"
echo "  1. Change default passwords in .env file"
echo "  2. Configure HTTPS with SSL certificates"
echo "  3. Close unnecessary ports in firewall"
echo "  4. Regular backups of database"
echo "  5. Monitor application logs"
echo
echo "🎯 Next Steps:"
echo "  1. Test the application functionality"
echo "  2. Configure monitoring and backups"
echo "  3. Set up SSL/HTTPS (see DEPLOYMENT.md)"
echo "  4. Review security settings"
echo "  5. For development, use: docker-compose -f docker-compose.dev.yml up"
echo

echo "✨ Deployment script completed!"