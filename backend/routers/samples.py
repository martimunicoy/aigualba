from fastapi import APIRouter, HTTPException
from models import MostreData
from database import fetch_mostres, create_mostre, fetch_all_mostres, validate_mostre, invalidate_mostre

router = APIRouter(prefix="/api/mostres", tags=["samples"])


@router.get("/")
def read_samples():
    """Get all sample data from mostres table"""
    try:
        return fetch_mostres()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching samples: {str(e)}")


@router.get("/{sample_id}")
def read_sample(sample_id: int):
    """Get a specific sample by ID"""
    try:
        samples = fetch_mostres()
        for sample in samples:
            if sample.get('id') == sample_id:
                return sample
        raise HTTPException(status_code=404, detail=f"Sample with id {sample_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sample: {str(e)}")

@router.post("/")
def create_sample(mostre: MostreData):
    """Create a new sample entry (will be unvalidated by default)"""
    try:
        new_id = create_mostre(mostre.dict())
        return {
            "message": "Mostra pujada amb èxit. Serà visible un cop validada per un administrador.", 
            "id": new_id,
            "validated": False
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sample: {str(e)}")

# Admin-only endpoints
@router.get("/admin/all")
def read_all_samples():
    """Get all sample data including unvalidated samples - ADMIN ONLY"""
    try:
        return fetch_all_mostres()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching all samples: {str(e)}")

@router.post("/{sample_id}/validate")
def validate_sample(sample_id: int):
    """Validate a sample to make it visible to public - ADMIN ONLY"""
    try:
        success = validate_mostre(sample_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Sample with id {sample_id} not found")
        return {"message": f"Sample {sample_id} validated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating sample: {str(e)}")

@router.post("/{sample_id}/invalidate")
def invalidate_sample(sample_id: int):
    """Invalidate a sample to hide it from public view - ADMIN ONLY"""
    try:
        success = invalidate_mostre(sample_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Sample with id {sample_id} not found")
        return {"message": f"Sample {sample_id} invalidated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invalidating sample: {str(e)}")
