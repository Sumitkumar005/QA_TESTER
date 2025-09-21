# backend/app/database/mongodb.py
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global database connection
_client: AsyncIOMotorClient = None
_database: AsyncIOMotorDatabase = None

async def init_db():
    """Initialize database connection"""
    global _client, _database
    try:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
        _database = _client[settings.DATABASE_NAME]
        
        # Test connection
        await _client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes
        await _create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

async def close_db():
    """Close database connection"""
    global _client
    if _client:
        _client.close()
        logger.info("Closed MongoDB connection")

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if _database is None:
        raise RuntimeError("Database not initialized")
    return _database

async def get_analysis_collection() -> AsyncIOMotorCollection:
    """Get analysis results collection"""
    db = await get_database()
    return db.analysis_results

async def get_reports_collection() -> AsyncIOMotorCollection:
    """Get reports collection"""
    db = await get_database()
    return db.reports

async def get_qa_collection() -> AsyncIOMotorCollection:
    """Get Q&A collection"""
    db = await get_database()
    return db.qa_sessions

async def _create_indexes():
    """Create database indexes"""
    try:
        # Analysis results indexes
        analysis_collection = await get_analysis_collection()
        await analysis_collection.create_index("report_id", unique=True)
        await analysis_collection.create_index("created_at")
        await analysis_collection.create_index("status")
        await analysis_collection.create_index([("source_info.path", 1), ("created_at", -1)])
        
        # Reports indexes
        reports_collection = await get_reports_collection()
        await reports_collection.create_index("report_id", unique=True)
        await reports_collection.create_index("created_at")
        
        # Q&A indexes
        qa_collection = await get_qa_collection()
        await qa_collection.create_index("session_id")
        await qa_collection.create_index("report_id")
        await qa_collection.create_index("created_at")
        
        logger.info("Created database indexes successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}")
