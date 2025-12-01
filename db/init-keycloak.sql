-- Keycloak database initialization
-- This script creates a separate database for Keycloak to avoid conflicts with the application database

-- Create Keycloak database
CREATE DATABASE keycloak;

-- Create Keycloak user (if not exists)
-- Note: Password will be set via environment variable in init-env.sh
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'keycloak_user') THEN

      -- Password will be updated by init-env.sh script
      CREATE ROLE keycloak_user LOGIN PASSWORD 'temp_password';
   END IF;
END
$do$;

-- Grant privileges to Keycloak user
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak_user;

-- Connect to keycloak database and grant schema privileges
\c keycloak;
GRANT ALL ON SCHEMA public TO keycloak_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO keycloak_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO keycloak_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO keycloak_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO keycloak_user;