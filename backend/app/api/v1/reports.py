from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.report import DetailedReport, ReportSummary, QualityScore, IssueSummary
from app.models.analysis import IssueCategory, IssueSeverity
from app.services.analysis_service import AnalysisService
from app.database.mongodb import get_reports_collection

router = APIRouter()
analysis_service = AnalysisService()

@router.get("/report/{report_id}", response_model=DetailedReport)
async def get_report(report_id: str, detailed: bool = True):
    """Get analysis report"""
    # Get analysis result
    result = await analysis_service.get_analysis_status(report_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if result.status.value != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    # Generate report
    try:
        # Calculate quality scores
        quality_score = _calculate_quality_score(result)
        
        # Generate issue summary
        issue_summary = _generate_issue_summary(result.issues)
        
        # Get top issues
        top_issues = result.issues[:10]  # Top 10 issues
        
        # Generate recommendations
        recommendations = _generate_recommendations(result)
        
        # Create summary
        summary = ReportSummary(
            report_id=report_id,
            total_issues=len(result.issues),
            critical_issues=len([i for i in result.issues if i.severity == IssueSeverity.CRITICAL]),
            high_priority_issues=len([i for i in result.issues if i.severity == IssueSeverity.HIGH]),
            quality_score=quality_score,
            top_issues=top_issues,
            issue_summary=issue_summary,
            recommendations=recommendations
        )
        
        # Return detailed report
        return DetailedReport(
            summary=summary,
            metrics=result.metrics,
            all_issues=result.issues if detailed else [],
            trends=None  # TODO: Implement trends
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

def _calculate_quality_score(result) -> QualityScore:
    """Calculate quality scores"""
    total_issues = len(result.issues)
    
    if total_issues == 0:
        return QualityScore(
            overall_score=100.0,
            security_score=100.0,
            maintainability_score=100.0,
            performance_score=100.0,
            test_coverage_score=100.0
        )
    
    # Count issues by category
    security_issues = len([i for i in result.issues if i.category == IssueCategory.SECURITY])
    performance_issues = len([i for i in result.issues if i.category == IssueCategory.PERFORMANCE])
    maintainability_issues = len([i for i in result.issues if i.category in [IssueCategory.MAINTAINABILITY, IssueCategory.CODE_QUALITY]])
    testing_issues = len([i for i in result.issues if i.category == IssueCategory.TESTING])
    
    # Calculate scores (simple algorithm)
    security_score = max(0, 100 - (security_issues * 15))
    performance_score = max(0, 100 - (performance_issues * 10))
    maintainability_score = max(0, 100 - (maintainability_issues * 5))
    test_coverage_score = max(0, 100 - (testing_issues * 10))
    
    overall_score = (security_score + performance_score + maintainability_score + test_coverage_score) / 4
    
    return QualityScore(
        overall_score=overall_score,
        security_score=security_score,
        maintainability_score=maintainability_score,
        performance_score=performance_score,
        test_coverage_score=test_coverage_score
    )

def _generate_issue_summary(issues) -> list[IssueSummary]:
    """Generate issue summary by category and severity"""
    summary_data = {}
    total_issues = len(issues)
    
    if total_issues == 0:
        return []
    
    for issue in issues:
        key = (issue.category, issue.severity)
        summary_data[key] = summary_data.get(key, 0) + 1
    
    summaries = []
    for (category, severity), count in summary_data.items():
        percentage = (count / total_issues) * 100
        summaries.append(IssueSummary(
            category=category,
            severity=severity,
            count=count,
            percentage=percentage
        ))
    
    # Sort by severity and count
    severity_order = {IssueSeverity.CRITICAL: 5, IssueSeverity.HIGH: 4, IssueSeverity.MEDIUM: 3, IssueSeverity.LOW: 2, IssueSeverity.INFO: 1}
    summaries.sort(key=lambda x: (severity_order.get(x.severity, 0), x.count), reverse=True)
    
    return summaries

def _generate_recommendations(result) -> list[str]:
    """Generate recommendations based on analysis results"""
    recommendations = []
    
    if not result.issues:
        recommendations.append("Great job! No major issues found in your codebase.")
        return recommendations
    
    # Security recommendations
    security_issues = [i for i in result.issues if i.category == IssueCategory.SECURITY]
    if security_issues:
        recommendations.append(f"Address {len(security_issues)} security issues to improve application security.")
    
    # Performance recommendations
    performance_issues = [i for i in result.issues if i.category == IssueCategory.PERFORMANCE]
    if performance_issues:
        recommendations.append(f"Optimize {len(performance_issues)} performance bottlenecks for better user experience.")
    
    # Maintainability recommendations
    maintainability_issues = [i for i in result.issues if i.category == IssueCategory.MAINTAINABILITY]
    if maintainability_issues:
        recommendations.append(f"Improve {len(maintainability_issues)} maintainability issues to reduce technical debt.")
    
    # Testing recommendations
    testing_issues = [i for i in result.issues if i.category == IssueCategory.TESTING]
    if testing_issues:
        recommendations.append(f"Add tests to cover {len(testing_issues)} areas lacking proper test coverage.")
    
    # Documentation recommendations
    doc_issues = [i for i in result.issues if i.category == IssueCategory.DOCUMENTATION]
    if doc_issues:
        recommendations.append(f"Improve documentation for {len(doc_issues)} components to enhance code understanding.")
    
    # Complexity recommendations
    if result.metrics and result.metrics.complexity_average > 10:
        recommendations.append("Consider refactoring complex functions to improve code readability and maintainability.")
    
    return recommendations
