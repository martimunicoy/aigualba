from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date


class MostreData(BaseModel):
    """Pydantic model for water sample data validation"""
    
    data: date = Field(..., description="Date of the sample")
    punt_mostreig: str = Field(..., min_length=1, max_length=255, description="Sampling point")
    temperatura: Optional[float] = Field(None, ge=-5, le=60, description="Temperature in Celsius")
    clor_lliure: Optional[float] = Field(None, ge=0, le=50, description="Free chlorine (mg Cl2/l)")
    clor_total: Optional[float] = Field(None, ge=0, le=50, description="Total chlorine (mg Cl2/l)")
    recompte_escherichia_coli: Optional[float] = Field(None, ge=0, description="E. coli count (NPM/100 ml)")
    recompte_enterococ: Optional[float] = Field(None, ge=0, description="Enterococcus count (NPM/100 ml)")
    recompte_microorganismes_aerobis_22c: Optional[float] = Field(None, ge=0, description="Aerobic microorganisms at 22°C (ufc/1 ml)")
    recompte_coliformes_totals: Optional[float] = Field(None, ge=0, description="Total coliforms (NMP/100 ml)")
    conductivitat_20c: Optional[float] = Field(None, ge=0, le=10000, description="Conductivity at 20°C (uS/cm)")
    ph: Optional[float] = Field(None, ge=0, le=14, description="pH units")
    terbolesa: Optional[float] = Field(None, ge=0, description="Turbidity (UNF)")
    color: Optional[float] = Field(None, ge=0, description="Color (mg/l Pt-Co)")
    olor: Optional[float] = Field(None, ge=0, description="Odor (dilution index at 25°C)")
    sabor: Optional[float] = Field(None, ge=0, description="Taste (dilution index at 25°C)")
    acid_monocloroacetic: Optional[float] = Field(None, ge=0, description="Monochloroacetic acid (ug/l)")
    acid_dicloroacetic: Optional[float] = Field(None, ge=0, description="Dichloroacetic acid (ug/l)")
    acid_tricloroacetic: Optional[float] = Field(None, ge=0, description="Trichloroacetic acid (ug/l)")
    acid_monobromoacetic: Optional[float] = Field(None, ge=0, description="Monobromoacetic acid (ug/l)")
    acid_dibromoacetic: Optional[float] = Field(None, ge=0, description="Dibromoacetic acid (ug/l)")
