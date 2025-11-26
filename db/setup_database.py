import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database configuration with defaults
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
DEV_POSTGRES_USER = os.getenv("DEV_POSTGRES_USER", "devuser")
DEV_POSTGRES_PASSWORD = os.getenv("DEV_POSTGRES_PASSWORD", "devpass")
DEV_POSTGRES_DB = os.getenv("DEV_POSTGRES_DB", "aigualba_db")
DEV_DATABASE_URL = os.getenv("DEV_DATABASE_URL")

# Determine the database host and environment
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = "5433" if DB_HOST == "localhost" else "5432"

# Determine if we're in development mode
IS_DEVELOPMENT = DB_HOST == "localhost" and DB_PORT == "5433"

if IS_DEVELOPMENT:
    # In development, the Docker container creates devuser as the superuser
    ADMIN_USER = DEV_POSTGRES_USER  
    ADMIN_PASSWORD = DEV_POSTGRES_PASSWORD
    # For setup script, we connect to localhost:5433 (port forwarded from Docker)
    ADMIN_DB_URL = f"postgresql://{ADMIN_USER}:{ADMIN_PASSWORD}@localhost:5433/postgres"
    TARGET_DB_URL = f"postgresql://{ADMIN_USER}:{ADMIN_PASSWORD}@localhost:5433/{DEV_POSTGRES_DB}"
else:
    # Production environment
    ADMIN_USER = POSTGRES_USER
    ADMIN_PASSWORD = POSTGRES_PASSWORD  
    ADMIN_DB_URL = f"postgresql://{ADMIN_USER}:{ADMIN_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
    TARGET_DB_URL = f"postgresql://{ADMIN_USER}:{ADMIN_PASSWORD}@{DB_HOST}:{DB_PORT}/{DEV_POSTGRES_DB}"

def database_exists(cursor, db_name):
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (db_name,)
    )
    return cursor.fetchone() is not None

def user_exists(cursor, username):
    cursor.execute(
        "SELECT 1 FROM pg_roles WHERE rolname = %s",
        (username,)
    )
    return cursor.fetchone() is not None

def ensure_application_tables():
    conn = None
    try:
        conn = psycopg2.connect(TARGET_DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Create parameters table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS parameters (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                value VARCHAR(255) NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Parameters table created or verified.")
        
        # Create mostres table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mostres (
                id SERIAL PRIMARY KEY,
                data DATE NOT NULL,
                punt_mostreig VARCHAR(255) NOT NULL,
                temperatura DECIMAL(5,2), -- en Celsius
                clor_lliure DECIMAL(10,4), -- mg Cl2/l
                clor_total DECIMAL(10,4), -- mg Cl2/l
                recompte_escherichia_coli DECIMAL(10,2), -- NPM/100 ml
                recompte_enterococ DECIMAL(10,2), -- NPM/100 ml
                recompte_microorganismes_aerobis_22c DECIMAL(15,2), -- ufc/1 ml
                recompte_coliformes_totals DECIMAL(10,2), -- NMP/100 ml
                conductivitat_20c DECIMAL(10,2), -- 148 uS/cm
                ph DECIMAL(4,2), -- unitat de pH
                terbolesa DECIMAL(10,2), -- UNF
                color DECIMAL(10,2), -- mg/l Pt-Co
                olor DECIMAL(10,2), -- index dilució a 25ºC
                sabor DECIMAL(10,2), -- index dilució a 25ºC
                acid_monocloroacetic DECIMAL(10,2), -- ug/l
                acid_dicloroacetic DECIMAL(10,2), -- ug/l
                acid_tricloroacetic DECIMAL(10,2), -- ug/l
                acid_monobromoacetic DECIMAL(10,2), -- ug/l
                acid_dibromoacetic DECIMAL(10,2), -- ug/l
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Mostres table created or verified.")
        
        # Seed parameters table only if empty
        cur.execute("SELECT COUNT(*) FROM parameters;")
        result = cur.fetchone()
        count = result[0] if result else 0
        
        if count == 0:
            cur.execute("""
                INSERT INTO parameters (name, value) VALUES
                ('pH', '7.0'),
                ('Temperature', '25.0');
            """)
            print("Seeded parameters table.")
        else:
            print("Parameters table already seeded.")
        cur.close()
    except psycopg2.Error as e:
        print(f"Error ensuring application tables: {e}")
    finally:
        if conn:
            conn.close()

def setup_database():
    if IS_DEVELOPMENT:
        print("Development mode: Database and user should already be created by Docker.")
        print(f"Connecting to database '{DEV_POSTGRES_DB}' as user '{DEV_POSTGRES_USER}'.")
        
        # In development, just ensure the application tables exist
        ensure_application_tables()
        return
    
    # Production setup - create database and user if needed
    conn = None
    try:
        conn = psycopg2.connect(ADMIN_DB_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        if not database_exists(cursor, DEV_POSTGRES_DB):
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DEV_POSTGRES_DB)))
            print(f"Database '{DEV_POSTGRES_DB}' created.")
        else:
            print(f"Database '{DEV_POSTGRES_DB}' already exists.")

        if not user_exists(cursor, DEV_POSTGRES_USER):
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(DEV_POSTGRES_USER)),
                [DEV_POSTGRES_PASSWORD],
            )
            print(f"User '{DEV_POSTGRES_USER}' created.")
        else:
            print(f"User '{DEV_POSTGRES_USER}' already exists.")

        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(DEV_POSTGRES_DB),
                sql.Identifier(DEV_POSTGRES_USER),
            )
        )
        print(f"Privileges granted on '{DEV_POSTGRES_DB}' to '{DEV_POSTGRES_USER}'.")
        cursor.close()
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

    # Ensure application tables
    ensure_application_tables()

if __name__ == "__main__":
    setup_database()
