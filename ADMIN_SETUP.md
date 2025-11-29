# Admin Authentication System with Keycloak

This document describes the implementation of the admin authentication system using Keycloak for the Aigualba water quality management system.

## Overview

The admin system provides:
- Secure authentication via Keycloak
- Role-based access control  
- Sample management dashboard
- Bulk operations on water quality samples
- System configuration interface

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Keycloak      │    │   Backend       │
│   (Dash)        │◄──►│   (Auth Server) │    │   (FastAPI)     │
│                 │    │                 │    │                 │
│ • Admin Page    │    │ • JWT Tokens    │    │ • Admin Routes  │
│ • Auth Flow     │    │ • User Mgmt     │    │ • Sample CRUD   │
│ • Dashboard     │    │ • Role Mgmt     │    │ • Validation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Setup Instructions

### 1. Start Keycloak

```bash
# Quick setup (recommended)
./setup-keycloak.sh

# Or manually
docker-compose -f docker-compose.keycloak.yml up -d
```

### 2. Start Development Environment

```bash
# Start all services including Keycloak
docker-compose -f docker-compose.dev.yml up --build
```

### 3. Access Admin Panel

1. Go to http://localhost:8051/admin
2. Click "Iniciar sessió" (Login)
3. Use credentials:
   - **Admin**: `admin` / `admin123`
   - **User**: `user` / `user123`

## Admin Features

### Sample Management
- **View all samples** with validation status
- **Bulk operations**:
  - Validate multiple samples
  - Mark as pending
  - Delete samples
- **Individual sample editing**
- **Real-time status updates**

### Statistics Dashboard
- Total samples count
- Validation status breakdown
- Location distribution
- Recent activity

### System Configuration  
- Keycloak settings
- Database operations
- Export functionality

## API Endpoints

### Admin Authentication
All admin endpoints require Bearer token authentication.

```http
Authorization: Bearer <jwt-token>
```

### Sample Management

#### Get All Samples (Admin)
```http
GET /api/admin/samples
```

#### Validate Sample
```http
PATCH /api/admin/samples/{sample_id}/validate
Content-Type: application/json

{"validated": true}
```

#### Update Sample
```http
PUT /api/admin/samples/{sample_id}
Content-Type: application/json

{
  "temperatura": 20.5,
  "ph": 7.2,
  "validated": true
}
```

#### Delete Sample
```http
DELETE /api/admin/samples/{sample_id}
```

#### Bulk Validate
```http
POST /api/admin/samples/bulk-validate
Content-Type: application/json

{
  "sample_ids": [1, 2, 3],
  "validated": true
}
```

#### Get Statistics
```http
GET /api/admin/statistics
```

## Database Schema Updates

The system adds validation columns to the samples table:

```sql
ALTER TABLE mostres_aigua ADD COLUMN IF NOT EXISTS validated BOOLEAN DEFAULT FALSE;
ALTER TABLE mostres_aigua ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

## Keycloak Configuration

### Realm: `aigualba`
- **Client ID**: `aigualba-frontend`
- **Client Secret**: `aigualba-frontend-secret-123`
- **Redirect URIs**: 
  - `http://localhost:8050/*`
  - `http://localhost:3000/*`

### Roles
- **admin**: Full access to admin panel and sample management
- **user**: Read-only access to public features

### Test Users
- **admin@aigualba.local**: Admin user with full permissions
- **user@aigualba.local**: Regular user with limited access

## Environment Variables

### Frontend
```bash
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=aigualba
KEYCLOAK_CLIENT_ID=aigualba-frontend
KEYCLOAK_CLIENT_SECRET=aigualba-frontend-secret-123
KEYCLOAK_REDIRECT_URI=http://localhost:8050/admin/callback
```

### Backend  
```bash
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=aigualba
```

## Security Considerations

### Development Mode
- Uses Keycloak in development mode
- Self-signed certificates accepted
- Demo credentials included

### Production Deployment
For production, ensure:
1. **HTTPS everywhere** - Keycloak, frontend, backend
2. **Strong passwords** - Change all default credentials  
3. **Certificate validation** - Proper SSL/TLS setup
4. **Network security** - Firewall rules, VPN access
5. **Token validation** - Proper JWT verification
6. **Rate limiting** - API request throttling

## Troubleshooting

### Keycloak Issues

#### Container won't start
```bash
# Check logs
docker-compose -f docker-compose.keycloak.yml logs keycloak

# Reset volumes
docker-compose -f docker-compose.keycloak.yml down -v
docker-compose -f docker-compose.keycloak.yml up -d
```

#### Realm not imported
1. Access admin console: http://localhost:8080
2. Login with `admin`/`admin123`
3. Manually import `keycloak/realm-import.json`

### Authentication Issues

#### Login redirects fail
- Check redirect URIs in Keycloak client configuration
- Verify frontend URL matches configuration

#### Token validation errors  
- Ensure backend can reach Keycloak
- Check JWT token format and expiration

### Admin Panel Issues

#### Can't access admin features
- Verify user has `admin` role in Keycloak
- Check browser developer console for errors
- Confirm backend admin API is accessible

## Development Workflow

### Adding New Admin Features

1. **Backend**: Add new route in `admin_router.py`
2. **Frontend**: Add UI components in `admin_dashboard.py`  
3. **Callbacks**: Add logic in `admin_callbacks.py`
4. **Styling**: Update `style.css` for admin classes

### Testing Admin Features

```bash
# Run with admin user
curl -H "Authorization: Bearer admin-demo-token" \
     http://localhost:8001/api/admin/samples

# Test bulk operations
curl -X POST \
     -H "Authorization: Bearer admin-demo-token" \
     -H "Content-Type: application/json" \
     -d '{"sample_ids": [1,2], "validated": true}' \
     http://localhost:8001/api/admin/samples/bulk-validate
```

## Future Enhancements

### Planned Features
- [ ] Audit logging for admin actions
- [ ] Email notifications for sample validations  
- [ ] Advanced filtering and search
- [ ] Bulk import/export functionality
- [ ] Role hierarchy (super-admin, moderator, etc.)
- [ ] API rate limiting per user role
- [ ] Dashboard analytics and reporting
- [ ] Mobile-responsive admin interface

### Security Improvements
- [ ] Multi-factor authentication (MFA)
- [ ] Session timeout warnings
- [ ] IP whitelist for admin access
- [ ] Advanced RBAC with custom permissions
- [ ] OAuth2 token refresh handling
- [ ] CSP headers and security hardening

This admin system provides a solid foundation for managing the Aigualba water quality database with proper authentication, authorization, and user-friendly interfaces.