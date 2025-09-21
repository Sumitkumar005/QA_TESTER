import pytest
from app.core.ast_parser import ASTAnalyzer
from app.models.analysis import IssueCategory

class TestASTAnalyzer:
    
    @pytest.fixture
    def ast_analyzer(self):
        return ASTAnalyzer()
    
    @pytest.mark.asyncio
    async def test_python_ast_analysis(self, ast_analyzer, sample_python_code):
        """Test Python AST analysis"""
        issues = await ast_analyzer.analyze(sample_python_code, "test.py", "python")
        
        # Should detect various issues
        assert len(issues) > 0
        
        # Check for function parameter issue
        param_issues = [issue for issue in issues if "parameters" in issue.title.lower()]
        assert len(param_issues) > 0
        
        # Check for missing docstring issues
        docstring_issues = [issue for issue in issues if "docstring" in issue.title.lower()]
        assert len(docstring_issues) > 0
    
    @pytest.mark.asyncio
    async def test_javascript_pattern_analysis(self, ast_analyzer, sample_javascript_code):
        """Test JavaScript pattern analysis"""
        issues = await ast_analyzer.analyze(sample_javascript_code, "test.js", "javascript")
        
        # Should detect == usage
        equality_issues = [issue for issue in issues if "===" in issue.description]
        assert len(equality_issues) > 0
        
        # Should detect var usage
        var_issues = [issue for issue in issues if "let or const" in issue.description]
        assert len(var_issues) > 0
    
    @pytest.mark.asyncio
    async def test_syntax_error_handling(self, ast_analyzer):
        """Test handling of syntax errors"""
        invalid_code = "def invalid_function(\n    pass"  # Missing closing parenthesis
        
        issues = await ast_analyzer.analyze(invalid_code, "invalid.py", "python")
        
        # Should detect syntax error
        syntax_issues = [issue for issue in issues if "syntax" in issue.title.lower()]
        assert len(syntax_issues) > 0