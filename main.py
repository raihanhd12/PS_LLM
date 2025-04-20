from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import subprocess
import sys

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize the FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    try:
        # Run database migrations
        logging.info("Running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"], capture_output=True, text=True, check=True
        )
        logging.info(f"Migration result: {result.stdout}")

        # Initialize database
        init_db()
        logging.info("Database initialized")
    except subprocess.CalledProcessError as e:
        logging.error(f"Migration error: {e.stderr}")
        logging.error("Failed to run migrations, but continuing startup")
    except Exception as e:
        logging.error(f"Startup error: {str(e)}")
        logging.error("Failed to initialize properly, but continuing startup")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Document AI Assistant API",
        "version": "1.0.0",
        "docs": f"/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "services": {
            "api": "running",
            "db": "connected",  # This would ideally check DB connection
            "embedding": "available",  # This would ideally check embedding service
        },
    }
