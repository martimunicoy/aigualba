"""
Admin API routes for sample management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
import psycopg2
import os
from datetime import datetime
import json

router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer()

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

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin authentication token"""
    # In production, implement proper JWT token verification
    # For development, we'll accept any token that starts with 'admin-'
    token = credentials.credentials
    if not token or not token.startswith('admin-'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.get("/samples")
def get_all_samples_admin(token: str = Depends(verify_admin_token)):
    """Get all samples with validation status for admin management"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, data, punt_mostreig, temperatura, ph, conductivitat_20c, 
                       terbolesa, color, olor, sabor, clor_lliure, clor_total,
                       acid_monocloroacetic, acid_dicloroacetic, acid_tricloroacetic,
                       acid_monobromoacetic, acid_dibromoacetic,
                       recompte_escherichia_coli, recompte_enterococ,
                       recompte_microorganismes_aerobis_22c, recompte_coliformes_totals,
                       validated, created_at
                FROM mostres
                ORDER BY created_at DESC
            """)
            
            columns = [desc[0] for desc in cursor.description]
            samples = []
            
            for row in cursor.fetchall():
                sample = dict(zip(columns, row))
                # Convert date to string if it's a date object
                if sample.get('data') and hasattr(sample['data'], 'strftime'):
                    sample['data'] = sample['data'].strftime('%Y-%m-%d')
                if sample.get('created_at') and hasattr(sample['created_at'], 'isoformat'):
                    sample['created_at'] = sample['created_at'].isoformat()
                samples.append(sample)
            
            return samples
            
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

@router.patch("/samples/{sample_id}/validate")
def validate_sample(
    sample_id: int, 
    validation_data: Dict[str, bool],
    token: str = Depends(verify_admin_token)
):
    """Update sample validation status"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            validated = validation_data.get("validated", True)
            cursor.execute(
                "UPDATE mostres SET validated = %s WHERE id = %s",
                (validated, sample_id)
            )
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Sample not found")
            
            connection.commit()
            return {"message": f"Sample {sample_id} validation status updated to {validated}"}
            
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

@router.delete("/samples/{sample_id}")
def delete_sample(sample_id: int, token: str = Depends(verify_admin_token)):
    """Delete a sample"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM mostres WHERE id = %s", (sample_id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Sample not found")
            
            connection.commit()
            return {"message": f"Sample {sample_id} deleted successfully"}
            
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

@router.put("/samples/{sample_id}")
def update_sample(
    sample_id: int, 
    sample_data: Dict[str, Any],
    token: str = Depends(verify_admin_token)
):
    """Update sample data"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # First check if sample exists
            cursor.execute("SELECT id FROM mostres WHERE id = %s", (sample_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Sample not found")
            
            # Build dynamic update query
            update_fields = []
            values = []
            
            allowed_fields = {
                'data', 'punt_mostreig', 'temperatura', 'ph', 'conductivitat_20c',
                'terbolesa', 'color', 'olor', 'sabor', 'clor_lliure', 'clor_total',
                'acid_monocloroacetic', 'acid_dicloroacetic', 'acid_tricloroacetic',
                'acid_monobromoacetic', 'acid_dibromoacetic',
                'recompte_escherichia_coli', 'recompte_enterococ',
                'recompte_microorganismes_aerobis_22c', 'recompte_coliformes_totals',
                'validated'
            }
            
            for field, value in sample_data.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = %s")
                    values.append(value)
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No valid fields to update")
            
            values.append(sample_id)  # For WHERE clause
            
            update_query = f"""
                UPDATE mostres 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING *
            """
            
            cursor.execute(update_query, values)
            updated_row = cursor.fetchone()
            
            if updated_row:
                columns = [desc[0] for desc in cursor.description]
                updated_sample = dict(zip(columns, updated_row))
                
                # Convert date to string if it's a date object
                if updated_sample.get('data') and hasattr(updated_sample['data'], 'strftime'):
                    updated_sample['data'] = updated_sample['data'].strftime('%Y-%m-%d')
                if updated_sample.get('created_at') and hasattr(updated_sample['created_at'], 'isoformat'):
                    updated_sample['created_at'] = updated_sample['created_at'].isoformat()
                
                connection.commit()
                return updated_sample
            else:
                raise HTTPException(status_code=500, detail="Failed to update sample")
            
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

@router.post("/samples/bulk-validate")
def bulk_validate_samples(
    bulk_data: Dict[str, Any],
    token: str = Depends(verify_admin_token)
):
    """Bulk validate/unvalidate samples"""
    connection = get_db_connection()
    try:
        sample_ids = bulk_data.get("sample_ids", [])
        validated = bulk_data.get("validated", True)
        
        if not sample_ids:
            raise HTTPException(status_code=400, detail="No sample IDs provided")
        
        with connection.cursor() as cursor:
            # Use tuple format for IN clause
            placeholders = ','.join(['%s'] * len(sample_ids))
            cursor.execute(
                f"UPDATE mostres SET validated = %s WHERE id IN ({placeholders})",
                [validated] + sample_ids
            )
            
            updated_count = cursor.rowcount
            connection.commit()
            
            return {
                "message": f"Bulk validation updated for {updated_count} samples",
                "updated_count": updated_count
            }
            
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

@router.get("/statistics")
def get_admin_statistics(token: str = Depends(verify_admin_token)):
    """Get statistics for admin dashboard"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Total samples
            cursor.execute("SELECT COUNT(*) FROM mostres")
            total_samples = cursor.fetchone()[0]
            
            # Validated samples
            cursor.execute("SELECT COUNT(*) FROM mostres WHERE validated = true")
            validated_samples = cursor.fetchone()[0]
            
            # Pending samples
            pending_samples = total_samples - validated_samples
            
            # Samples by location
            cursor.execute("""
                SELECT punt_mostreig, COUNT(*) 
                FROM mostres 
                GROUP BY punt_mostreig
                ORDER BY COUNT(*) DESC
            """)
            samples_by_location = dict(cursor.fetchall())
            
            # Recent samples (last 5)
            cursor.execute("""
                SELECT id, data, punt_mostreig, validated, created_at
                FROM mostres
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            columns = ['id', 'data', 'punt_mostreig', 'validated', 'created_at']
            recent_samples = []
            
            for row in cursor.fetchall():
                sample = dict(zip(columns, row))
                if sample.get('data') and hasattr(sample['data'], 'strftime'):
                    sample['data'] = sample['data'].strftime('%Y-%m-%d')
                if sample.get('created_at') and hasattr(sample['created_at'], 'isoformat'):
                    sample['created_at'] = sample['created_at'].isoformat()
                recent_samples.append(sample)
            
            # Get visits statistics for last 7 days
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as visit_date,
                    COUNT(*) as visits
                FROM visits 
                WHERE timestamp >= NOW() - INTERVAL '7 days'
                GROUP BY DATE(timestamp)
                ORDER BY visit_date ASC
            """)
            
            visits_data = []
            for row in cursor.fetchall():
                visits_data.append({
                    "date": row[0].strftime('%Y-%m-%d'),
                    "visits": row[1]
                })
            
            # Get monthly visits statistics for last year (including months with 0 visits)
            cursor.execute("""
                WITH months AS (
                    SELECT DATE_TRUNC('month', generate_series(
                        NOW() - INTERVAL '1 year',
                        NOW(),
                        INTERVAL '1 month'
                    )) as month_date
                )
                SELECT 
                    m.month_date,
                    COALESCE(COUNT(v.timestamp), 0) as visits
                FROM months m
                LEFT JOIN visits v ON DATE_TRUNC('month', v.timestamp) = m.month_date
                GROUP BY m.month_date
                ORDER BY m.month_date ASC
            """)
            
            visits_monthly_data = []
            for row in cursor.fetchall():
                visits_monthly_data.append({
                    "month": row[0].strftime('%Y-%m'),
                    "visits": row[1]
                })
            
            # Get total visits for last 30 days
            cursor.execute("""
                SELECT COUNT(*) FROM visits 
                WHERE timestamp >= NOW() - INTERVAL '30 days'
            """)
            total_visits = cursor.fetchone()[0]
            
            return {
                "total_samples": total_samples,
                "validated_samples": validated_samples,
                "pending_samples": pending_samples,
                "samples_by_location": samples_by_location,
                "recent_samples": recent_samples,
                "visits_last_7_days": visits_data,
                "visits_last_year_monthly": visits_monthly_data,
                "total_visits_30_days": total_visits
            }
            
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

@router.get("/logs/{service}")
def get_service_logs(
    service: str, 
    lines: int = 100,
    token: str = Depends(verify_admin_token)
):
    """Get logs for a specific service"""
    import subprocess
    import datetime
    
    # Map service names to container names
    service_containers = {
        "backend": "aigualba-backend-1",
        "frontend": "aigualba-frontend-1", 
        "database": "aigualba-db-1",
        "nginx": "aigualba-nginx-1",
        "keycloak": "aigualba_keycloak_dev"
    }
    
    if service not in service_containers:
        raise HTTPException(status_code=400, detail=f"Unknown service: {service}")
    
    container_name = service_containers[service]
    
    try:
        # Try to get logs using docker command
        result = subprocess.run(
            ["docker", "logs", container_name, "--tail", str(lines)], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            logs = result.stdout.split('\n')
            # Also include stderr if available
            if result.stderr:
                logs.extend(['--- STDERR ---'] + result.stderr.split('\n'))
            
            # Filter out empty lines
            logs = [line for line in logs if line.strip()]
            
            return {
                "service": service,
                "container": container_name,
                "logs": logs,
                "timestamp": datetime.datetime.now().isoformat(),
                "lines_requested": lines,
                "lines_returned": len(logs)
            }
        else:
            return {
                "service": service,
                "container": container_name,
                "logs": [f"Error getting logs: {result.stderr}"],
                "timestamp": datetime.datetime.now().isoformat(),
                "error": True
            }
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout getting logs")
    except FileNotFoundError:
        # Docker not available, return system info
        return {
            "service": service,
            "container": container_name,
            "logs": [
                f"Docker CLI not available in container",
                f"Cannot fetch logs for {service}",
                f"This endpoint requires Docker CLI access"
            ],
            "timestamp": datetime.datetime.now().isoformat(),
            "error": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")

@router.get("/logs")
def get_all_services_logs(
    lines: int = 50,
    token: str = Depends(verify_admin_token)
):
    """Get logs for all services"""
    from datetime import datetime
    
    services = ["backend", "frontend", "database", "nginx", "keycloak"]
    all_logs = {}
    
    for service in services:
        try:
            # Get logs for each service
            service_logs = get_service_logs(service, lines, token)
            all_logs[service] = service_logs
        except Exception as e:
            all_logs[service] = {
                "service": service,
                "logs": [f"Error fetching logs: {str(e)}"],
                "error": True
            }
    
    return {
        "timestamp": datetime.now().isoformat(),
        "services": all_logs
    }

@router.get("/visits")
def get_visits_statistics(
    days: int = 30,
    token: str = Depends(verify_admin_token)
):
    """Get visits statistics for the last N days"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Get visits by day for the last N days
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as visit_date,
                    COUNT(*) as visits,
                    COUNT(DISTINCT ip_address) as unique_visitors
                FROM visits 
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(timestamp)
                ORDER BY visit_date ASC
            """, (days,))
            
            daily_visits = []
            for row in cursor.fetchall():
                daily_visits.append({
                    "date": row[0].strftime('%Y-%m-%d'),
                    "visits": row[1],
                    "unique_visitors": row[2]
                })
            
            # Get visits by page for the last N days
            cursor.execute("""
                SELECT 
                    page,
                    COUNT(*) as visits,
                    COUNT(DISTINCT ip_address) as unique_visitors
                FROM visits 
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                GROUP BY page
                ORDER BY visits DESC
            """, (days,))
            
            page_visits = []
            for row in cursor.fetchall():
                page_visits.append({
                    "page": row[0],
                    "visits": row[1],
                    "unique_visitors": row[2]
                })
            
            # Get total visits and unique visitors
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_visits,
                    COUNT(DISTINCT ip_address) as total_unique_visitors
                FROM visits 
                WHERE timestamp >= NOW() - INTERVAL '%s days'
            """, (days,))
            
            totals = cursor.fetchone()
            
            return {
                "period_days": days,
                "total_visits": totals[0] if totals else 0,
                "total_unique_visitors": totals[1] if totals else 0,
                "daily_visits": daily_visits,
                "page_visits": page_visits
            }
            
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

@router.post("/visits")
def track_visit(
    visit_data: Dict[str, Any]
):
    """Track a page visit (no authentication required for tracking)"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO visits (page, user_agent, ip_address) 
                VALUES (%s, %s, %s)
            """, (
                visit_data.get('page', 'unknown'),
                visit_data.get('user_agent', ''),
                visit_data.get('ip_address', '')
            ))
            
            connection.commit()
            return {"message": "Visit tracked successfully"}
            
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()