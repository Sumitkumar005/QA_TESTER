from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class IssueCategory(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    CODE_QUALITY = "code_quality"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"

class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AnalysisRequest(BaseModel):
    source_type: str = Field(..., description="Type of source: 'local', 'github'")
    source_path: str = Field(..., description="Path to local directory or GitHub URL")
    languages: Optional[List[str]] = Field(default=None, description="Languages to analyze")
    include_tests: bool = Field(default=True, description="Include test files in analysis")
    exclude_patterns: List[str] = Field(default_factory=list, description="Patterns to exclude")

class CodeIssue(BaseModel):
    id: str = Field(..., description="Unique issue ID")
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: str
    impact_score: float = Field(ge=0.0, le=10.0)
    confidence: float = Field(ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)

class FileMetrics(BaseModel):
    file_path: str
    language: str
    lines_of_code: int
    complexity: float
    maintainability_index: float
    test_coverage: Optional[float] = None
    issues_count: int

class RepositoryMetrics(BaseModel):
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    complexity_average: float
    maintainability_average: float
    test_coverage_average: Optional[float] = None
    technical_debt_hours: float

class AnalysisResult(BaseModel):
    report_id: str
    status: AnalysisStatus
    source_info: Dict[str, Any]
    metrics: Optional[RepositoryMetrics] = None
    issues: List[CodeIssue] = Field(default_factory=list)
    file_metrics: List[FileMetrics] = Field(default_factory=list)
    quality_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    

