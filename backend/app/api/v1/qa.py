from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

# CORRECTED IMPORT: Changed 'services' to 'app.services'
from app.services.qa_service import QAService

router = APIRouter()
qa_service = QAService()

class QuestionRequest(BaseModel):
    question: str
    report_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]
    report_id: Optional[str]
    confidence: float

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about code analysis"""
    try:
        result = await qa_service.ask_question(
            question=request.question,
            report_id=request.report_id,
            context=request.context
        )
        
        return QuestionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
