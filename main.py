import logging
import subprocess

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import router
from app.core.config import API_HOST, API_PORT
from app.db.session import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize the FastAPI app
app = FastAPI(
    title="Document AI Assistant API",
    description="API for document search and AI-powered question answering",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router directly from endpoints
app.include_router(router, prefix="/api/v1")


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
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
    )
