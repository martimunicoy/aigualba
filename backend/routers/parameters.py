from fastapi import APIRouter, HTTPException
from database import fetch_parameters

router = APIRouter(prefix="/api/parameters", tags=["parameters"])


@router.get("/")
def read_parameters():
    """Get all water quality parameters"""
    try:
        return fetch_parameters()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching parameters: {str(e)}")
