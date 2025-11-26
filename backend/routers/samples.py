from fastapi import APIRouter, HTTPException
from models import MostreData
from database import fetch_mostres, create_mostre

router = APIRouter(prefix="/api/mostres", tags=["samples"])


@router.get("/")
def read_samples():
    """Get all sample data from mostres table"""
    try:
        return fetch_mostres()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching samples: {str(e)}")


@router.post("/")
def create_sample(mostre: MostreData):
    """Create a new sample entry"""
    try:
        new_id = create_mostre(mostre.dict())
        return {"message": "Sample created successfully", "id": new_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sample: {str(e)}")
