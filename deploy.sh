#!/bin/bash

# Aigualba deployment script for both development and production environments
# This script helps deploy Aigualba in various environments

set -e  # Exit on any error

echo "🚀 Aigualba Deployment Script"
echo "============================="
echo

# Ask for deployment environment
echo "Please select deployment environment:"
echo "1) Development (local setup with HTTP)"
echo "2) Production (HTTPS with SSL certificates)"
echo
read -p "Enter your choice [1-2]: " env_choice

case $env_choice in
    1)
        DEPLOY_ENV="development"
        COMPOSE_FILE="docker-compose.dev.yml"
        echo "📝 Selected: Development environment"
        ;;
    2)
        DEPLOY_ENV="production" 
        COMPOSE_FILE="docker-compose.yml"
        echo "📝 Selected: Production environment"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again and select 1 or 2."
        exit 1
        ;;
esac
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

# Check if .env file exists (only needed for production)
if [ "$DEPLOY_ENV" = "production" ]; then
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
else
    echo "📝 Development mode: Using built-in environment variables from docker-compose.dev.yml"
fi

# Check environment variables (production only)
if [ "$DEPLOY_ENV" = "production" ]; then
    echo "🔧 Validating environment variables..."

    # Check for placeholder passwords
    if ! grep -q "change_me" .env 2>/dev/null; then
        echo "✅ Default passwords appear to have been changed"
    else
        echo "⚠️  WARNING: Some default passwords still contain 'change_me'"
        echo "   Please update all passwords in .env file for security!"
        read -p "Continue anyway? (y/N): " confirm
        if [[ $confirm != [yY] ]]; then
            exit 1
        fi
    fi
else
    echo "🔧 Development mode: Using default secure development credentials"
fi

# Check for SSL certificate configuration (production only)
if [ "$DEPLOY_ENV" = "production" ]; then
    if grep -q "https://" .env 2>/dev/null; then
        echo "🔍 HTTPS configuration detected, checking SSL certificate settings..."
        
        if ! grep -q "KC_HTTPS_CERTIFICATE_FILE=" .env || ! grep -q "KC_HTTPS_CERTIFICATE_KEY_FILE=" .env; then
            echo "⚠️  WARNING: HTTPS URLs detected but SSL certificate variables missing"
            echo "   Adding default SSL certificate paths to .env file..."
            
            # Add SSL certificate variables if not present
            if ! grep -q "KC_HTTPS_CERTIFICATE_FILE=" .env; then
                echo "KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/certs/live/aigualba.cat/fullchain.pem" >> .env
            fi
            if ! grep -q "KC_HTTPS_CERTIFICATE_KEY_FILE=" .env; then
                echo "KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/certs/live/aigualba.cat/privkey.pem" >> .env
            fi
            
            echo "✅ SSL certificate paths added to .env file"
            echo "💡 Make sure your SSL certificates are properly mounted in docker-compose.yml"
        else
            echo "✅ SSL certificate configuration found"
        fi
    else
        echo "✅ HTTP configuration detected"
    fi
else
    echo "✅ Development mode: Using HTTP only (no SSL certificates required)"
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose -f $COMPOSE_FILE down || true

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose -f $COMPOSE_FILE pull

# Build services
echo "🏗️  Building services..."
docker-compose -f $COMPOSE_FILE build

# Start services
echo "🚀 Starting services..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
health_ok=true

services=("nginx" "db" "backend" "frontend" "keycloak")
for service in "${services[@]}"; do
    if docker-compose -f $COMPOSE_FILE ps "$service" | grep -q "Up"; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Not running"
        health_ok=false
    fi
done

if [ "$health_ok" = false ]; then
    echo
    echo "❌ Some services are not running. Check logs with:"
    echo "   docker-compose -f $COMPOSE_FILE logs"
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
docker-compose -f $COMPOSE_FILE ps
echo
echo "🌐 Application URLs:"
if [ "$DEPLOY_ENV" = "production" ]; then
    # Read from .env to show actual configured URLs
    if [ -f ".env" ]; then
        KEYCLOAK_URL=$(grep "^KEYCLOAK_URL=" .env | cut -d'=' -f2 2>/dev/null || echo "http://localhost:8080")
        if [[ "$KEYCLOAK_URL" == *"auth.aigualba.cat"* ]]; then
            echo "   - Main Application: https://aigualba.cat"
            echo "   - Admin Panel: https://aigualba.cat/admin"
            echo "   - Backend API: https://aigualba.cat/api"
            echo "   - Keycloak Admin: https://auth.aigualba.cat (restricted to local/private networks)"
        else
            echo "   - Main Application: http://localhost"
            echo "   - Admin Panel: http://localhost/admin"
            echo "   - Backend API: http://localhost/api"
            echo "   - Keycloak Admin: $KEYCLOAK_URL"
        fi
    else
        echo "   - Main Application: http://localhost"
        echo "   - Admin Panel: http://localhost/admin"
        echo "   - Backend API: http://localhost/api"
        echo "   - Keycloak Admin: http://localhost:8080"
    fi
else
    # Development URLs
    echo "   - Main Application: http://localhost:8088"
    echo "   - Admin Panel: http://localhost:8088/admin"
    echo "   - Backend API: http://localhost:8088/api"
    echo "   - Backend Direct: http://localhost:8001"
    echo "   - Frontend Direct: http://localhost:8051"
    echo "   - Keycloak Admin: http://localhost:8080"
    echo "   - Database: localhost:5433 (PostgreSQL)"
fi
echo
echo "👤 Default Admin Credentials:"
echo "   - Username: admin"
echo "   - Password: admin123"
echo
echo "🔧 Useful Commands:"
echo "   - View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "   - Restart services: docker-compose -f $COMPOSE_FILE restart"
echo "   - Stop services: docker-compose -f $COMPOSE_FILE down"
echo "   - Update application: git pull && docker-compose -f $COMPOSE_FILE up --build -d"
echo
echo "📚 Additional Documentation:"
echo "   - Deployment Guide: DEPLOYMENT.md"
echo "   - Admin Setup: ADMIN_SETUP.md"
echo "   - Main README: README.md"
echo

# Environment-specific recommendations
if [ "$DEPLOY_ENV" = "production" ]; then
    echo "🔐 IMPORTANT SECURITY REMINDERS:"
    echo "  1. Change default passwords in .env file"
    echo "  2. Configure HTTPS with SSL certificates for both domains"
    echo "  3. Ensure DNS points both aigualba.cat and auth.aigualba.cat to server"
    echo "  4. Keycloak admin console restricted to local/private networks"
    echo "  5. Use VPN or SSH tunnel for remote Keycloak administration"
    echo "  6. Close unnecessary ports in firewall"
    echo "  7. Regular backups of database"
    echo "  8. Monitor application logs"
    echo
    echo "🎯 Next Steps:"
    echo "  1. Test the application functionality"
    echo "  2. Configure monitoring and backups"
    echo "  3. Set up SSL/HTTPS (see DEPLOYMENT.md)"
    echo "  4. Review security settings"
else
    echo "💻 DEVELOPMENT ENVIRONMENT NOTES:"
    echo "  1. All services use default development credentials"
    echo "  2. HTTP only - no SSL certificates required"
    echo "  3. Database data is persistent between restarts"
    echo "  4. Keycloak realm is automatically imported"
    echo "  5. All services accessible via localhost"
    echo
    echo "🎯 Development Next Steps:"
    echo "  1. Test the application functionality at http://localhost:8088"
    echo "  2. Access admin panel at http://localhost:8088/admin"
    echo "  3. Use Keycloak admin at http://localhost:8080 (admin/admin123)"
    echo "  4. Database accessible at localhost:5433"
    echo "  5. For production deployment, run this script again and select option 2"
fi
echo

echo "✨ Deployment script completed!"