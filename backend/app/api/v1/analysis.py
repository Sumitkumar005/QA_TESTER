from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import os
import tempfile
import shutil
import logging

from app.models.analysis import AnalysisRequest, AnalysisResult, AnalysisStatus
from app.services.analysis_service import AnalysisService
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()
analysis_service = AnalysisService()
settings = get_settings()

@router.post("/analyze", response_model=dict)
async def analyze_repository(
    source_type: str = Form(...),
    source_path: str = Form(...),
    languages: Optional[str] = Form(None),
    include_tests: bool = Form(True),
    exclude_patterns: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Start code analysis"""
    try:
        # Parse languages if provided
        language_list = None
        if languages:
            language_list = [lang.strip() for lang in languages.split(",")]

        # Parse exclude patterns
        exclude_list = []
        if exclude_patterns:
            exclude_list = [pattern.strip() for pattern in exclude_patterns.split(",")]

        # Handle file upload
        if source_type == "upload" and file:
            # Save uploaded file
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file.filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            source_path = file_path

            # LOG WHAT TYPE OF FILE WE RECEIVED
            _, ext = os.path.splitext(file.filename.lower())
            logger.info(f"Received uploaded file: {file.filename} with extension: {ext}")

        # Validate source
        if source_type == "github" and not source_path.startswith("https://github.com/"):
            raise HTTPException(status_code=400, detail="Invalid GitHub URL")

        if source_type == "local" and not os.path.exists(source_path):
            raise HTTPException(status_code=400, detail="Local path does not exist")

        # Start analysis
        report_id = await analysis_service.start_analysis(
            source_type=source_type,
            source_path=source_path,
            languages=language_list,
            include_tests=include_tests,
            exclude_patterns=exclude_list
        )

        return {
            "report_id": report_id,
            "status": "started",
            "message": "Analysis started successfully"
        }

    except Exception as e:
        logger.error(f"Analysis request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/{report_id}/status", response_model=AnalysisResult)
async def get_analysis_status(report_id: str):
    """Get analysis status"""
    result = await analysis_service.get_analysis_status(report_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return result

@router.delete("/analyze/{report_id}")
async def cancel_analysis(report_id: str):
    """Cancel ongoing analysis"""
    success = await analysis_service.cancel_analysis(report_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found or already completed")
    
    return {"message": "Analysis cancelled successfully"}

@router.get("/analyze/supported-languages", response_model=List[str])
async def get_supported_languages():
    """Get supported programming languages"""
    return settings.SUPPORTED_LANGUAGES     