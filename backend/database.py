"""
Database operations for the Aigualba backend
"""

import os
import psycopg2
from typing import List, Dict, Any, Optional

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Get a database connection"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def fetch_parameters() -> List[Dict[str, Any]]:
    """Fetch water quality parameters from the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name, value, updated_at FROM parameters;")
        rows = cur.fetchall()
        return [{"name": r[0], "value": r[1], "updated_at": r[2]} for r in rows]
    finally:
        cur.close()
        conn.close()

def fetch_mostres() -> List[Dict[str, Any]]:
    """Fetch all sample data from mostres table"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, data, punt_mostreig, temperatura, clor_lliure, clor_total,
                   recompte_escherichia_coli, recompte_enterococ, recompte_microorganismes_aerobis_22c,
                   recompte_coliformes_totals, conductivitat_20c, ph, terbolesa, color, olor, sabor,
                   acid_monocloroacetic, acid_dicloroacetic, acid_tricloroacetic,
                   acid_monobromoacetic, acid_dibromoacetic, created_at, validated
            FROM mostres 
            WHERE validated = TRUE
            ORDER BY data DESC, created_at DESC
        """)
        rows = cur.fetchall()
        
        columns = [
            'id', 'data', 'punt_mostreig', 'temperatura', 'clor_lliure', 'clor_total',
            'recompte_escherichia_coli', 'recompte_enterococ', 'recompte_microorganismes_aerobis_22c',
            'recompte_coliformes_totals', 'conductivitat_20c', 'ph', 'terbolesa', 'color', 'olor', 'sabor',
            'acid_monocloroacetic', 'acid_dicloroacetic', 'acid_tricloroacetic',
            'acid_monobromoacetic', 'acid_dibromoacetic', 'created_at', 'validated'
        ]
        
        return [dict(zip(columns, row)) for row in rows]
    finally:
        cur.close()
        conn.close()

def create_mostre(mostre_data: Dict[str, Any]) -> int:
    """Create a new sample entry with validated=FALSE by default and return the new ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Build dynamic query based on provided fields
        fields = []
        values = []
        placeholders = []
        
        for field, value in mostre_data.items():
            if value is not None:
                fields.append(field)
                values.append(value)
                placeholders.append("%s")
        
        if not fields:
            raise ValueError("At least one field must be provided")
        
        # Explicitly set validated to FALSE for new submissions
        fields.append('validated')
        values.append(False)
        placeholders.append("%s")
        
        query = f"""
            INSERT INTO mostres ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
        """
        
        cur.execute(query, values)
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        cur.close()
        conn.close()

def fetch_all_mostres() -> List[Dict[str, Any]]:
    """Fetch ALL sample data from mostres table (including unvalidated) - ADMIN ONLY"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, data, punt_mostreig, temperatura, clor_lliure, clor_total,
                   recompte_escherichia_coli, recompte_enterococ, recompte_microorganismes_aerobis_22c,
                   recompte_coliformes_totals, conductivitat_20c, ph, terbolesa, color, olor, sabor,
                   acid_monocloroacetic, acid_dicloroacetic, acid_tricloroacetic,
                   acid_monobromoacetic, acid_dibromoacetic, created_at, validated
            FROM mostres 
            ORDER BY validated ASC, data DESC, created_at DESC
        """)
        rows = cur.fetchall()
        
        columns = [
            'id', 'data', 'punt_mostreig', 'temperatura', 'clor_lliure', 'clor_total',
            'recompte_escherichia_coli', 'recompte_enterococ', 'recompte_microorganismes_aerobis_22c',
            'recompte_coliformes_totals', 'conductivitat_20c', 'ph', 'terbolesa', 'color', 'olor', 'sabor',
            'acid_monocloroacetic', 'acid_dicloroacetic', 'acid_tricloroacetic',
            'acid_monobromoacetic', 'acid_dibromoacetic', 'created_at', 'validated'
        ]
        
        return [dict(zip(columns, row)) for row in rows]
    finally:
        cur.close()
        conn.close()

def validate_mostre(sample_id: int) -> bool:
    """Validate a sample (set validated=TRUE) - ADMIN ONLY"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE mostres 
            SET validated = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (sample_id,))
        
        success = cur.rowcount > 0
        conn.commit()
        return success
    finally:
        cur.close()
        conn.close()

def invalidate_mostre(sample_id: int) -> bool:
    """Invalidate a sample (set validated=FALSE) - ADMIN ONLY"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE mostres 
            SET validated = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (sample_id,))
        
        success = cur.rowcount > 0
        conn.commit()
        return success
    finally:
        cur.close()
        conn.close()