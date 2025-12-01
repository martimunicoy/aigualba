# Keycloak Authentication Fix Summary

## Issues Identified and Fixed

### 1. **URL Mismatch Issues**
- **Problem**: Inconsistent Keycloak URLs between `.env`, `docker-compose.yml`, and nginx configuration
- **Fix**: 
  - Updated `.env` to use `KEYCLOAK_URL=https://auth.aigualba.cat` (consistent with nginx proxy)
  - Updated `docker-compose.yml` frontend to use environment variables from `.env`
  - Nginx already correctly proxies `auth.aigualba.cat` to `keycloak:8443`

### 2. **Client Secret Mismatch**
- **Problem**: `.env` had different client secret than `keycloak/realm-import.json`
- **Fix**: 
  - Updated `.env` to use `KEYCLOAK_CLIENT_SECRET=aigualba-frontend-secret-123` (matching realm config)
  - This ensures frontend and Keycloak use the same client secret

### 3. **Missing Production URLs in Keycloak Realm**
- **Problem**: Keycloak realm only allowed localhost URLs for redirects
- **Fix**: 
  - Added production URLs to `redirectUris` and `webOrigins` in `keycloak/realm-import.json`
  - Now includes: `https://aigualba.cat/*` and `https://auth.aigualba.cat/*`

### 4. **Database Configuration Mismatch**
- **Problem**: Keycloak service used hardcoded DB credentials instead of environment variables
- **Fix**: 
  - Updated `docker-compose.yml` to use `${KC_DB_USERNAME}` and `${KC_DB_PASSWORD}`
  - Updated `.env` to have correct Keycloak DB credentials: `keycloak_user` / `keycloak_pass`

### 5. **Authentication Flow Issues**
- **Problem**: Frontend was trying to use password grant flow (insecure for SPAs)
- **Fix**: 
  - Modified admin callbacks to redirect to Keycloak authorization endpoint
  - Removed username/password form fields, replaced with Keycloak login button
  - Maintained callback handling for authorization code flow

### 6. **Internal Docker Communication**
- **Problem**: Frontend couldn't reliably communicate with Keycloak container
- **Fix**: 
  - Updated auth.py to use `KEYCLOAK_INTERNAL_URL` environment variable
  - Set `KEYCLOAK_INTERNAL_URL=https://keycloak:8443` in docker-compose.yml
  - Added fallback mechanism for internal container communication

## Files Modified

1. **`.env`**
   - Updated `KEYCLOAK_URL` to match nginx proxy
   - Fixed `KEYCLOAK_CLIENT_SECRET` to match realm config
   - Fixed Keycloak database credentials

2. **`docker-compose.yml`**
   - Updated frontend environment to use variables from `.env`
   - Updated Keycloak environment to use database credentials from `.env`

3. **`keycloak/realm-import.json`**
   - Added production redirect URIs and web origins

4. **`frontend/callbacks/admin_callbacks.py`**
   - Modified login flow to redirect to Keycloak instead of password grant
   - Added proper authorization code handling

5. **`frontend/pages/admin.py`**
   - Removed username/password form fields
   - Updated login button text to reflect Keycloak authentication

6. **`frontend/utils/auth.py`**
   - Updated to use `KEYCLOAK_INTERNAL_URL` for container communication
   - Improved error handling and logging

## New Files Added

1. **`test-keycloak-auth.sh`**
   - Comprehensive test script to verify Keycloak configuration
   - Tests endpoints, service connectivity, and configuration consistency

## How Authentication Now Works

1. **User Access**: User navigates to `/admin`
2. **Authentication Check**: Frontend checks for existing valid session
3. **Redirect to Keycloak**: If not authenticated, user clicks "Login with Keycloak" button
4. **Keycloak Login**: User is redirected to `https://auth.aigualba.cat/realms/aigualba/protocol/openid-connect/auth`
5. **User Login**: User enters credentials on Keycloak login page
6. **Authorization Code**: Keycloak redirects back to `https://aigualba.cat/admin` with authorization code
7. **Token Exchange**: Frontend exchanges code for access token using backend communication
8. **Role Check**: Frontend validates user has admin role
9. **Access Granted**: User gains access to admin dashboard

## Testing Instructions

### 1. Apply Changes
```bash
# Ensure you're in the project directory
cd /path/to/aigualba

# Pull latest changes if needed
git pull origin main

# Restart services to apply configuration changes
docker-compose down
docker-compose up -d
```

### 2. Run Authentication Test
```bash
# Run the comprehensive test script
./test-keycloak-auth.sh
```

### 3. Manual Testing
1. **Navigate to Admin Page**: Visit `https://aigualba.cat/admin`
2. **Click Login**: Click "Iniciar sessió amb Keycloak" button
3. **Keycloak Login**: Should redirect to Keycloak login page at `auth.aigualba.cat`
4. **Enter Credentials**: Use `admin` / `admin123` (or configured credentials)
5. **Verify Redirect**: Should return to admin dashboard at `aigualba.cat/admin`
6. **Check Admin Access**: Verify admin dashboard loads with user data

### 4. Troubleshooting
If authentication doesn't work:

```bash
# Check service logs
docker-compose logs keycloak
docker-compose logs frontend
docker-compose logs nginx

# Verify container connectivity
docker-compose exec frontend curl -k https://keycloak:8443/realms/aigualba

# Restart authentication services
docker-compose restart keycloak frontend

# Check environment variables
docker-compose exec frontend env | grep KEYCLOAK
```

## Security Improvements

1. **Proper OAuth 2.0 Flow**: Now uses authorization code flow instead of password grant
2. **Secure Client Authentication**: Client secret properly configured and secured
3. **HTTPS Enforcement**: All authentication flows use HTTPS
4. **Proper CORS Configuration**: Keycloak realm configured with correct origins
5. **Session Management**: Proper token validation and session handling

## Production Considerations

1. **SSL Certificates**: Ensure valid SSL certificates are installed for both `aigualba.cat` and `auth.aigualba.cat`
2. **Keycloak Admin**: Change default Keycloak admin password after deployment
3. **Client Secret**: Ensure client secret is kept secure and not exposed
4. **Database Security**: Keycloak database credentials are properly secured
5. **Network Security**: Ensure proper firewall rules for container communication

## Next Steps

1. **Test Authentication Flow**: Use the provided test script and manual testing
2. **Update Documentation**: Update any user documentation with new login flow
3. **Monitor Logs**: Check authentication logs for any issues
4. **Security Audit**: Perform security review of authentication configuration
5. **Backup Configuration**: Ensure all authentication configuration is backed up

The authentication system should now work properly with Keycloak providing secure OAuth 2.0 authentication for the admin panel.