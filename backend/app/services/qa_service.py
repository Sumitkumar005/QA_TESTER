import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from app.config.settings import get_settings
from app.core.rag_engine import rag_engine
from app.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)
settings = get_settings()

class QAService:
    """Service for handling Q&A about code analysis"""
    
    def __init__(self):
        self.analysis_service = AnalysisService()
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            logger.warning("Gemini API key not configured")
            self.model = None
    
    async def ask_question(
        self,
        question: str,
        report_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Answer a question about code analysis"""
        try:
            # Get relevant context from RAG engine
            rag_context = await rag_engine.get_relevant_context(question, report_id)
            
            # Get analysis data if report_id provided
            analysis_context = ""
            if report_id:
                analysis_result = await self.analysis_service.get_analysis_status(report_id)
                if analysis_result:
                    analysis_context = self._format_analysis_context(analysis_result)
            
            # Generate response using AI
            if self.model:
                response = await self._generate_ai_response(
                    question, rag_context, analysis_context, context
                )
            else:
                response = self._generate_fallback_response(
                    question, rag_context, analysis_context
                )
            
            return {
                "answer": response,
                "sources": self._extract_sources(rag_context),
                "report_id": report_id,
                "confidence": 0.8 if self.model else 0.6
            }
            
        except Exception as e:
            logger.error(f"QA failed for question '{question}': {str(e)}")
            return {
                "answer": "I'm sorry, I encountered an error while processing your question. Please try again.",
                "sources": [],
                "report_id": report_id,
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _generate_ai_response(
        self,
        question: str,
        rag_context: str,
        analysis_context: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate AI response using Gemini"""
        try:
            prompt = self._build_prompt(question, rag_context, analysis_context, user_context)
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"AI response generation failed: {str(e)}")
            return self._generate_fallback_response(question, rag_context, analysis_context)
    
    def _build_prompt(
        self,
        question: str,
        rag_context: str,
        analysis_context: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for AI model"""
        prompt = f"""
You are a helpful code quality assistant. Answer the user's question based on the provided context.

Question: {question}

Context from code analysis:
{analysis_context}

Relevant information:
{rag_context}
"""
        
        if user_context:
            prompt += f"\nAdditional context: {user_context}"
        
        prompt += """

Please provide a helpful, accurate answer. If you're not sure about something, say so. 
Focus on practical advice and actionable recommendations.
Keep your response conversational and developer-friendly.
"""
        
        return prompt
    
    def _generate_fallback_response(
        self,
        question: str,
        rag_context: str,
        analysis_context: str
    ) -> str:
        """Generate fallback response without AI"""
        if not rag_context and not analysis_context:
            return "I don't have enough information to answer that question. Please run an analysis first or provide more context."
        
        # Simple keyword-based responses
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["security", "vulnerable", "exploit"]):
            return "Based on the analysis, I found security-related issues. Please review the security vulnerabilities in the report and address them with proper input validation and sanitization."
        
        elif any(word in question_lower for word in ["performance", "slow", "optimize"]):
            return "The analysis identified performance-related issues. Consider optimizing loops, caching expensive operations, and reviewing algorithmic complexity."
        
        elif any(word in question_lower for word in ["test", "coverage", "testing"]):
            return "Testing is important for code quality. Consider adding unit tests, integration tests, and improving test coverage for better reliability."
        
        elif any(word in question_lower for word in ["complexity", "complex", "complicated"]):
            return "High complexity can make code hard to maintain. Consider breaking down complex functions, reducing nesting, and following single responsibility principle."
        
        else:
            return f"Based on the available information: {rag_context[:500]}..." if rag_context else "I need more specific information to answer that question."
    
    def _format_analysis_context(self, result) -> str:
        """Format analysis result for context"""
        context_parts = []
        
        if result.metrics:
            context_parts.append(f"Repository has {result.metrics.total_files} files with {result.metrics.total_lines} lines of code.")
            context_parts.append(f"Languages: {', '.join(result.metrics.languages.keys())}")
            context_parts.append(f"Average complexity: {result.metrics.complexity_average:.2f}")
        
        if result.issues:
            context_parts.append(f"Found {len(result.issues)} issues total.")
            
            # Group by severity
            severity_counts = {}
            for issue in result.issues:
                severity_counts[issue.severity.value] = severity_counts.get(issue.severity.value, 0) + 1
            
            severity_info = ", ".join([f"{count} {severity}" for severity, count in severity_counts.items()])
            context_parts.append(f"Issue breakdown: {severity_info}")
        
        return " ".join(context_parts)
    
    def _extract_sources(self, rag_context: str) -> List[str]:
        """Extract source information from RAG context"""
        # This is a simplified implementation
        # In a real system, you'd track sources more systematically
        sources = []
        if "Repository analysis:" in rag_context:
            sources.append("Repository metrics")
        if "Issue:" in rag_context:
            sources.append("Code issues")
        if "File analysis:" in rag_context:
            sources.append("File metrics")
        
        return sources