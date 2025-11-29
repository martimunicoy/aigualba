# 🚀 Aigualba Deployment Checklist

Use this checklist to ensure a successful production deployment.

## Pre-Deployment Checklist

### ✅ Environment Setup
- [ ] Server with Docker and Docker Compose installed
- [ ] Domain name configured (optional)
- [ ] SSL certificate obtained (recommended)
- [ ] Firewall configured (ports 80, 443, 8080)
- [ ] Sufficient resources (min: 4GB RAM, 2 CPU cores, 20GB storage)

### ✅ Code Preparation
- [ ] Repository cloned to production server
- [ ] Latest code pulled from main branch
- [ ] All deployment files present:
  - [ ] `.env.example` (template for environment variables)
  - [ ] `docker-compose.yml` (production configuration)
  - [ ] `docker-compose.prod.yml` (production overrides)
  - [ ] `DEPLOYMENT.md` (detailed deployment guide)
  - [ ] `deploy.sh` (automated deployment script)
  - [ ] `health-check.sh` (health monitoring script)
  - [ ] `backup.sh` (backup script)

### ✅ Configuration
- [ ] `.env` file created from template
- [ ] Strong passwords set for all services:
  - [ ] `POSTGRES_PASSWORD`
  - [ ] `KEYCLOAK_ADMIN_PASSWORD`
  - [ ] `KC_DB_PASSWORD`
  - [ ] `KEYCLOAK_CLIENT_SECRET`
- [ ] Domain names updated in configuration
- [ ] SSL certificate paths configured (if using HTTPS)

## Deployment Process

### ✅ Automated Deployment (Recommended)
- [ ] Run `./deploy.sh` script
- [ ] Follow prompts and verify configuration
- [ ] Wait for all services to start
- [ ] Run health checks

### ✅ Manual Deployment (Alternative)
- [ ] `docker-compose up -d` to start services
- [ ] `./setup-keycloak.sh` for authentication setup
- [ ] `./health-check.sh` to verify status

## Post-Deployment Checklist

### ✅ Functionality Testing
- [ ] Public dashboard accessible (http://your-server)
- [ ] Browse page loads with sample data
- [ ] Visualizations render correctly
- [ ] Sample submission form works
- [ ] Admin login functional (http://your-server/admin)
- [ ] Admin can validate/manage samples
- [ ] Keycloak admin console accessible (http://your-server:8080)

### ✅ Security Verification
- [ ] Default passwords changed
- [ ] Admin authentication working
- [ ] HTTPS configured (production)
- [ ] Unnecessary ports closed
- [ ] Database not directly accessible from outside

### ✅ Performance and Monitoring
- [ ] All services showing healthy status
- [ ] Resource usage within acceptable limits
- [ ] Response times reasonable
- [ ] Logs showing no critical errors

### ✅ Backup and Recovery
- [ ] First backup created: `./backup.sh`
- [ ] Backup directory configured
- [ ] Backup restoration tested
- [ ] Automated backups scheduled (cron)

### ✅ Documentation and Maintenance
- [ ] Access credentials documented securely
- [ ] Monitoring procedures established
- [ ] Update procedures documented
- [ ] Support contacts configured

## Quick Commands Reference

```bash
# Deploy application
./deploy.sh

# Check health
./health-check.sh

# Create backup
./backup.sh

# View logs
docker-compose logs -f [service]

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update application
git pull && docker-compose up --build -d
```

## Emergency Contacts

- **System Administrator**: [Your contact info]
- **Database Administrator**: [Your contact info]
- **Application Developer**: [Your contact info]

## Service URLs

- **Public Dashboard**: http://your-server
- **Admin Panel**: http://your-server/admin
- **API Documentation**: http://your-server/api/docs
- **Keycloak Admin**: http://your-server:8080
- **Health Check**: http://your-server/health

---

**Deployment Date**: _______________
**Deployed by**: _______________
**Version**: _______________
**Notes**: _____________________