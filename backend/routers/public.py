"""
Public API routes that don't require authentication
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import psycopg2
import os
from datetime import datetime

router = APIRouter(prefix="/public", tags=["public"])

def get_db_connection():
    """Get database connection"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(status_code=500, detail="DATABASE_URL environment variable not set")
        connection = psycopg2.connect(database_url)
        return connection
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@router.post("/visits")
def track_visit(visit_data: Dict[str, Any]):
    """Track a page visit (public endpoint, no authentication required)"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO visits (page, user_agent, ip_address) 
                VALUES (%s, %s, %s)
                RETURNING id, timestamp
            """, (
                visit_data.get('page', 'unknown'),
                visit_data.get('user_agent', ''),
                visit_data.get('ip_address', '')
            ))
            
            result = cursor.fetchone()
            visit_id = result[0]
            timestamp = result[1]
            connection.commit()
            
            return {
                "message": "Visit tracked successfully", 
                "visit_id": visit_id,
                "timestamp": timestamp.isoformat() if timestamp else None,
                "page": visit_data.get('page', 'unknown'),
                "ip_address": visit_data.get('ip_address', '')
            }
            
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

@router.put("/visits/update-ip")
def update_visit_ip(ip_data: Dict[str, Any]):
    """Update IP address for recent visits from the same session (public endpoint)"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            real_ip = ip_data.get('ip_address')
            
            if not real_ip:
                raise HTTPException(status_code=400, detail="IP address required")
            
            # Update recent visits (last 5 minutes) that have 'pending' IP or empty IP
            # This handles cases where JavaScript detects real IP after initial page load
            cursor.execute("""
                UPDATE visits 
                SET ip_address = %s 
                WHERE (ip_address = 'pending' OR ip_address = '' OR ip_address IS NULL)
                  AND timestamp >= NOW() - INTERVAL '5 minutes'
            """, (real_ip,))
            
            updated_count = cursor.rowcount
            connection.commit()
            
            return {
                "message": f"Updated IP address for {updated_count} recent visits",
                "updated_count": updated_count,
                "ip_address": real_ip
            }
            
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()