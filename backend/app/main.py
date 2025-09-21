# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config.settings import get_settings
from app.database.mongodb import init_db, close_db
from app.database.vector_db import init_vector_db, close_vector_db
from app.api.v1 import analysis, reports, qa, pr_review

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Code Quality Intelligence Agent")
    await init_db()
    await init_vector_db()
    yield
    # Shutdown
    logger.info("Shutting down Code Quality Intelligence Agent")
    await close_db()
    await close_vector_db()

app = FastAPI(
    title="Code Quality Intelligence Agent",
    description="AI-powered code analysis and quality assessment",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Code Quality Intelligence Agent",
        "version": "1.0.0"
    }

# Include API routers
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(qa.router, prefix="/api/v1", tags=["qa"])
app.include_router(pr_review.router, prefix="/api/v1", tags=["pr-review"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )