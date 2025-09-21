import pytest
from app.core.severity_scorer import SeverityScorer
from app.models.analysis import CodeIssue, IssueCategory, IssueSeverity

class TestSeverityScorer:
    
    @pytest.fixture
    def scorer(self):
        return SeverityScorer()
    
    @pytest.mark.asyncio
    async def test_impact_score_calculation(self, scorer):
        """Test impact score calculation"""
        # High severity security issue
        security_issue = CodeIssue(
            id="test-1",
            category=IssueCategory.SECURITY,
            severity=IssueSeverity.HIGH,
            title="SQL injection vulnerability",
            description="Potential SQL injection in database query",
            file_path="app.py",
            line_number=10,
            suggestion="Use parameterized queries",
            impact_score=0.0,
            confidence=0.9
        )
        
        score = await scorer.calculate_impact_score(security_issue)
        assert score >= 7.0  # Should be high impact
        
        # Low severity documentation issue
        doc_issue = CodeIssue(
            id="test-2",
            category=IssueCategory.DOCUMENTATION,
            severity=IssueSeverity.LOW,
            title="Missing docstring",
            description="Function lacks documentation",
            file_path="utils.py",
            line_number=100,
            suggestion="Add docstring",
            impact_score=0.0,
            confidence=1.0
        )
        
        doc_score = await scorer.calculate_impact_score(doc_issue)
        assert doc_score <= 3.0  # Should be low impact
        assert score > doc_score  # Security should be higher than documentation
    
    def test_issue_prioritization(self, scorer):
        """Test issue prioritization"""
        issues = [
            CodeIssue(
                id="low",
                category=IssueCategory.CODE_QUALITY,
                severity=IssueSeverity.LOW,
                title="Low issue",
                description="Low priority issue",
                file_path="test.py",
                suggestion="Fix it",
                impact_score=2.0,
                confidence=0.8
            ),
            CodeIssue(
                id="critical",
                category=IssueCategory.SECURITY,
                severity=IssueSeverity.CRITICAL,
                title="Critical issue",
                description="Critical security vulnerability",
                file_path="test.py",
                suggestion="Fix immediately",
                impact_score=9.5,
                confidence=1.0
            ),
            CodeIssue(
                id="high",
                category=IssueCategory.PERFORMANCE,
                severity=IssueSeverity.HIGH,
                title="Performance issue",
                description="Performance bottleneck",
                file_path="test.py",
                suggestion="Optimize",
                impact_score=7.0,
                confidence=0.9
            )
        ]
        
        prioritized = scorer.prioritize_issues(issues)
        
        # Should be ordered by severity and impact
        assert prioritized[0].id == "critical"
        assert prioritized[1].id == "high"
        assert prioritized[2].id == "low"
