#!/usr/bin/env python3
"""
Database migration script to remove clor_combinat column from mostres table

This script safely removes the clor_combinat column since it can be calculated
as clor_total - clor_lliure when needed.

Usage:
    python migrate_remove_clor_combinat.py
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
DEV_POSTGRES_USER = os.getenv("DEV_POSTGRES_USER", "devuser")
DEV_POSTGRES_PASSWORD = os.getenv("DEV_POSTGRES_PASSWORD", "devpass")
DEV_POSTGRES_DB = os.getenv("DEV_POSTGRES_DB", "aigualba_db")

# Determine the database host and environment
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = "5433" if DB_HOST == "localhost" else "5432"

# Determine if we're in development mode
IS_DEVELOPMENT = DB_HOST == "localhost" and DB_PORT == "5433"

if IS_DEVELOPMENT:
    ADMIN_USER = DEV_POSTGRES_USER  
    ADMIN_PASSWORD = DEV_POSTGRES_PASSWORD
    TARGET_DB_URL = f"postgresql://{ADMIN_USER}:{ADMIN_PASSWORD}@localhost:5433/{DEV_POSTGRES_DB}"
else:
    ADMIN_USER = POSTGRES_USER
    ADMIN_PASSWORD = POSTGRES_PASSWORD  
    TARGET_DB_URL = f"postgresql://{ADMIN_USER}:{ADMIN_PASSWORD}@{DB_HOST}:{DB_PORT}/{DEV_POSTGRES_DB}"

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = %s 
            AND column_name = %s
        );
    """, (table_name, column_name))
    return cursor.fetchone()[0]

def migrate_remove_clor_combinat():
    """Remove clor_combinat column from mostres table"""
    conn = None
    try:
        conn = psycopg2.connect(TARGET_DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if the column exists
        if column_exists(cur, 'mostres', 'clor_combinat'):
            print("Found clor_combinat column in mostres table.")
            
            # Show some statistics before removing
            cur.execute("SELECT COUNT(*) FROM mostres WHERE clor_combinat IS NOT NULL;")
            count = cur.fetchone()[0]
            print(f"Found {count} records with clor_combinat values.")
            
            if count > 0:
                # Show some sample data
                cur.execute("""
                    SELECT id, data, clor_lliure, clor_total, clor_combinat,
                           (clor_total - clor_lliure) as calculated_combined
                    FROM mostres 
                    WHERE clor_combinat IS NOT NULL 
                    LIMIT 5;
                """)
                samples = cur.fetchall()
                print("\nSample data before migration:")
                print("ID | Date | Free | Total | Stored Combined | Calculated Combined")
                print("-" * 65)
                for sample in samples:
                    print(f"{sample[0]} | {sample[1]} | {sample[2]} | {sample[3]} | {sample[4]} | {sample[5]}")
            
            # Remove the column
            print("\nRemoving clor_combinat column...")
            cur.execute("ALTER TABLE mostres DROP COLUMN clor_combinat;")
            print("✓ clor_combinat column removed successfully.")
            
        else:
            print("clor_combinat column not found in mostres table. No migration needed.")
        
        # Verify the final table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'mostres' 
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        print("\nFinal table structure:")
        print("Column Name | Data Type")
        print("-" * 30)
        for col in columns:
            print(f"{col[0]} | {col[1]}")
        
        cur.close()
        print("\n✓ Migration completed successfully!")
        
    except psycopg2.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    print("=== Aigualba Database Migration: Remove clor_combinat ===\n")
    
    print(f"Target database: {DEV_POSTGRES_DB}")
    print(f"Environment: {'Development' if IS_DEVELOPMENT else 'Production'}")
    print(f"Database URL: {TARGET_DB_URL.split('@')[1]}")  # Hide credentials
    print()
    
    confirmation = input("Do you want to proceed with removing the clor_combinat column? (y/N): ")
    if confirmation.lower() in ['y', 'yes']:
        migrate_remove_clor_combinat()
    else:
        print("Migration cancelled.")