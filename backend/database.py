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
                   acid_monobromoacetic, acid_dibromoacetic, created_at
            FROM mostres 
            ORDER BY data DESC, created_at DESC
        """)
        rows = cur.fetchall()
        
        columns = [
            'id', 'data', 'punt_mostreig', 'temperatura', 'clor_lliure', 'clor_total',
            'recompte_escherichia_coli', 'recompte_enterococ', 'recompte_microorganismes_aerobis_22c',
            'recompte_coliformes_totals', 'conductivitat_20c', 'ph', 'terbolesa', 'color', 'olor', 'sabor',
            'acid_monocloroacetic', 'acid_dicloroacetic', 'acid_tricloroacetic',
            'acid_monobromoacetic', 'acid_dibromoacetic', 'created_at'
        ]
        
        return [dict(zip(columns, row)) for row in rows]
    finally:
        cur.close()
        conn.close()

def create_mostre(mostre_data: Dict[str, Any]) -> int:
    """Create a new sample entry and return the new ID"""
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