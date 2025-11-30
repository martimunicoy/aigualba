"""
Keycloak authentication utilities for Aigualba
"""
import os
import jwt
import requests
from datetime import datetime, timedelta
from functools import wraps
from dash import callback_context
import json

class KeycloakAuth:
    def __init__(self):
        self.keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
        self.realm = os.getenv("KEYCLOAK_REALM", "aigualba")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID", "aigualba-frontend")
        self.client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET", "aigualba-frontend-secret-123")
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
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        # Prefer the configured KEYCLOAK_URL (works for local dev and proxied production).
        # If that fails (e.g. frontend running inside docker needs internal hostname),
        # fall back to the container-internal hostname replacement.
        public_token_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
        internal_keycloak_url = self.keycloak_url.replace('localhost', 'keycloak')
        internal_token_url = f"{internal_keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"

        try:
            # Try public URL first
            response = requests.post(public_token_url, data=data, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception:
            try:
                # Fallback to internal URL (useful when running inside docker-compose)
                response = requests.post(internal_token_url, data=data, timeout=5)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error exchanging code for token: {e}")
                return None
    
    def get_user_info(self, access_token):
        """Get user information from access token"""
        try:
            # Decode token without verification for development
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            
            user_info = {
                "username": decoded_token.get("preferred_username"),
                "email": decoded_token.get("email"),
                "first_name": decoded_token.get("given_name"),
                "last_name": decoded_token.get("family_name"),
                "roles": decoded_token.get("realm_access", {}).get("roles", [])
            }
            
            return user_info
        except Exception as e:
            print(f"Error decoding token: {e}")
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
            if exp and datetime.fromtimestamp(exp) > datetime.now():
                return True
            return False
        except Exception as e:
            print(f"Error validating token: {e}")
            return False
    
    def get_admin_token(self, username, password):
        """Get admin token using direct grant for development"""
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": username,
            "password": password,
            "scope": "openid profile email roles"
        }

        public_token_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
        internal_keycloak_url = self.keycloak_url.replace('localhost', 'keycloak')
        internal_token_url = f"{internal_keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"

        try:
            response = requests.post(public_token_url, data=data, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception:
            try:
                response = requests.post(internal_token_url, data=data, timeout=5)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error getting admin token: {e}")
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