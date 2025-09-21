import logging
import os
from app.config.settings import get_settings
from app.core.rag_engine import rag_engine

logger = logging.getLogger(__name__)

async def init_vector_db():
    """Initialize vector database and ensure its storage directory exists."""
    try:
        # Get settings and ensure the directory for the index exists
        settings = get_settings()
        index_dir = settings.FAISS_INDEX_PATH
        os.makedirs(index_dir, exist_ok=True)
        
        # Now, initialize the engine
        await rag_engine.initialize()
        logger.info("Vector database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize vector database: {str(e)}")
        raise

async def close_vector_db():
    """Close vector database"""
    try:
        await rag_engine.save_index()
        logger.info("Vector database saved and closed")
    except Exception as e:
        logger.error(f"Error closing vector database: {str(e)}")

async def get_vector_engine():
    """Get vector engine instance"""
    return rag_engine