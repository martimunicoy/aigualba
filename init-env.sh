#!/bin/bash

# Aigualba Environment Initialization Script
# This script creates a .env file with secure, randomly generated credentials

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to generate secure random password
generate_password() {
    local length=${1:-32}
    if command -v openssl &> /dev/null; then
        openssl rand -base64 $((length * 3/4)) | tr -d "=+/" | cut -c1-$length
    elif command -v head &> /dev/null && [ -r /dev/urandom ]; then
        head -c $((length * 2)) /dev/urandom | base64 | tr -d "=+/\n" | cut -c1-$length
    else
        # Fallback using date and random
        echo "$(date +%s)$(echo $RANDOM | md5sum | head -c $((length-10)))"
    fi
}

# Function to generate secure database password (alphanumeric + safe symbols)
generate_db_password() {
    local length=${1:-24}
    if command -v openssl &> /dev/null; then
        openssl rand -base64 $((length * 3/4)) | tr -d "=+/\n" | sed 's/[^a-zA-Z0-9]//g' | cut -c1-$length
    else
        # Fallback
        head -c $((length * 2)) /dev/urandom 2>/dev/null | base64 | tr -d "=+/\n" | sed 's/[^a-zA-Z0-9]//g' | cut -c1-$length || echo "SecurePass$(date +%s)"
    fi
}

echo -e "${BLUE}🔐 Aigualba Environment Initialization${NC}"
echo "======================================"
echo

# Check if .env already exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists!${NC}"
    echo
    read -p "Do you want to backup the existing .env and create a new one? (y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        backup_file=".env.backup.$(date +%Y%m%d_%H%M%S)"
        cp .env "$backup_file"
        echo -e "${GREEN}✅ Existing .env backed up as: $backup_file${NC}"
    else
        echo -e "${YELLOW}Operation cancelled.${NC}"
        exit 0
    fi
fi

# Check if .env.example exists
if [ ! -f ".env.example" ]; then
    echo -e "${RED}❌ Error: .env.example file not found${NC}"
    echo "Please ensure you're in the correct directory with .env.example"
    exit 1
fi

echo -e "${YELLOW}🔑 Generating secure credentials...${NC}"

# Generate secure passwords
POSTGRES_PASSWORD=$(generate_db_password 32)
DEV_POSTGRES_PASSWORD=$(generate_db_password 24)
KEYCLOAK_ADMIN_PASSWORD=$(generate_db_password 24)
KC_DB_PASSWORD=$(generate_db_password 32)
KEYCLOAK_CLIENT_SECRET=$(generate_password 64)

echo -e "${GREEN}✅ Secure credentials generated${NC}"
echo

# Prompt for configuration options
echo -e "${BLUE}🌐 Configuration Options${NC}"
echo

# Domain configuration
read -p "Enter your domain name (or press Enter for localhost): " domain_input
DOMAIN=${domain_input:-localhost}

# Environment type
read -p "Is this a production deployment? (y/N): " is_production
if [[ $is_production == [yY] ]]; then
    ENV_TYPE="production"
    DASH_DEBUG="0"
    PROTOCOL="https"
    echo -e "${YELLOW}⚠️  Production mode selected - HTTPS will be configured${NC}"
else
    ENV_TYPE="development"
    DASH_DEBUG="1" 
    PROTOCOL="http"
fi

# Port configuration for development
if [[ $ENV_TYPE == "development" ]]; then
    read -p "Enter frontend port (default: 8051): " frontend_port
    FRONTEND_PORT=${frontend_port:-8051}
    read -p "Enter backend port (default: 8001): " backend_port
    BACKEND_PORT=${backend_port:-8001}
    read -p "Enter Keycloak port (default: 8080): " keycloak_port
    KEYCLOAK_PORT=${keycloak_port:-8080}
else
    FRONTEND_PORT="8050"
    BACKEND_PORT="8000"
    KEYCLOAK_PORT="8080"
fi

# Create .env file
echo -e "${YELLOW}📝 Creating .env file...${NC}"

cat > .env << EOF
# Aigualba Environment Configuration
# Generated on: $(date)
# Environment: $ENV_TYPE

# Database Configuration
POSTGRES_USER=aigualba_user
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=aigualba

# Backend Configuration
$(if [[ $ENV_TYPE == "development" ]]; then
echo "DATABASE_URL=postgresql://devuser:$DEV_POSTGRES_PASSWORD@db:5432/aigualba_db"
else
echo "DATABASE_URL=postgresql://aigualba_user:$POSTGRES_PASSWORD@db:5432/aigualba"
fi)

# Frontend Configuration  
BACKEND_URL=http://backend:$BACKEND_PORT

# Development Environment Variables (only needed if running database migrations or dev setup)
DEV_POSTGRES_USER=devuser
DEV_POSTGRES_PASSWORD=$DEV_POSTGRES_PASSWORD
DEV_POSTGRES_DB=aigualba_db
$(if [[ $ENV_TYPE == "development" ]]; then
echo "DEV_DATABASE_URL=postgresql://devuser:$DEV_POSTGRES_PASSWORD@db:5432/aigualba_db"
else
echo "# DEV_DATABASE_URL=postgresql://devuser:$DEV_POSTGRES_PASSWORD@db:5432/aigualba_db"
fi)

# Keycloak Configuration
KEYCLOAK_URL=$PROTOCOL://auth.$DOMAIN
KEYCLOAK_REALM=aigualba
KEYCLOAK_CLIENT_ID=aigualba-frontend  
KEYCLOAK_CLIENT_SECRET=$KEYCLOAK_CLIENT_SECRET
KEYCLOAK_REDIRECT_URI=$PROTOCOL://$DOMAIN/admin
KEYCLOAK_ADMIN_PASSWORD=$KEYCLOAK_ADMIN_PASSWORD

# Keycloak Database Configuration
KC_DB_USERNAME=keycloak_user
KC_DB_PASSWORD=$KC_DB_PASSWORD

# Application Configuration
DASH_DEBUG=$DASH_DEBUG
ENVIRONMENT=$ENV_TYPE

$(if [[ $ENV_TYPE == "production" ]]; then
echo "# SSL Certificate Configuration (Production only)"
echo "KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/certs/live/aigualba.cat/fullchain.pem"
echo "KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/certs/live/aigualba.cat/privkey.pem"
fi)
EOF

echo -e "${GREEN}✅ .env file created successfully!${NC}"
echo

# Generate Keycloak realm configuration from template
echo -e "${YELLOW}🔧 Generating Keycloak realm configuration from template...${NC}"
if [ -f "keycloak/realm-import.json.template" ]; then
    # Generate realm-import.json from template
    sed "s/{{KEYCLOAK_CLIENT_SECRET}}/$KEYCLOAK_CLIENT_SECRET/g" keycloak/realm-import.json.template > keycloak/realm-import.json
    echo -e "${GREEN}✅ Keycloak realm configuration generated with secure client secret${NC}"
else
    echo -e "${RED}❌ Error: keycloak/realm-import.json.template not found${NC}"
    echo -e "${YELLOW}   Please ensure the template file exists${NC}"
    exit 1
fi

# Create database password update script
echo -e "${YELLOW}🔧 Creating Keycloak database password update script...${NC}"
cat > db/03-update-keycloak-password.sql << EOF
-- Update Keycloak user password with generated password
-- This script runs after the initial user creation
ALTER ROLE keycloak_user WITH PASSWORD '$KC_DB_PASSWORD';
EOF

echo -e "${GREEN}✅ Keycloak database password update script created${NC}"
echo

# Display configuration summary
echo -e "${BLUE}📋 Configuration Summary${NC}"
echo "========================"
echo "Environment: $ENV_TYPE"
echo "Domain: $DOMAIN"
echo "Protocol: $PROTOCOL"
if [[ $ENV_TYPE == "development" ]]; then
    echo "Frontend Port: $FRONTEND_PORT"
    echo "Backend Port: $BACKEND_PORT"
    echo "Keycloak Port: $KEYCLOAK_PORT"
fi
echo

# Security information
echo -e "${GREEN}🔐 Security Information${NC}"
echo "======================="
echo "✅ All passwords are randomly generated and secure"
echo "✅ Database passwords: 24-32 characters"
echo "✅ Client secrets: 64 characters" 
echo "✅ Keycloak realm configuration automatically updated"
echo "✅ Passwords contain alphanumeric characters only (database compatible)"
echo

# Important notes
echo -e "${YELLOW}📝 Important Notes${NC}"
echo "=================="
echo "• Keep your .env file secure and never commit it to version control"
echo "• The keycloak/realm-import.json file contains secrets and is automatically generated"
echo "• Never commit keycloak/realm-import.json - only the .template version should be in git"
echo "• Backup your .env file in a secure location"
echo "• For production, ensure HTTPS is properly configured"
echo "• Change the Keycloak admin password after first login if needed"
echo

# Show admin credentials
echo -e "${BLUE}👤 Admin Credentials${NC}"
echo "==================="
echo "Keycloak Admin Username: admin"
echo "Keycloak Admin Password: $KEYCLOAK_ADMIN_PASSWORD"
echo

# Next steps
echo -e "${GREEN}🚀 Next Steps${NC}"
echo "============="
if [[ $ENV_TYPE == "production" ]]; then
    echo "1. Review the .env file and adjust any settings as needed"
    echo "2. Ensure SSL certificates are configured for HTTPS"
    echo "3. Run: ./deploy.sh"
    echo "4. Run: ./health-check.sh"
else
    echo "1. Review the .env file and adjust any settings as needed" 
    echo "2. Run: docker-compose -f docker-compose.dev.yml up --build"
    echo "3. Run: ./setup-keycloak.sh"
fi
echo "5. Access the application and verify all functionality"
echo "6. Create your first backup: ./backup.sh"
echo

# Save credentials summary
CREDS_FILE=".env.credentials.$(date +%Y%m%d_%H%M%S).txt"
cat > "$CREDS_FILE" << EOF
Aigualba Deployment Credentials
Generated: $(date)
Environment: $ENV_TYPE
Domain: $DOMAIN

=== Database Credentials ===
Main Database User: aigualba_user
Main Database Password: $POSTGRES_PASSWORD
Dev Database User: devuser  
Dev Database Password: $DEV_POSTGRES_PASSWORD

=== Keycloak Credentials ===
Admin Username: admin
Admin Password: $KEYCLOAK_ADMIN_PASSWORD
Client Secret: $KEYCLOAK_CLIENT_SECRET
Keycloak DB User: keycloak_user
Keycloak DB Password: $KC_DB_PASSWORD

=== Application URLs ===
Frontend: $PROTOCOL://$DOMAIN:$FRONTEND_PORT
Backend API: $PROTOCOL://$DOMAIN:$BACKEND_PORT/api
Keycloak Admin: $PROTOCOL://$DOMAIN:$KEYCLOAK_PORT

IMPORTANT: Store these credentials securely and delete this file after recording them safely.
EOF

echo -e "${BLUE}💾 Credentials Summary${NC}"
echo "Credentials saved to: $CREDS_FILE"
echo -e "${YELLOW}⚠️  Please store these credentials securely and delete the file after saving them safely${NC}"
echo

echo -e "${GREEN}🎉 Environment initialization completed!${NC}"
echo "Your Aigualba instance is ready for deployment."