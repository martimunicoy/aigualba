#!/bin/bash

# Health check script for Aigualba services
# This script checks if all services are running and healthy

set -e

echo "🏥 Aigualba Health Check"
echo "======================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not available${NC}"
    exit 1
fi

# Check if services are running
echo "🔍 Checking service status..."
services=("nginx" "db" "backend" "frontend" "keycloak")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose ps "$service" | grep -q "Up"; then
        echo -e "✅ ${GREEN}$service${NC}: Running"
    else
        echo -e "❌ ${RED}$service${NC}: Not running"
        all_healthy=false
    fi
done

echo

# Check service health endpoints
echo "🩺 Checking health endpoints..."

# Check nginx
if curl -f -s http://localhost/health > /dev/null 2>&1; then
    echo -e "✅ ${GREEN}nginx${NC}: Health endpoint OK"
else
    echo -e "❌ ${RED}nginx${NC}: Health endpoint failed"
    all_healthy=false
fi

# Check backend
if curl -f -s http://localhost/api/health > /dev/null 2>&1; then
    echo -e "✅ ${GREEN}backend${NC}: Health endpoint OK"
else
    echo -e "⚠️ ${YELLOW}backend${NC}: Health endpoint not available (may not be implemented)"
fi

# Check frontend
if curl -f -s http://localhost > /dev/null 2>&1; then
    echo -e "✅ ${GREEN}frontend${NC}: Responding"
else
    echo -e "❌ ${RED}frontend${NC}: Not responding"
    all_healthy=false
fi

# Check keycloak
if curl -f -s http://localhost:8080/health/ready > /dev/null 2>&1; then
    echo -e "✅ ${GREEN}keycloak${NC}: Health endpoint OK"
else
    echo -e "⚠️ ${YELLOW}keycloak${NC}: Health endpoint may still be starting"
fi

echo

# Check database connectivity
echo "💾 Checking database connectivity..."
if docker-compose exec -T db pg_isready -U $(grep POSTGRES_USER .env | cut -d= -f2) > /dev/null 2>&1; then
    echo -e "✅ ${GREEN}database${NC}: Connection OK"
else
    echo -e "❌ ${RED}database${NC}: Connection failed"
    all_healthy=false
fi

echo

# Resource usage check
echo "📊 Resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo

# Disk usage
echo "💽 Disk usage:"
df -h / | tail -1 | awk '{print "   Root filesystem: " $3 " used, " $4 " available (" $5 " used)"}'

# Docker volumes disk usage
echo "   Docker volumes:"
docker system df | tail -n +2

echo

# Final status
if [ "$all_healthy" = true ]; then
    echo -e "🎉 ${GREEN}All critical services are healthy!${NC}"
    exit 0
else
    echo -e "⚠️ ${YELLOW}Some services have issues. Check the logs:${NC}"
    echo "   docker-compose logs -f"
    echo
    echo -e "${YELLOW}Recent errors from logs:${NC}"
    docker-compose logs --tail=10 2>&1 | grep -i error | tail -5 || echo "   No recent errors found"
    exit 1
fi