"""Keycloak authentication utilities for Aigualba with diagnostics logging"""
import os
import jwt
import requests
import logging
from datetime import datetime, timedelta
from functools import wraps
from dash import callback_context
import json

# Logger for Keycloak operations
logger = logging.getLogger("aigualba.keycloak")
if not logger.handlers:
    # Avoid adding multiple handlers if module reloaded; let application configure handlers in production
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(os.getenv('AIGUALBA_LOG_LEVEL', 'INFO'))

class KeycloakAuth:
    def __init__(self):
        self.keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
        self.realm = os.getenv("KEYCLOAK_REALM", "aigualba")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID", "aigualba-frontend")
        # Get client secret from environment
        self.client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET", "aigualba-frontend-secret-123")
        # For embedded login, we use confidential client with direct access grants
        self.public_client = False
        # Use same client for admin operations (since we have embedded login)
        self.admin_client_id = self.client_id
        self.admin_client_secret = self.client_secret
        self.redirect_uri = os.getenv("KEYCLOAK_REDIRECT_URI", "http://localhost:8050/admin/callback")

    def get_auth_url(self, state=None):
        """Generate Keycloak authorization URL"""
        auth_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/auth"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid profile email roles"
        }
        if state:
            params["state"] = state
        
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{auth_url}?{param_string}"
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            # include client_secret only when configured (confidential client)
            **({"client_secret": self.client_secret} if self.client_secret else {}),
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        # Use the configured KEYCLOAK_URL and internal URL
        public_token_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
        # Use internal URL for docker-compose communication
        internal_keycloak_url = os.getenv("KEYCLOAK_INTERNAL_URL", "https://keycloak:8443")
        internal_token_url = f"{internal_keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"

        # Try public URL first, then fallback to internal URL used inside docker-compose
        try:
            logger.debug("Attempting token exchange (public) %s for client_id=%s", public_token_url, self.client_id)
            response = requests.post(public_token_url, data=data, timeout=5)
            logger.debug("Response (public) status=%s body=%s", response.status_code, response.text)
            response.raise_for_status()
            token_json = response.json()
            logger.info("Token exchange (public) successful for client_id=%s", self.client_id)
            return token_json
        except requests.exceptions.RequestException as e_public:
            logger.warning("Public token exchange failed: %s", str(e_public))
            try:
                logger.debug("Attempting token exchange (internal) %s for client_id=%s", internal_token_url, self.client_id)
                response = requests.post(internal_token_url, data=data, timeout=5)
                logger.debug("Response (internal) status=%s body=%s", response.status_code, response.text)
                response.raise_for_status()
                token_json = response.json()
                logger.info("Token exchange (internal) successful for client_id=%s", self.client_id)
                return token_json
            except requests.exceptions.RequestException as e_internal:
                logger.error("Internal token exchange failed: %s", str(e_internal))
                return None
    
    def get_user_info(self, access_token):
        """Get user information from access token"""
        try:
            # Decode token without verification for development
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            logger.debug("Decoded access token keys: %s", list(decoded_token.keys()))
            user_info = {
                "username": decoded_token.get("preferred_username"),
                "email": decoded_token.get("email"),
                "first_name": decoded_token.get("given_name"),
                "last_name": decoded_token.get("family_name"),
                "roles": decoded_token.get("realm_access", {}).get("roles", [])
            }
            logger.info("Extracted user info for username=%s roles=%s", user_info.get('username'), user_info.get('roles'))
            return user_info
        except Exception as e:
            logger.error("Error decoding token: %s", str(e))
            return None
    
    def has_admin_role(self, user_info):
        """Check if user info contains admin role"""
        if user_info and isinstance(user_info, dict):
            roles = user_info.get("roles", [])
            return "admin" in roles
        return False
    
    def validate_token(self, access_token):
        """Validate access token"""
        try:
            # For production, implement proper token validation
            # For development, we'll just check if token exists and is not expired
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            exp = decoded_token.get("exp")
            if exp:
                expiry = datetime.fromtimestamp(exp)
                logger.debug("Token expires at %s (now=%s)", expiry.isoformat(), datetime.now().isoformat())
                if expiry > datetime.now():
                    return True
                logger.info("Token expired at %s", expiry.isoformat())
                return False
            logger.warning("Token has no exp claim")
            return False
        except Exception as e:
            logger.error("Error validating token: %s", str(e))
            return False
    
    def get_admin_token(self, username=None, password=None):
        """Get admin token using password grant for embedded login"""
        if not username or not password:
            logger.error("Username and password are required for embedded login")
            return None

        # Use password grant with the confidential client
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": username,
            "password": password,
            "scope": "openid profile email roles"
        }

        # Token endpoint URLs (public + internal fallback)
        public_token_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
        # Use internal URL for docker-compose communication (HTTP within secure container network)
        internal_keycloak_url = os.getenv("KEYCLOAK_INTERNAL_URL", "http://keycloak:8080")
        internal_token_url = f"{internal_keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"

        # Try public URL first, then internal
        try:
            logger.debug("Requesting admin token (public) %s for client_id=%s", public_token_url, self.client_id)
            response = requests.post(public_token_url, data=data, timeout=5)
            logger.debug("Response (public) status=%s body=%s", getattr(response, "status_code", None), getattr(response, "text", None))
            response.raise_for_status()
            logger.info("Admin token obtained (public) for client_id=%s", self.client_id)
            return response.json()
        except requests.exceptions.RequestException as e_public:
            # If we have a response object, include its body for diagnostics
            body = ""
            try:
                body = getattr(e_public.response, "text", "") if hasattr(e_public, "response") else ""
            except Exception:
                body = ""
            logger.warning("Public admin token request failed: %s; response_body=%s", str(e_public), body)
            try:
                logger.debug("Requesting admin token (internal) %s for client_id=%s", internal_token_url, self.client_id)
                response = requests.post(internal_token_url, data=data, timeout=5)
                logger.debug("Response (internal) status=%s body=%s", getattr(response, "status_code", None), getattr(response, "text", None))
                response.raise_for_status()
                logger.info("Admin token obtained (internal) for client_id=%s", self.client_id)
                return response.json()
            except requests.exceptions.RequestException as e_internal:
                body_int = ""
                try:
                    body_int = getattr(e_internal.response, "text", "") if hasattr(e_internal, "response") else ""
                except Exception:
                    body_int = ""
                logger.error("Internal admin token request failed: %s; response_body=%s", str(e_internal), body_int)
                return None
    
    def logout_url(self, redirect_uri=None):
        """Generate logout URL"""
        logout_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/logout"
        if redirect_uri:
            logout_url += f"?redirect_uri={redirect_uri}"
        return logout_url

# Global auth instance
keycloak_auth = KeycloakAuth()

def require_admin(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This would be implemented in the callback context
        # For now, we'll return the original function
        return f(*args, **kwargs)
    return decorated_function