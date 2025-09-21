import pytest
from unittest.mock import Mock, patch
from app.core.rag_engine import RAGEngine
from app.models.analysis import AnalysisResult, AnalysisStatus, CodeIssue, IssueCategory, IssueSeverity

class TestRAGEngine:
    
    @pytest.fixture
    def rag_engine(self):
        engine = RAGEngine()
        # Mock the sentence transformer to avoid downloading models in tests
        engine.model = Mock()
        engine.model.encode = Mock(return_value=Mock())
        engine.initialized = True
        return engine
    
    @pytest.mark.asyncio
    async def test_index_analysis_result(self, rag_engine):
        """Test indexing analysis results"""
        # Create mock analysis result
        issue = CodeIssue(
            id="test-issue",
            category=IssueCategory.SECURITY,
            severity=IssueSeverity.HIGH,
            title="Test security issue",
            description="Test description",
            file_path="test.py",
            suggestion="Fix this issue",
            impact_score=8.0,
            confidence=0.9
        )
        
        result = AnalysisResult(
            report_id="test-report",
            status=AnalysisStatus.COMPLETED,
            source_info={"path": "/test/repo", "type": "local"},
            issues=[issue],
            file_metrics=[],
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
        
        # Mock FAISS index
        rag_engine.index = Mock()
        rag_engine.index.add = Mock()
        
        await rag_engine.index_analysis_result(result)
        
        # Verify documents were added
        assert len(rag_engine.documents) > 0
        assert len(rag_engine.metadata) > 0
        
        # Verify FAISS index was called
        rag_engine.index.add.assert_called()
    
    @pytest.mark.asyncio
    async def test_search(self, rag_engine):
        """Test searching in RAG engine"""
        # Setup mock data
        rag_engine.documents = ["Test document about security issues"]
        rag_engine.metadata = [{"type": "issue", "category": "security"}]
        
        # Mock FAISS search
        rag_engine.index = Mock()
        rag_engine.index.search = Mock(return_value=([0.5], [0]))  # score, index
        
        results = await rag_engine.search("security vulnerability", k=1)
        
        assert len(results) == 1
        assert results[0]["document"] == "Test document about security issues"
        assert "similarity" in results[0]
    
    @pytest.mark.asyncio
    async def test_get_relevant_context(self, rag_engine):
        """Test getting relevant context"""
        # Setup mock search results
        rag_engine.search = Mock(return_value=[
            {"document": "Security issue in file.py", "similarity": 0.8},
            {"document": "Performance problem detected", "similarity": 0.7}
        ])
        
        context = await rag_engine.get_relevant_context("security problems")
        
        assert "Security issue in file.py" in context
        assert isinstance(context, str)