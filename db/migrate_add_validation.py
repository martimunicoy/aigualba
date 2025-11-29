#!/usr/bin/env python3
"""
Migration script to add validated column to existing mostres table
This script will:
1. Add the validated column with default FALSE
2. Set existing samples to validated=TRUE (since they were previously visible)
3. Create indexes for the new column
"""

import os
import psycopg2
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Get a database connection"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Handle different DATABASE_URL formats
    if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://"):
        return psycopg2.connect(DATABASE_URL)
    else:
        # Handle format like "localhost:5433/aigualba_db"
        if "://" not in DATABASE_URL:
            # Parse host:port/database format
            parts = DATABASE_URL.split("/")
            if len(parts) != 2:
                raise ValueError("Invalid DATABASE_URL format. Expected: host:port/database or postgresql://user:pass@host:port/database")
            
            host_port, database = parts
            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host = host_port
                port = "5432"
            
            # Use environment variables for user/password if available, otherwise defaults
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "")
            
            conn_string = f"host={host} port={port} dbname={database} user={user}"
            if password:
                conn_string += f" password={password}"
                
            return psycopg2.connect(conn_string)
        else:
            return psycopg2.connect(DATABASE_URL)

def run_migration():
    """Run the validation migration"""
    try:
        print(f"Attempting to connect to database with URL: {DATABASE_URL}")
        conn = get_db_connection()
        cur = conn.cursor()
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        print("\nTroubleshooting tips:")
        print("1. If running outside Docker, make sure PostgreSQL is accessible on localhost")
        print("2. Replace 'db' with 'localhost' in your DATABASE_URL if needed")
        print("3. Ensure the database service is running")
        print(f"   Current DATABASE_URL: {DATABASE_URL}")
        raise
    
    try:
        print("✓ Connected to database successfully")
        print("Starting validation column migration...")
        
        # Check if column already exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='mostres' AND column_name='validated'
        """)
        
        if cur.fetchone():
            print("✓ Validated column already exists, skipping migration")
            return
        
        # Add the validated column with default FALSE
        print("Adding validated column...")
        cur.execute("""
            ALTER TABLE mostres 
            ADD COLUMN validated BOOLEAN DEFAULT FALSE
        """)
        
        # Set existing samples to validated=TRUE (they were previously visible)
        print("Setting existing samples as validated...")
        cur.execute("""
            UPDATE mostres 
            SET validated = TRUE 
            WHERE validated IS NULL OR validated = FALSE
        """)
        
        # Add index for better performance
        print("Creating index on validated column...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mostres_validated ON mostres(validated)
        """)
        
        # Add comment to the new column
        cur.execute("""
            COMMENT ON COLUMN mostres.validated IS 'Whether the sample has been admin-validated for public display'
        """)
        
        # Commit all changes
        conn.commit()
        print("✓ Migration completed successfully!")
        
        # Show summary
        cur.execute("SELECT COUNT(*) FROM mostres WHERE validated = TRUE")
        validated_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM mostres WHERE validated = FALSE")
        unvalidated_count = cur.fetchone()[0]
        
        print(f"Summary:")
        print(f"  - Validated samples: {validated_count}")
        print(f"  - Unvalidated samples: {unvalidated_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"Migration error: {e}")
        exit(1)