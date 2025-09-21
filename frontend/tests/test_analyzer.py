import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.core.analyzer import CodeQualityAnalyzer
from app.models.analysis import AnalysisStatus, IssueCategory, IssueSeverity

class TestCodeQualityAnalyzer:
    
    @pytest.fixture
    def analyzer(self):
        return CodeQualityAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_repository_success(self, analyzer, temp_dir, sample_python_code):
        """Test successful repository analysis"""
        # Create test files
        test_file = temp_dir / "test.py"
        test_file.write_text(sample_python_code)
        
        # Mock external dependencies
        with patch.object(analyzer, 'model', Mock()):
            result = await analyzer.analyze_repository(str(temp_dir), "test-report-id")
        
        assert result.report_id == "test-report-id"
        assert result.status == AnalysisStatus.COMPLETED
        assert len(result.issues) > 0
        assert len(result.file_metrics) > 0
        assert result.metrics is not None
    
    @pytest.mark.asyncio
    async def test_analyze_security_issues(self, analyzer, sample_python_code):
        """Test security issue detection"""
        issues = await analyzer._analyze_security(sample_python_code, "test.py", "python")
        
        # Should detect eval() usage
        eval_issues = [issue for issue in issues if "eval" in issue.title.lower()]
        assert len(eval_issues) > 0
        assert eval_issues[0].category == IssueCategory.SECURITY
        assert eval_issues[0].severity == IssueSeverity.HIGH
    
    @pytest.mark.asyncio
    async def test_analyze_performance_issues(self, analyzer, sample_python_code):
        """Test performance issue detection"""
        issues = await analyzer._analyze_performance(sample_python_code, "test.py", "python")
        
        # Should detect range(len()) pattern
        range_issues = [issue for issue in issues if "enumerate" in issue.description]
        assert len(range_issues) > 0
        assert range_issues[0].category == IssueCategory.PERFORMANCE
    
    @pytest.mark.asyncio
    async def test_analyze_code_quality_issues(self, analyzer, sample_python_code):
        """Test code quality issue detection"""
        issues = await analyzer._analyze_code_quality(sample_python_code, "test.py", "python")
        
        # Should detect TODO comments
        todo_issues = [issue for issue in issues if "TODO" in issue.description]
        assert len(todo_issues) > 0
    
    @pytest.mark.asyncio
    async def test_complexity_calculation(self, analyzer):
        """Test complexity calculation"""
        complex_code = '''
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                while i > 0:
                    if i % 3 == 0:
                        return i
                    i -= 1
            else:
                continue
    else:
        return 0
'''
        complexity = await analyzer._calculate_complexity(complex_code, "python")
        assert complexity > 5  # Should detect high complexity
    
    @pytest.mark.asyncio
    async def test_empty_repository(self, analyzer, temp_dir):
        """Test analysis of empty repository"""
        result = await analyzer.analyze_repository(str(temp_dir), "empty-repo")
        
        assert result.status == AnalysisStatus.COMPLETED
        assert len(result.issues) == 0
        assert len(result.file_metrics) == 0
        assert result.metrics.total_files == 0