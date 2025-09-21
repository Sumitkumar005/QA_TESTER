import os
import ast
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import subprocess
import re
from datetime import datetime
import uuid

import google.generativeai as genai
from app.config.settings import get_settings
from app.models.analysis import (
    CodeIssue, FileMetrics, RepositoryMetrics, AnalysisResult,
    IssueCategory, IssueSeverity, AnalysisStatus
)
from app.core.ast_parser import ASTAnalyzer
from app.core.severity_scorer import SeverityScorer
from app.utils.file_utils import get_file_language, count_lines_of_code

settings = get_settings()
logger = logging.getLogger(__name__)

class CodeQualityAnalyzer:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            logger.warning("Gemini API key not configured")
            self.model = None
        
        self.ast_analyzer = ASTAnalyzer()
        self.severity_scorer = SeverityScorer()
        
        # Security patterns for different languages
        self.security_patterns = {
            'python': [
                (r'exec\s*\(', 'Use of exec() can lead to code injection'),
                (r'eval\s*\(', 'Use of eval() can lead to code injection'),
                (r'pickle\.loads?\s*\(', 'Pickle can execute arbitrary code'),
                (r'subprocess\.call.*shell\s*=\s*True', 'Shell injection vulnerability'),
                (r'sql.*\+.*', 'Possible SQL injection'),
            ],
            'javascript': [
                (r'eval\s*\(', 'Use of eval() can lead to code injection'),
                (r'innerHTML\s*=', 'Potential XSS vulnerability'),
                (r'document\.write\s*\(', 'document.write can lead to XSS'),
                (r'window\.location\s*=.*\+', 'Potential open redirect'),
            ],
            'java': [
                (r'Runtime\.getRuntime\(\)\.exec', 'Command injection vulnerability'),
                (r'System\.exit\s*\(', 'System.exit can terminate application'),
                (r'Random\s+.*=\s+new\s+Random\(\)', 'Use SecureRandom for cryptographic purposes'),
            ]
        }
        
        # Performance patterns
        self.performance_patterns = {
            'python': [
                (r'for.*in.*range\(len\(', 'Use enumerate() instead of range(len())'),
                (r'\.append\(.*\)\s*$', 'Consider list comprehension for better performance'),
            ],
            'javascript': [
                (r'document\.getElementById.*in.*loop', 'Cache DOM queries outside loops'),
                (r'\.innerHTML\s*\+=', 'Use textContent or build string first'),
            ]
        }

    async def analyze_repository(self, repo_path: str, report_id: str) -> AnalysisResult:
        """Main analysis entry point"""
        try:
            logger.info(f"Starting analysis for {repo_path} with report_id {report_id}")
            
            # Initialize result
            result = AnalysisResult(
                report_id=report_id,
                status=AnalysisStatus.IN_PROGRESS,
                source_info={"path": repo_path, "type": "local"},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Get all code files
            code_files = await self._get_code_files(repo_path)
            logger.info(f"Found {len(code_files)} code files")
            
            # Analyze each file
            all_issues = []
            file_metrics = []
            
            for file_path in code_files:
                try:
                    file_issues, metrics = await self._analyze_file(file_path, repo_path)
                    all_issues.extend(file_issues)
                    if metrics:
                        file_metrics.append(metrics)
                except Exception as e:
                    logger.error(f"Error analyzing file {file_path}: {str(e)}")
                    continue
            
            # Calculate repository metrics
            repo_metrics = await self._calculate_repository_metrics(file_metrics, code_files)
            
            # Score and prioritize issues
            scored_issues = await self._score_issues(all_issues)
            
            # Update result
            result.status = AnalysisStatus.COMPLETED
            result.issues = scored_issues
            result.file_metrics = file_metrics
            result.metrics = repo_metrics
            result.completed_at = datetime.utcnow()
            result.updated_at = datetime.utcnow()
            
            logger.info(f"Analysis completed. Found {len(scored_issues)} issues")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            result.status = AnalysisStatus.FAILED
            result.error_message = str(e)
            result.updated_at = datetime.utcnow()
            return result
            

    async def _get_code_files(self, repo_path: str) -> List[str]:
        """Get all code files from repository OR single file"""
        code_files = []
        supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php'
        }

        # CHECK IF IT'S A SINGLE FILE
        if os.path.isfile(repo_path):
            _, ext = os.path.splitext(repo_path)
            if ext in supported_extensions:
                code_files.append(repo_path)
                logger.info(f"Analyzing single file: {repo_path}")
            else:
                logger.warning(f"Unsupported file type: {ext}")
            return code_files

        # IT'S A DIRECTORY - ORIGINAL LOGIC
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'venv', '.venv'}]

            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                if ext in supported_extensions:
                    code_files.append(file_path)

        return code_files

    async def _analyze_file(self, file_path: str, repo_root: str) -> tuple[List[CodeIssue], Optional[FileMetrics]]:
        """Analyze a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            language = get_file_language(file_path)

            # FIX FOR SINGLE FILES
            if os.path.isfile(repo_root):
                # If repo_root is actually a file, use the filename
                relative_path = os.path.basename(file_path)
            else:
                # Normal directory case
                relative_path = os.path.relpath(file_path, repo_root)
            
            # Basic metrics
            lines_of_code = count_lines_of_code(content)
            complexity = await self._calculate_complexity(content, language)
            
            # Find issues
            issues = []
            
            # Security analysis
            security_issues = await self._analyze_security(content, relative_path, language)
            issues.extend(security_issues)
            
            # Performance analysis
            performance_issues = await self._analyze_performance(content, relative_path, language)
            issues.extend(performance_issues)
            
            # Code quality analysis
            quality_issues = await self._analyze_code_quality(content, relative_path, language)
            issues.extend(quality_issues)
            
            # AST-based analysis for supported languages
            if language in ['python', 'javascript']:
                ast_issues = await self.ast_analyzer.analyze(content, relative_path, language)
                issues.extend(ast_issues)
            
            # AI-powered analysis (if available)
            if self.model:
                ai_issues = await self._ai_analyze_code(content, relative_path, language)
                issues.extend(ai_issues)
            
            # Create file metrics
            metrics = FileMetrics(
                file_path=relative_path,
                language=language,
                lines_of_code=lines_of_code,
                complexity=complexity,
                maintainability_index=max(0, 100 - complexity * 10 - len(issues) * 5),
                issues_count=len(issues)
            )
            
            return issues, metrics
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return [], None

    async def _analyze_security(self, content: str, file_path: str, language: str) -> List[CodeIssue]:
        """Analyze security vulnerabilities"""
        issues = []
        
        if language not in self.security_patterns:
            return issues
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, description in self.security_patterns[language]:
                if re.search(pattern, line, re.IGNORECASE):
                    issue = CodeIssue(
                        id=str(uuid.uuid4()),
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.HIGH,
                        title=f"Security vulnerability: {description}",
                        description=description,
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggestion=f"Review and secure this code pattern",
                        impact_score=8.0,
                        confidence=0.8,
                        tags=["security", "vulnerability"]
                    )
                    issues.append(issue)
        
        return issues

    async def _analyze_performance(self, content: str, file_path: str, language: str) -> List[CodeIssue]:
        """Analyze performance issues"""
        issues = []
        
        if language not in self.performance_patterns:
            return issues
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, description in self.performance_patterns[language]:
                if re.search(pattern, line, re.IGNORECASE):
                    issue = CodeIssue(
                        id=str(uuid.uuid4()),
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.MEDIUM,
                        title=f"Performance issue: {description}",
                        description=description,
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggestion=description,
                        impact_score=5.0,
                        confidence=0.7,
                        tags=["performance", "optimization"]
                    )
                    issues.append(issue)
        
        return issues

    async def _analyze_code_quality(self, content: str, file_path: str, language: str) -> List[CodeIssue]:
        """Analyze general code quality issues"""
        issues = []
        lines = content.split('\n')
        
        # Check for long lines
        for line_num, line in enumerate(lines, 1):
            if len(line) > 120:
                issue = CodeIssue(
                    id=str(uuid.uuid4()),
                    category=IssueCategory.CODE_QUALITY,
                    severity=IssueSeverity.LOW,
                    title="Line too long",
                    description=f"Line exceeds 120 characters ({len(line)} chars)",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line[:100] + "..." if len(line) > 100 else line,
                    suggestion="Break long lines into multiple lines for better readability",
                    impact_score=2.0,
                    confidence=1.0,
                    tags=["code-quality", "readability"]
                )
                issues.append(issue)
        
        # Check for TODO/FIXME comments
        for line_num, line in enumerate(lines, 1):
            if re.search(r'(TODO|FIXME|HACK)', line, re.IGNORECASE):
                issue = CodeIssue(
                    id=str(uuid.uuid4()),
                    category=IssueCategory.MAINTAINABILITY,
                    severity=IssueSeverity.LOW,
                    title="Technical debt comment",
                    description="Found TODO/FIXME comment indicating incomplete work",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line.strip(),
                    suggestion="Address the technical debt indicated by this comment",
                    impact_score=3.0,
                    confidence=1.0,
                    tags=["technical-debt", "maintainability"]
                )
                issues.append(issue)
        
        return issues

    async def _ai_analyze_code(self, content: str, file_path: str, language: str) -> List[CodeIssue]:
        """Use AI to analyze code for complex issues"""
        if not self.model:
            return []
        
        try:
            prompt = f"""
            Analyze the following {language} code for potential issues. Focus on:
            1. Complex logic that could be simplified
            2. Potential bugs or edge cases
            3. Design pattern violations
            4. Maintainability concerns
            
            Code from {file_path}:
            ```{language}
            {content[:2000]}  # Limit content to avoid token limits
            ```
            
            Return a JSON array of issues with this structure:
            {{
                "title": "Issue title",
                "description": "Detailed description",
                "severity": "critical|high|medium|low",
                "category": "security|performance|code_quality|maintainability|testing|documentation",
                "suggestion": "How to fix this issue",
                "line_number": null or line number if identifiable
            }}
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            # Parse AI response
            try:
                # Extract JSON from response
                response_text = response.text
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end != -1:
                    ai_issues_data = json.loads(response_text[json_start:json_end])
                    
                    issues = []
                    for issue_data in ai_issues_data:
                        issue = CodeIssue(
                            id=str(uuid.uuid4()),
                            category=IssueCategory(issue_data.get('category', 'code_quality')),
                            severity=IssueSeverity(issue_data.get('severity', 'medium')),
                            title=issue_data.get('title', 'AI detected issue'),
                            description=issue_data.get('description', ''),
                            file_path=file_path,
                            line_number=issue_data.get('line_number'),
                            suggestion=issue_data.get('suggestion', ''),
                            impact_score=6.0,  # Default for AI issues
                            confidence=0.6,    # AI confidence
                            tags=["ai-detected"]
                        )
                        issues.append(issue)
                    
                    return issues
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response as JSON")
                
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
        
        return []

    async def _calculate_complexity(self, content: str, language: str) -> float:
        """Calculate cyclomatic complexity"""
        if language == 'python':
            try:
                tree = ast.parse(content)
                complexity = 1  # Base complexity
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                        complexity += 1
                    elif isinstance(node, ast.FunctionDef):
                        complexity += 1
                
                return min(complexity, 50)  # Cap at 50
            except:
                return 10  # Default complexity
        
        # Simple heuristic for other languages
        complexity = content.count('if ') + content.count('while ') + content.count('for ')
        return min(max(complexity, 1), 50)

    async def _calculate_repository_metrics(self, file_metrics: List[FileMetrics], code_files: List[str]) -> RepositoryMetrics:
        """Calculate overall repository metrics"""
        if not file_metrics:
            return RepositoryMetrics(
                total_files=len(code_files),
                total_lines=0,
                languages={},
                complexity_average=0.0,
                maintainability_average=0.0,
                technical_debt_hours=0.0
            )
        
        total_lines = sum(fm.lines_of_code for fm in file_metrics)
        languages = {}
        
        for fm in file_metrics:
            languages[fm.language] = languages.get(fm.language, 0) + 1
        
        complexity_avg = sum(fm.complexity for fm in file_metrics) / len(file_metrics)
        maintainability_avg = sum(fm.maintainability_index for fm in file_metrics) / len(file_metrics)
        
        # Estimate technical debt (simplified)
        total_issues = sum(fm.issues_count for fm in file_metrics)
        tech_debt_hours = total_issues * 0.5  # Assume 30 minutes per issue on average
        
        return RepositoryMetrics(
            total_files=len(code_files),
            total_lines=total_lines,
            languages=languages,
            complexity_average=complexity_avg,
            maintainability_average=maintainability_avg,
            technical_debt_hours=tech_debt_hours
        )

    async def _score_issues(self, issues: List[CodeIssue]) -> List[CodeIssue]:
        """Score and prioritize issues"""
        for issue in issues:
            issue.impact_score = await self.severity_scorer.calculate_impact_score(issue)
        
        # Sort by severity and impact score
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0}
        issues.sort(key=lambda x: (severity_order.get(x.severity.value, 0), x.impact_score), reverse=True)
        
        return issues