import asyncio
import logging

# Suppress quota exceeded error logs from Gemini API
class QuotaExceededFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if "quota exceeded" in msg.lower() or "generativelanguage.googleapis.com" in msg:
            return False
        return True

logger = logging.getLogger(__name__)
logger.addFilter(QuotaExceededFilter())
import uuid
import os
from typing import Dict, Optional
from datetime import datetime

from app.core.analyzer import CodeQualityAnalyzer
from app.core.rag_engine import rag_engine
from app.models.analysis import AnalysisResult, AnalysisStatus
from app.services.github_service import GitHubService
from app.database.mongodb import get_analysis_collection
from app.utils.file_utils import extract_archive, cleanup_temp_files

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for managing code analysis operations"""
    
    def __init__(self):
        self.analyzer = CodeQualityAnalyzer()
        self.github_service = GitHubService()
        self.active_analyses: Dict[str, asyncio.Task] = {}
    
    async def start_analysis(self, source_type: str, source_path: str, **kwargs) -> str:
        """Start a new code analysis"""
        report_id = str(uuid.uuid4())
        
        # Create initial analysis record
        result = AnalysisResult(
            report_id=report_id,
            status=AnalysisStatus.PENDING,
            source_info={
                "type": source_type,
                "path": source_path,
                **kwargs
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        collection = await get_analysis_collection()
        await collection.insert_one(result.model_dump())
        
        # Start analysis task
        task = asyncio.create_task(self._run_analysis(result))
        self.active_analyses[report_id] = task
        
        logger.info(f"Started analysis {report_id} for {source_type}:{source_path}")
        return report_id
    
    async def _run_analysis(self, result: AnalysisResult):
        """Run the actual analysis"""
        try:
            # Update status to in_progress
            result.status = AnalysisStatus.IN_PROGRESS
            result.updated_at = datetime.utcnow()
            await self._update_result(result)

            # Prepare source path
            analysis_path = result.source_info["path"]

            if result.source_info["type"] == "github":
                analysis_path = await self.github_service.clone_repository(
                    result.source_info["path"]
                )
            elif result.source_info["type"] == "upload":
                # CHECK IF IT'S A SINGLE FILE OR ARCHIVE
                uploaded_path = result.source_info["path"]

                # Get file extension to determine if it's an archive or code file
                _, ext = os.path.splitext(uploaded_path.lower())

                # Code file extensions
                code_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go',
                                 '.rs', '.cpp', '.cxx', '.cc', '.c', '.h', '.cs',
                                 '.rb', '.php', '.kt', '.scala', '.swift', '.m', '.r',
                                 '.sql', '.sh', '.bash']

                # Archive extensions
                archive_extensions = ['.zip', '.tar', '.tar.gz', '.tgz']

                if ext in code_extensions:
                    # It's a single code file - use it directly
                    analysis_path = uploaded_path
                    logger.info(f"Analyzing single uploaded file: {uploaded_path}")
                elif any(uploaded_path.lower().endswith(arch_ext) for arch_ext in archive_extensions):
                    # It's an archive - extract it
                    analysis_path = await extract_archive(uploaded_path)
                    logger.info(f"Extracted archive to: {analysis_path}")
                else:
                    # Unknown file type
                    raise ValueError(f"Unsupported file type: {ext}. Please upload a code file or archive.")

            # Run analysis
            analyzed_result = await self.analyzer.analyze_repository(
                analysis_path, result.report_id
            )

            # Update result with analysis data
            result.status = analyzed_result.status
            result.issues = analyzed_result.issues
            result.file_metrics = analyzed_result.file_metrics
            result.metrics = analyzed_result.metrics
            result.quality_score = getattr(analyzed_result, "quality_score", None)
            result.completed_at = analyzed_result.completed_at
            result.updated_at = datetime.utcnow()

            # Index in RAG engine
            await rag_engine.index_analysis_result(result)

            # Save final result
            await self._update_result(result)

            # Cleanup temporary files (only for archives and GitHub repos)
            if result.source_info["type"] == "github" or (
                result.source_info["type"] == "upload" and
                analysis_path != result.source_info["path"]  # Only if we extracted an archive
            ):
                await cleanup_temp_files(analysis_path)

            logger.info(f"Completed analysis {result.report_id}")

        except Exception as e:
            logger.error(f"Analysis {result.report_id} failed: {str(e)}")
            result.status = AnalysisStatus.FAILED
            result.error_message = str(e)
            result.updated_at = datetime.utcnow()
            await self._update_result(result)
        finally:
            # Remove from active analyses
            if result.report_id in self.active_analyses:
                del self.active_analyses[result.report_id]
    
    async def get_analysis_status(self, report_id: str) -> Optional[AnalysisResult]:
        """Get analysis status"""
        collection = await get_analysis_collection()
        doc = await collection.find_one({"report_id": report_id})
        
        if doc:
            return AnalysisResult(**doc)
        return None
    
    async def cancel_analysis(self, report_id: str) -> bool:
        """Cancel an ongoing analysis"""
        if report_id in self.active_analyses:
            task = self.active_analyses[report_id]
            task.cancel()
            
            # Update status in database
            collection = await get_analysis_collection()
            await collection.update_one(
                {"report_id": report_id},
                {
                    "$set": {
                        "status": AnalysisStatus.CANCELLED.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Cancelled analysis {report_id}")
            return True
        
        return False
    
    async def _update_result(self, result: AnalysisResult):
        """Update analysis result in database"""
        collection = await get_analysis_collection()
        await collection.replace_one(
            {"report_id": result.report_id},
            result.model_dump(),
            upsert=True
        )