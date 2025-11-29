#!/bin/bash

# Backup script for Aigualba production deployment
# This script creates backups of the database and application files

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/opt/aigualba/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
DATE=$(date +%Y%m%d_%H%M%S)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🗄️  Aigualba Backup Script${NC}"
echo "=========================="
echo "Backup directory: $BACKUP_DIR"
echo "Retention: $RETENTION_DAYS days"
echo "Timestamp: $DATE"
echo

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Database backup
echo -e "${YELLOW}📊 Creating database backup...${NC}"
DB_BACKUP_FILE="$BACKUP_DIR/db_$DATE.sql.gz"

if docker-compose exec -T db pg_dump -U "$POSTGRES_USER" -c "$POSTGRES_DB" | gzip > "$DB_BACKUP_FILE"; then
    echo -e "${GREEN}✅ Database backup completed: $(basename $DB_BACKUP_FILE)${NC}"
    echo "   Size: $(du -h $DB_BACKUP_FILE | cut -f1)"
else
    echo -e "${RED}❌ Database backup failed${NC}"
    exit 1
fi

# Application files backup
echo -e "${YELLOW}📁 Creating application files backup...${NC}"
APP_BACKUP_FILE="$BACKUP_DIR/app_$DATE.tar.gz"

# Create application backup excluding unnecessary files
if tar -czf "$APP_BACKUP_FILE" \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    --exclude='logs' \
    --exclude='backups' \
    --exclude='.env' \
    --exclude='docker-compose.override.yml' \
    .; then
    echo -e "${GREEN}✅ Application backup completed: $(basename $APP_BACKUP_FILE)${NC}"
    echo "   Size: $(du -h $APP_BACKUP_FILE | cut -f1)"
else
    echo -e "${RED}❌ Application backup failed${NC}"
    exit 1
fi

# Configuration backup (without sensitive data)
echo -e "${YELLOW}⚙️  Creating configuration backup...${NC}"
CONFIG_BACKUP_FILE="$BACKUP_DIR/config_$DATE.tar.gz"

# Create config backup with sanitized env file
if [ -f .env ]; then
    # Create temporary sanitized .env
    TEMP_ENV=$(mktemp)
    sed 's/=.*/=REDACTED/g' .env > "$TEMP_ENV"
    
    tar -czf "$CONFIG_BACKUP_FILE" \
        --transform="s|$TEMP_ENV|.env.example|" \
        docker-compose.yml \
        docker-compose.prod.yml \
        nginx/nginx.conf \
        nginx/nginx.prod.conf \
        keycloak/realm-import.json \
        "$TEMP_ENV"
    
    rm "$TEMP_ENV"
    echo -e "${GREEN}✅ Configuration backup completed: $(basename $CONFIG_BACKUP_FILE)${NC}"
    echo "   Size: $(du -h $CONFIG_BACKUP_FILE | cut -f1)"
fi

# Docker volumes backup (if needed)
echo -e "${YELLOW}🐳 Creating Docker volumes backup...${NC}"
VOLUMES_BACKUP_FILE="$BACKUP_DIR/volumes_$DATE.tar.gz"

# Get volume names
POSTGRES_VOLUME=$(docker volume ls -q | grep postgres_data || echo "")
KEYCLOAK_VOLUME=$(docker volume ls -q | grep keycloak_data || echo "")

if [ -n "$POSTGRES_VOLUME" ] || [ -n "$KEYCLOAK_VOLUME" ]; then
    # Create temporary container to backup volumes
    docker run --rm \
        -v "$POSTGRES_VOLUME:/source/postgres:ro" \
        -v "$KEYCLOAK_VOLUME:/source/keycloak:ro" \
        -v "$BACKUP_DIR:/backup" \
        busybox \
        tar -czf "/backup/volumes_$DATE.tar.gz" -C /source .
    
    echo -e "${GREEN}✅ Volumes backup completed: $(basename $VOLUMES_BACKUP_FILE)${NC}"
    echo "   Size: $(du -h $VOLUMES_BACKUP_FILE | cut -f1)"
else
    echo -e "${YELLOW}⚠️  No Docker volumes found to backup${NC}"
fi

# Cleanup old backups
echo -e "${YELLOW}🧹 Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
DELETED_COUNT=$(find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete -print | wc -l)
echo -e "${GREEN}✅ Deleted $DELETED_COUNT old backup files${NC}"

# Generate backup report
echo
echo -e "${GREEN}📋 Backup Summary${NC}"
echo "=================="
echo "Backup directory: $BACKUP_DIR"
echo "Available backups:"
ls -lh "$BACKUP_DIR" | tail -n +2 | while read -r line; do
    echo "   $line"
done

echo
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "Total backup size: $TOTAL_SIZE"

# Test database backup integrity (optional)
if command -v gzip &> /dev/null && command -v head &> /dev/null; then
    echo
    echo -e "${YELLOW}🔍 Testing database backup integrity...${NC}"
    if gzip -t "$DB_BACKUP_FILE" && gunzip -c "$DB_BACKUP_FILE" | head -n 5 | grep -q "PostgreSQL"; then
        echo -e "${GREEN}✅ Database backup integrity check passed${NC}"
    else
        echo -e "${RED}❌ Database backup integrity check failed${NC}"
    fi
fi

echo
echo -e "${GREEN}🎉 Backup completed successfully!${NC}"

# Optional: Send notification (uncomment if you have mail configured)
# echo "Aigualba backup completed successfully on $(date)" | mail -s "Aigualba Backup Report" admin@yourdomain.com

exit 0