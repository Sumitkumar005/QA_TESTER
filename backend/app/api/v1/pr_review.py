from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import logging
import re
import uuid
import ast
import json
from pathlib import Path
import tempfile
import os

router = APIRouter()
logger = logging.getLogger(__name__)

class CodeQualityMetrics(BaseModel):
    complexity: int
    maintainability_score: float
    code_smells: List[str]
    security_issues: List[str]
    performance_issues: List[str]
    best_practices_violations: List[str]

class FileAnalysis(BaseModel):
    filename: str
    language: str
    lines_added: int
    lines_deleted: int
    complexity_score: int
    maintainability_score: float
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    functions_changed: List[str]
    classes_changed: List[str]

class PRReviewRequest(BaseModel):
    pr_url: str
    github_token: Optional[str] = None

class EnhancedPRReviewResponse(BaseModel):
    review_id: str
    status: str
    message: str
    files_reviewed: int
    lines_added: int
    lines_deleted: int
    overall_quality_score: float
    risk_assessment: str
    file_analyses: List[FileAnalysis]
    summary_metrics: CodeQualityMetrics
    recommendations: List[str]
    changeset_impact: Dict[str, Any]

class CodeAnalyzer:
    """Advanced code analyzer for PR reviews"""
    
    @staticmethod
    def analyze_python_file(content: str, filename: str) -> Dict[str, Any]:
        """Analyze Python file for quality metrics"""
        try:
            tree = ast.parse(content)
            
            # Extract functions and classes
            functions = []
            classes = []
            complexity = 0
            issues = []
            suggestions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    # Calculate cyclomatic complexity approximation
                    func_complexity = CodeAnalyzer._calculate_complexity(node)
                    complexity += func_complexity
                    
                    if func_complexity > 10:
                        issues.append({
                            "type": "complexity",
                            "severity": "high",
                            "line": node.lineno,
                            "message": f"Function '{node.name}' has high complexity ({func_complexity})"
                        })
                        suggestions.append(f"Consider refactoring function '{node.name}' to reduce complexity")
                
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    
                    # Check for large classes
                    class_methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(class_methods) > 15:
                        issues.append({
                            "type": "maintainability",
                            "severity": "medium",
                            "line": node.lineno,
                            "message": f"Class '{node.name}' has many methods ({len(class_methods)})"
                        })
            
            # Check for code smells
            code_smells = CodeAnalyzer._detect_python_code_smells(content, tree)
            issues.extend(code_smells)
            
            # Security checks
            security_issues = CodeAnalyzer._detect_python_security_issues(content, tree)
            issues.extend(security_issues)
            
            # Calculate maintainability score
            maintainability_score = max(0, 100 - (complexity * 2) - (len(issues) * 5))
            
            return {
                "functions": functions,
                "classes": classes,
                "complexity": complexity,
                "maintainability_score": maintainability_score,
                "issues": issues,
                "suggestions": suggestions
            }
            
        except SyntaxError as e:
            return {
                "functions": [],
                "classes": [],
                "complexity": 0,
                "maintainability_score": 0,
                "issues": [{
                    "type": "syntax",
                    "severity": "critical",
                    "line": e.lineno or 0,
                    "message": f"Syntax error: {str(e)}"
                }],
                "suggestions": ["Fix syntax errors before proceeding"]
            }
        except Exception as e:
            logger.error(f"Error analyzing Python file {filename}: {str(e)}")
            return {
                "functions": [],
                "classes": [],
                "complexity": 0,
                "maintainability_score": 50,
                "issues": [],
                "suggestions": []
            }
    
    @staticmethod
    def analyze_javascript_file(content: str, filename: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file for quality metrics"""
        issues = []
        suggestions = []
        functions = []
        classes = []
        
        lines = content.split('\n')
        complexity = 0
        
        # Simple pattern-based analysis for JavaScript
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Function declarations
            if re.search(r'function\s+(\w+)', line):
                match = re.search(r'function\s+(\w+)', line)
                if match:
                    functions.append(match.group(1))
            
            # Arrow functions
            if re.search(r'const\s+(\w+)\s*=\s*\(.*\)\s*=>', line):
                match = re.search(r'const\s+(\w+)\s*=', line)
                if match:
                    functions.append(match.group(1))
            
            # Class declarations
            if re.search(r'class\s+(\w+)', line):
                match = re.search(r'class\s+(\w+)', line)
                if match:
                    classes.append(match.group(1))
            
            # Complexity indicators
            if re.search(r'\b(if|for|while|switch|catch)\b', line):
                complexity += 1
            
            # Code quality checks
            if 'console.log(' in line and not line.strip().startswith('//'):
                issues.append({
                    "type": "code_quality",
                    "severity": "low",
                    "line": i,
                    "message": "Consider removing console.log() statement"
                })
                suggestions.append("Use proper logging instead of console.log()")
            
            if 'eval(' in line:
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "line": i,
                    "message": "Use of eval() poses security risks"
                })
                suggestions.append("Avoid using eval() - consider safer alternatives")
            
            if len(line) > 120:
                issues.append({
                    "type": "maintainability",
                    "severity": "low",
                    "line": i,
                    "message": "Line too long (>120 characters)"
                })
        
        maintainability_score = max(0, 100 - (complexity * 3) - (len(issues) * 4))
        
        return {
            "functions": functions,
            "classes": classes,
            "complexity": complexity,
            "maintainability_score": maintainability_score,
            "issues": issues,
            "suggestions": suggestions
        }
    
    @staticmethod
    def _calculate_complexity(node):
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    @staticmethod
    def _detect_python_code_smells(content: str, tree) -> List[Dict[str, Any]]:
        """Detect common Python code smells"""
        issues = []
        
        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    issues.append({
                        "type": "code_smell",
                        "severity": "medium",
                        "line": node.lineno,
                        "message": f"Function '{node.name}' is too long ({func_lines} lines)"
                    })
        
        # Check for too many parameters
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 5:
                    issues.append({
                        "type": "code_smell",
                        "severity": "medium",
                        "line": node.lineno,
                        "message": f"Function '{node.name}' has too many parameters ({param_count})"
                    })
        
        return issues
    
    @staticmethod
    def _detect_python_security_issues(content: str, tree) -> List[Dict[str, Any]]:
        """Detect potential security issues in Python code"""
        issues = []
        
        # Check for dangerous functions
        dangerous_calls = ['eval', 'exec', 'compile']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in dangerous_calls:
                    issues.append({
                        "type": "security",
                        "severity": "high",
                        "line": node.lineno,
                        "message": f"Use of {node.func.id}() poses security risks"
                    })
        
        # Check for SQL injection patterns
        if re.search(r'execute\s*\(\s*["\'].*%.*["\']', content):
            issues.append({
                "type": "security",
                "severity": "high",
                "line": 0,
                "message": "Potential SQL injection vulnerability"
            })
        
        return issues

@router.post("/pr/review", response_model=EnhancedPRReviewResponse)
async def review_pull_request(request: PRReviewRequest):
    """
    Enhanced pull request review with detailed code quality analysis
    """
    if not request.github_token:
        raise HTTPException(status_code=400, detail="GitHub token is required")

    try:
        # Extract PR information
        match = re.match(r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)", request.pr_url)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid GitHub pull request URL format")

        owner = match.group("owner")
        repo = match.group("repo")
        pull_number = match.group("number")
        
        logger.info(f"Starting enhanced PR review for {owner}/{repo}#{pull_number}")

        headers = {
            "Authorization": f"token {request.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Code-Quality-Agent/1.0"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Fetch PR information
            pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
            pr_response = await client.get(pr_url, headers=headers)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            # Fetch PR files
            files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
            files_response = await client.get(files_url, headers=headers)
            files_response.raise_for_status()
            files = files_response.json()

            # Analyze each file
            file_analyses = []
            total_complexity = 0
            total_issues = []
            all_suggestions = []
            total_lines_added = 0
            total_lines_deleted = 0
            
            code_extensions = {
                '.py': 'python',
                '.js': 'javascript',
                '.jsx': 'javascript',
                '.ts': 'typescript', 
                '.tsx': 'typescript'
            }
            
            for file in files:
                filename = file.get("filename", "")
                patch = file.get("patch", "")
                status = file.get("status", "")
                additions = file.get("additions", 0)
                deletions = file.get("deletions", 0)
                
                # Only analyze code files
                file_ext = Path(filename).suffix.lower()
                if file_ext not in code_extensions:
                    continue
                
                total_lines_added += additions
                total_lines_deleted += deletions
                
                # Get file content for analysis
                try:
                    if status != "removed":
                        # Fetch current file content
                        content_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}?ref={pr_data['head']['sha']}"
                        content_response = await client.get(content_url, headers=headers)
                        content_response.raise_for_status()
                        content_data = content_response.json()
                        
                        import base64
                        file_content = base64.b64decode(content_data['content']).decode('utf-8')
                        
                        # Analyze based on language
                        if code_extensions[file_ext] in ['python']:
                            analysis_result = CodeAnalyzer.analyze_python_file(file_content, filename)
                        else:
                            analysis_result = CodeAnalyzer.analyze_javascript_file(file_content, filename)
                        
                        total_complexity += analysis_result['complexity']
                        total_issues.extend(analysis_result['issues'])
                        all_suggestions.extend(analysis_result['suggestions'])
                        
                        file_analysis = FileAnalysis(
                            filename=filename,
                            language=code_extensions[file_ext],
                            lines_added=additions,
                            lines_deleted=deletions,
                            complexity_score=analysis_result['complexity'],
                            maintainability_score=analysis_result['maintainability_score'],
                            issues=analysis_result['issues'],
                            suggestions=analysis_result['suggestions'][:5],  # Top 5
                            functions_changed=analysis_result['functions'],
                            classes_changed=analysis_result['classes']
                        )
                        
                        file_analyses.append(file_analysis)
                        
                except Exception as e:
                    logger.warning(f"Could not analyze file {filename}: {str(e)}")
                    continue

            # Calculate overall metrics
            if file_analyses:
                avg_maintainability = sum(f.maintainability_score for f in file_analyses) / len(file_analyses)
                overall_quality_score = max(0, avg_maintainability - (len(total_issues) * 2))
            else:
                overall_quality_score = 100
                avg_maintainability = 100

            # Risk assessment
            critical_issues = [i for i in total_issues if i.get('severity') == 'critical']
            high_issues = [i for i in total_issues if i.get('severity') == 'high']
            
            if critical_issues:
                risk_assessment = "HIGH - Critical issues found"
            elif len(high_issues) > 3:
                risk_assessment = "MEDIUM - Multiple high-severity issues"
            elif total_complexity > 50:
                risk_assessment = "MEDIUM - High complexity changes"
            else:
                risk_assessment = "LOW - Changes look good"

            # Generate recommendations
            recommendations = []
            if total_complexity > 30:
                recommendations.append("Consider breaking down complex functions to improve maintainability")
            if len(critical_issues) > 0:
                recommendations.append("Address critical security and syntax issues before merging")
            if avg_maintainability < 70:
                recommendations.append("Refactor code to improve maintainability scores")
            if total_lines_added > 300:
                recommendations.append("Large changeset - consider splitting into smaller PRs")
            
            # Remove duplicates from suggestions
            unique_suggestions = list(set(all_suggestions))
            
            # Summary metrics
            summary_metrics = CodeQualityMetrics(
                complexity=total_complexity,
                maintainability_score=avg_maintainability,
                code_smells=[i['message'] for i in total_issues if i.get('type') == 'code_smell'],
                security_issues=[i['message'] for i in total_issues if i.get('type') == 'security'],
                performance_issues=[i['message'] for i in total_issues if i.get('type') == 'performance'],
                best_practices_violations=[i['message'] for i in total_issues if i.get('type') == 'code_quality']
            )

            # Changeset impact
            changeset_impact = {
                "files_modified": len([f for f in files if f.get("status") == "modified"]),
                "files_added": len([f for f in files if f.get("status") == "added"]),
                "files_deleted": len([f for f in files if f.get("status") == "removed"]),
                "functions_affected": sum(len(f.functions_changed) for f in file_analyses),
                "classes_affected": sum(len(f.classes_changed) for f in file_analyses),
                "total_complexity_added": total_complexity
            }

            review_id = f"{owner}-{repo}-{pull_number}-{str(uuid.uuid4())[:8]}"
            
            message = f"Enhanced code quality analysis completed. Reviewed {len(file_analyses)} code files with overall quality score of {overall_quality_score:.1f}%"

            return EnhancedPRReviewResponse(
                review_id=review_id,
                status="completed",
                message=message,
                files_reviewed=len(file_analyses),
                lines_added=total_lines_added,
                lines_deleted=total_lines_deleted,
                overall_quality_score=round(overall_quality_score, 1),
                risk_assessment=risk_assessment,
                file_analyses=file_analyses,
                summary_metrics=summary_metrics,
                recommendations=recommendations[:10],
                changeset_impact=changeset_impact
            )

    except httpx.HTTPStatusError as e:
        error_detail = f"GitHub API error: {e.response.status_code}"
        if e.response.status_code == 401:
            error_detail = "Invalid GitHub token or insufficient permissions"
        elif e.response.status_code == 404:
            error_detail = "Pull request not found or access denied"
        
        logger.error(f"GitHub API error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    
    except Exception as e:
        logger.error(f"Error in enhanced PR review: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Health check endpoint
@router.get("/pr/health")
async def pr_review_health():
    """Health check for enhanced PR review service"""
    return {"status": "healthy", "service": "enhanced_pr_review", "features": ["complexity_analysis", "security_scanning", "maintainability_scoring"]}