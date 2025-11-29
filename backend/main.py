from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import parameters_router, samples_router
from routers.admin_router import router as admin_router

app = FastAPI(
    title="Aigualba API", 
    description="API for water quality management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(parameters_router)
app.include_router(samples_router)
app.include_router(admin_router)


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Aigualba API is running"}
