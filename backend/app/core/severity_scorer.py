import logging
from typing import Dict, Any
from app.models.analysis import CodeIssue, IssueCategory, IssueSeverity

logger = logging.getLogger(__name__)

class SeverityScorer:
    """Automated severity scoring for code issues"""
    
    def __init__(self):
        # Base scores for different categories
        self.category_weights = {
            IssueCategory.SECURITY: 10.0,
            IssueCategory.PERFORMANCE: 7.0,
            IssueCategory.CODE_QUALITY: 5.0,
            IssueCategory.MAINTAINABILITY: 6.0,
            IssueCategory.TESTING: 8.0,
            IssueCategory.DOCUMENTATION: 3.0,
            IssueCategory.COMPLEXITY: 7.0,
            IssueCategory.DUPLICATION: 4.0,
        }
        
        # Severity multipliers
        self.severity_multipliers = {
            IssueSeverity.CRITICAL: 1.0,
            IssueSeverity.HIGH: 0.8,
            IssueSeverity.MEDIUM: 0.6,
            IssueSeverity.LOW: 0.4,
            IssueSeverity.INFO: 0.2,
        }
        
        # Keywords that increase severity
        self.high_impact_keywords = [
            'injection', 'vulnerability', 'security', 'exploit',
            'deadlock', 'memory leak', 'crash', 'exception',
            'performance', 'bottleneck', 'slow', 'timeout'
        ]
    
    async def calculate_impact_score(self, issue: CodeIssue) -> float:
        """Calculate impact score for an issue"""
        try:
            # Base score from category
            base_score = self.category_weights.get(issue.category, 5.0)
            
            # Apply severity multiplier
            severity_multiplier = self.severity_multipliers.get(issue.severity, 0.6)
            
            # Confidence factor
            confidence_factor = issue.confidence if issue.confidence > 0 else 0.5
            
            # Check for high-impact keywords
            keyword_bonus = 0.0
            issue_text = (issue.title + " " + issue.description).lower()
            for keyword in self.high_impact_keywords:
                if keyword in issue_text:
                    keyword_bonus += 1.0
            
            # Line number factor (earlier in file = higher impact)
            line_factor = 1.0
            if issue.line_number and issue.line_number > 0:
                # Issues in first 100 lines get higher priority
                if issue.line_number <= 100:
                    line_factor = 1.2
                elif issue.line_number <= 500:
                    line_factor = 1.0
                else:
                    line_factor = 0.9
            
            # Calculate final score
            impact_score = (
                (base_score * severity_multiplier * confidence_factor) +
                keyword_bonus
            ) * line_factor
            
            # Normalize to 0-10 scale
            impact_score = min(max(impact_score, 0.0), 10.0)
            
            return round(impact_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating impact score: {str(e)}")
            return 5.0  # Default score
    
    def prioritize_issues(self, issues: list[CodeIssue]) -> list[CodeIssue]:
        """Sort issues by priority"""
        def priority_key(issue):
            severity_order = {
                IssueSeverity.CRITICAL: 5,
                IssueSeverity.HIGH: 4,
                IssueSeverity.MEDIUM: 3,
                IssueSeverity.LOW: 2,
                IssueSeverity.INFO: 1
            }
            return (
                severity_order.get(issue.severity, 0),
                issue.impact_score,
                -len(issue.tags)  # More tags = higher specificity
            )
        
        return sorted(issues, key=priority_key, reverse=True)