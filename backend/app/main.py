"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import routes

# Create FastAPI app
app = FastAPI(
    title="Enterprise Document Intelligence API",
    description="RAG-based document intelligence system with Decision Mode",
    version="1.0.0"
)

# CORS middleware (for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api", tags=["API"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Enterprise Document Intelligence API",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "vector_db": settings.VECTOR_DB_TYPE
    }
