from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from .analysis import CodeIssue, RepositoryMetrics, IssueSeverity, IssueCategory

class IssueSummary(BaseModel):
    category: IssueCategory
    severity: IssueSeverity
    count: int
    percentage: float

class QualityScore(BaseModel):
    overall_score: float = Field(ge=0.0, le=100.0)
    security_score: float = Field(ge=0.0, le=100.0)
    maintainability_score: float = Field(ge=0.0, le=100.0)
    performance_score: float = Field(ge=0.0, le=100.0)
    test_coverage_score: float = Field(ge=0.0, le=100.0)

class ReportSummary(BaseModel):
    report_id: str
    total_issues: int
    critical_issues: int
    high_priority_issues: int
    quality_score: QualityScore
    top_issues: List[CodeIssue]
    issue_summary: List[IssueSummary]
    recommendations: List[str]

class DetailedReport(BaseModel):
    summary: ReportSummary
    metrics: RepositoryMetrics
    all_issues: List[CodeIssue]
    trends: Optional[Dict[str, Any]] = None