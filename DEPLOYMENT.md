# Deployment Guide for Aigualba

This guide covers deploying Aigualba in production environments.

## 🚀 Quick Production Deployment

### Prerequisites
- Docker & Docker Compose
- Domain name (optional, can use IP)
- SSL certificate (recommended for production)

### 1. Server Setup

```bash
# Clone the repository
git clone https://github.com/martimunicoy/aigualba.git
cd aigualba

# Initialize secure environment
./init-env.sh

# OR manually copy and edit
# cp .env.example .env
# nano .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your production values:

```bash
# Database Configuration - Use strong passwords
POSTGRES_USER=aigualba_user  
POSTGRES_PASSWORD=your_secure_database_password_here
POSTGRES_DB=aigualba

# Backend Configuration
DATABASE_URL=postgresql://aigualba_user:your_secure_database_password_here@db:5432/aigualba

# Keycloak Configuration  
KEYCLOAK_ADMIN_PASSWORD=your_secure_keycloak_admin_password
KC_DB_USERNAME=keycloak_user
KC_DB_PASSWORD=your_secure_keycloak_db_password
KEYCLOAK_CLIENT_SECRET=your_secure_client_secret

# Frontend Configuration
BACKEND_URL=http://backend:8000
DASH_DEBUG=0
```

### 3. Deploy the Application

```bash
# Automated deployment (recommended)
./deploy.sh

# OR Manual deployment
docker-compose up -d

# Check service status
docker-compose ps

# View logs if needed
docker-compose logs -f
```

### 4. Initialize Keycloak (First Time Only)

```bash
# Setup script (auto-detects production environment)
./setup-keycloak.sh

# Verify Keycloak is working
curl http://localhost:8080/health/ready
```

### 5. Access the Application

- **Public Dashboard**: http://your-server-ip (or http://localhost if local)
- **Admin Panel**: http://your-server-ip/admin
- **Keycloak Admin Console**: http://your-server-ip:8080

## 🔄 Environment Management

### Automatic Environment Detection

The deployment scripts automatically detect the environment:

**Production Environment** (uses `docker-compose.yml`):
- `.env` file with `DASH_DEBUG=0` or missing
- Optimized containers with security hardening
- No development sample data

**Development Environment** (uses `docker-compose.dev.yml`):
- `.env` file with `DASH_DEBUG=1`
- Development tools and hot reload
- Sample data for testing

### Manual Environment Selection

```bash
# Force development mode
./setup-keycloak.sh --dev

# Production deployment
./deploy.sh

# Development setup
docker-compose -f docker-compose.dev.yml up --build
```

## 🔐 Production Security Checklist

### Essential Security Steps

1. **Change Default Passwords**
   ```bash
   # Update .env with secure passwords:
   - POSTGRES_PASSWORD
   - KEYCLOAK_ADMIN_PASSWORD  
   - KC_DB_PASSWORD
   - KEYCLOAK_CLIENT_SECRET
   ```

2. **Enable HTTPS**
   - Get SSL certificates (Let's Encrypt recommended)
   - Configure reverse proxy (nginx or traefik)
   - Update `KEYCLOAK_REDIRECT_URI` to use https://

3. **Network Security**
   - Close unnecessary ports (only 80/443 should be public)
   - Use firewall rules
   - Consider VPN for admin access

4. **Database Security**  
   - Remove port exposure in docker-compose.yml
   - Regular backups
   - Monitor access logs

### Recommended Production Setup

```bash
# Remove port exposure from services
# Edit docker-compose.yml and comment out:
# - "5432:5432" (database)
# - "8000:8000" (backend) 
# - "8050:8050" (frontend)

# Only nginx on port 80/443 should be exposed
```

## 🔧 HTTPS Configuration with Let's Encrypt

### Using Certbot with Nginx

1. **Install Certbot**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Update Nginx Configuration**
```nginx
# Add to nginx/nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
    
    location / {
        proxy_pass http://frontend:8050/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

3. **Get SSL Certificate**
```bash
sudo certbot --nginx -d your-domain.com
```

4. **Update Environment Variables**
```bash
# Update .env
KEYCLOAK_REDIRECT_URI=https://your-domain.com/admin
```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check service health
docker-compose ps

# Monitor resource usage
docker stats

# View application logs
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db
```

### Database Backup

```bash
# Create backup
docker-compose exec db pg_dump -U aigualba_user aigualba > backup-$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U aigualba_user aigualba < backup-20241129.sql
```

### Updates

```bash
# Update to latest version
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose up --build -d

# Check for issues
docker-compose logs -f
```

## 🚨 Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check logs
   docker-compose logs
   
   # Check disk space
   df -h
   
   # Check memory
   free -h
   ```

2. **Database connection errors**
   ```bash
   # Verify database is running
   docker-compose exec db pg_isready -U aigualba_user
   
   # Check environment variables
   docker-compose exec backend env | grep DATABASE
   ```

3. **Keycloak authentication issues**
   ```bash
   # Check Keycloak logs
   docker-compose logs keycloak
   
   # Verify realm import
   docker-compose exec keycloak ls -la /opt/keycloak/data/import/
   ```

4. **High resource usage**
   ```bash
   # Monitor resources
   docker stats
   
   # Restart specific service
   docker-compose restart frontend
   ```

### Performance Optimization

1. **Database Optimization**
   - Regular vacuum and analyze
   - Monitor slow queries
   - Consider connection pooling

2. **Application Optimization**
   - Monitor memory usage
   - Optimize query patterns
   - Consider caching layer

3. **Infrastructure**
   - Use SSD storage
   - Adequate RAM (minimum 4GB recommended)
   - Monitor network bandwidth

## 📈 Scaling Considerations

### Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer**
   - Multiple frontend/backend instances
   - Database read replicas
   - Redis for session storage

2. **Container Orchestration**
   - Consider Kubernetes for large deployments
   - Docker Swarm for simpler scaling
   - Managed container services (ECS, GKE)

3. **Database Scaling**
   - PostgreSQL read replicas
   - Connection pooling with PgBouncer
   - Separate analytics database

### Resource Requirements

| Component | Minimum | Recommended | High Load |
|-----------|---------|-------------|-----------|
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **RAM** | 4GB | 8GB | 16+ GB |
| **Storage** | 20GB SSD | 50GB SSD | 100+ GB SSD |
| **Network** | 100 Mbps | 1 Gbps | 10+ Gbps |

## 🔄 Backup and Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh - Daily backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/aigualba/backups"
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T db pg_dump -U aigualba_user -c aigualba | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Application files backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz --exclude='.git' --exclude='__pycache__' /opt/aigualba

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Add to Crontab

```bash
# Daily backup at 2 AM
0 2 * * * /opt/aigualba/backup.sh >> /var/log/aigualba-backup.log 2>&1
```

---

For additional support or questions, please refer to the main [README.md](README.md) or open an issue on GitHub.