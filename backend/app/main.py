"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from app.core.config import settings
from app.api import routes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Enterprise Document Intelligence API",
    description="RAG-based document intelligence system with Decision Mode",
    version="1.0.0"
)

# CORS middleware (for frontend connection) - simple localhost setup
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple request logging (optional)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.url.path.startswith("/api"):
        logger.info(f"API: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

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


@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify connectivity."""
    return {
        "message": "Backend is accessible",
        "status": "ok"
    }
