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
        # Treat empty/absent secret as "no secret" (public client)
        _cs = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
        self.client_secret = _cs if _cs.strip() else None
        # Flag to indicate frontend is a public client (default true for SPA)
        self.public_client = os.getenv("KEYCLOAK_PUBLIC_CLIENT", "true").lower() in ("1", "true", "yes")
        # Optional separate confidential client to perform admin token requests
        self.admin_client_id = os.getenv("KEYCLOAK_ADMIN_CLIENT_ID")
        _admin_cs = os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET", "")
        self.admin_client_secret = _admin_cs if _admin_cs.strip() else None
        self.redirect_uri = os.getenv("KEYCLOAK_REDIRECT_URI", "http://localhost:8050/admin/callback")
        
        # If KEYCLOAK_PUBLIC_CLIENT is true and a secret was provided, ignore it to avoid sending invalid credentials.
        if self.public_client and self.client_secret:
            logger.info("KEYCLOAK_PUBLIC_CLIENT=true, ignoring KEYCLOAK_CLIENT_SECRET for public frontend client")
            self.client_secret = None

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

        # Prefer the configured KEYCLOAK_URL (works for local dev and proxied production).
        # If that fails (e.g. frontend running inside docker needs internal hostname),
        # fall back to the container-internal hostname replacement.
        public_token_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
        internal_keycloak_url = self.keycloak_url.replace('localhost', 'keycloak')
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
        """Get admin token using direct grant for development

        Behavior:
        - If KEYCLOAK_ADMIN_CLIENT_ID + KEYCLOAK_ADMIN_CLIENT_SECRET provided:
            * If username/password provided: use grant_type=password with confidential client.
            * Else: use grant_type=client_credentials (service account).
        - If KEYCLOAK_ADMIN_CLIENT_ID provided but no secret:
            * Require KEYCLOAK_ADMIN_PUBLIC_CLIENT=true and username/password; use password grant (requires Direct Access Grants in Keycloak).
        - If no admin client configured:
            * Do not attempt password grant with the public frontend client — return None and log instructions.
        """
        # Determine which client to use for admin operations
        admin_public_flag = os.getenv("KEYCLOAK_ADMIN_PUBLIC_CLIENT", "false").lower() in ("1", "true", "yes")

        if self.admin_client_id and self.admin_client_secret:
            # Confidential admin client available
            client_id = self.admin_client_id
            client_secret = self.admin_client_secret
            if username and password:
                data = {
                    "grant_type": "password",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "username": username,
                    "password": password,
                    "scope": "openid profile email roles"
                }
            else:
                # Prefer client_credentials for service-account style tokens
                data = {
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": "openid profile email roles"
                }
        elif self.admin_client_id and not self.admin_client_secret:
            # Admin client exists but is public — only allow if explicitly configured
            if not admin_public_flag:
                logger.error(
                    "Admin client %s is public but KEYCLOAK_ADMIN_PUBLIC_CLIENT not set. "
                    "Set KEYCLOAK_ADMIN_PUBLIC_CLIENT=true to allow password grant with a public admin client, "
                    "or configure a confidential admin client with KEYCLOAK_ADMIN_CLIENT_SECRET.",
                    self.admin_client_id
                )
                return None
            if not username or not password:
                logger.error(
                    "Admin public client %s requires username and password for password grant. "
                    "Provide credentials or configure a confidential client.",
                    self.admin_client_id
                )
                return None
            client_id = self.admin_client_id
            data = {
                "grant_type": "password",
                "client_id": client_id,
                "username": username,
                "password": password,
                "scope": "openid profile email roles"
            }
            logger.warning("Using public admin client %s with password grant; ensure Direct Access Grants are enabled in Keycloak", client_id)
        else:
            # No admin client configured — do not attempt password grant with frontend public client
            logger.error(
                "No KEYCLOAK_ADMIN_CLIENT_ID configured. Refusing to perform password grant using the public frontend client '%s'. "
                "Configure a confidential admin client (KEYCLOAK_ADMIN_CLIENT_ID/KEYCLOAK_ADMIN_CLIENT_SECRET) "
                "or enable an explicit admin public client and set KEYCLOAK_ADMIN_PUBLIC_CLIENT=true.",
                self.client_id
            )
            return None

        # Token endpoint URLs (public + internal fallback)
        public_token_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
        internal_keycloak_url = self.keycloak_url.replace('localhost', 'keycloak')
        internal_token_url = f"{internal_keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"

        # Try public URL first, then internal
        try:
            logger.debug("Requesting admin token (public) %s for client_id=%s", public_token_url, client_id)
            response = requests.post(public_token_url, data=data, timeout=5)
            logger.debug("Response (public) status=%s body=%s", getattr(response, "status_code", None), getattr(response, "text", None))
            response.raise_for_status()
            logger.info("Admin token obtained (public) for client_id=%s", client_id)
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
                logger.debug("Requesting admin token (internal) %s for client_id=%s", internal_token_url, client_id)
                response = requests.post(internal_token_url, data=data, timeout=5)
                logger.debug("Response (internal) status=%s body=%s", getattr(response, "status_code", None), getattr(response, "text", None))
                response.raise_for_status()
                logger.info("Admin token obtained (internal) for client_id=%s", client_id)
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