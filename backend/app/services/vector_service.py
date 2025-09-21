import logging
from typing import List, Dict, Any, Optional
from app.core.rag_engine import rag_engine

logger = logging.getLogger(__name__)

class VectorService:
    """Service for vector database operations"""
    
    def __init__(self):
        self.rag_engine = rag_engine
    
    async def initialize(self):
        """Initialize vector service"""
        await self.rag_engine.initialize()
    
    async def search_similar(
        self,
        query: str,
        report_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar content"""
        return await self.rag_engine.search(query, k=limit, report_id=report_id)
    
    async def get_context(
        self,
        query: str,
        report_id: Optional[str] = None
    ) -> str:
        """Get relevant context for a query"""
        return await self.rag_engine.get_relevant_context(query, report_id)
    
    async def cleanup_old_data(self, max_reports: int = 1000):
        """Clean up old vector data"""
        await self.rag_engine.cleanup_old_data(max_reports)