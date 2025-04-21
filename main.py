import logging
import subprocess
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import router
from app.core.config import API_HOST, API_PORT, DB_URL
from app.db.session import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events manager for application startup and shutdown"""
    # Startup logic
    try:
        if not DB_URL:
            logging.error(
                "Database URL is not configured. Set POSTGRES_URL in the .env file."
            )
        else:
            # Run database migrations
            logging.info("Running database migration...")
            try:
                result = subprocess.run(
                    ["alembic", "upgrade", "head"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                logging.info(f"Migration result: {result.stdout}")

                # Initialize database
                init_db()
                logging.info("Database initialized successfully")
            except subprocess.CalledProcessError as e:
                logging.error(f"Migration error: {e.stderr}")
                logging.error(
                    f"Migration command output: {e.stdout if hasattr(e, 'stdout') else 'No output'}"
                )
                logging.error(f"Return code: {e.returncode}")
                logging.error("Failed to execute migration, but startup continued")
    except Exception as e:
        logging.error(f"Error startup: {str(e)}")
        logging.error("Failed to initialize correctly, but startup continued")

    yield  # Server berjalan disini

    # Shutdown logic bisa ditambahkan di sini
    logging.info("Application shutdown")


# Initialize the FastAPI app with lifespan manager
app = FastAPI(
    title="Document AI Assistant API",
    description="API for document search and AI-powered question answering",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome in Document AI Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host=API_HOST, port=API_PORT)
