import ast
import re
import uuid
from typing import List, Dict, Any, Set
from collections import defaultdict
import logging

from app.models.analysis import CodeIssue, IssueCategory, IssueSeverity

logger = logging.getLogger(__name__)

class ASTAnalyzer:
    """Advanced AST-based code analysis"""
    
    def __init__(self):
        self.function_names = set()
        self.class_names = set()
        self.variable_names = set()
        
    async def analyze(self, content: str, file_path: str, language: str) -> List[CodeIssue]:
        """Analyze code using AST parsing"""
        issues = []
        
        if language == 'python':
            issues.extend(await self._analyze_python_ast(content, file_path))
        elif language in ['javascript', 'typescript']:
            issues.extend(await self._analyze_js_patterns(content, file_path))
        
        return issues
    
    async def _analyze_python_ast(self, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze Python code using AST"""
        issues = []
        
        try:
            tree = ast.parse(content)
            visitor = PythonASTVisitor(file_path)
            visitor.visit(tree)
            issues.extend(visitor.issues)
        except SyntaxError as e:
            issue = CodeIssue(
                id=str(uuid.uuid4()),
                category=IssueCategory.CODE_QUALITY,
                severity=IssueSeverity.HIGH,
                title="Syntax Error",
                description=f"Syntax error in Python code: {str(e)}",
                file_path=file_path,
                line_number=getattr(e, 'lineno', None),
                suggestion="Fix the syntax error",
                impact_score=9.0,
                confidence=1.0,
                tags=["syntax", "error"]
            )
            issues.append(issue)
        except Exception as e:
            logger.error(f"AST analysis failed for {file_path}: {str(e)}")
        
        return issues
    
    async def _analyze_js_patterns(self, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze JavaScript/TypeScript using regex patterns"""
        issues = []
        lines = content.split('\n')
        
        # Check for common JavaScript issues
        patterns = [
            (r'==\s*[^=]', 'Use === instead of == for strict equality', IssueSeverity.MEDIUM),
            (r'!=\s*[^=]', 'Use !== instead of != for strict inequality', IssueSeverity.MEDIUM),
            (r'var\s+\w+', 'Consider using let or const instead of var', IssueSeverity.LOW),
            (r'function\s*\(\s*\)\s*{[^}]*}', 'Consider using arrow functions', IssueSeverity.LOW),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, description, severity in patterns:
                if re.search(pattern, line):
                    issue = CodeIssue(
                        id=str(uuid.uuid4()),
                        category=IssueCategory.CODE_QUALITY,
                        severity=severity,
                        title=f"JavaScript best practice: {description}",
                        description=description,
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggestion=description,
                        impact_score=3.0,
                        confidence=0.8,
                        tags=["javascript", "best-practice"]
                    )
                    issues.append(issue)
        
        return issues

class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor for Python code analysis"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
        self.function_complexity = {}
        self.current_function = None
        self.nested_level = 0
        self.imports = set()
        
    def visit_FunctionDef(self, node):
        """Analyze function definitions"""
        self.current_function = node.name
        
        # Check function length
        if hasattr(node, 'end_lineno') and node.end_lineno and node.lineno:
            func_length = node.end_lineno - node.lineno
            if func_length > 50:
                self.issues.append(CodeIssue(
                    id=str(uuid.uuid4()),
                    category=IssueCategory.MAINTAINABILITY,
                    severity=IssueSeverity.MEDIUM,
                    title="Function too long",
                    description=f"Function '{node.name}' is {func_length} lines long",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    suggestion="Consider breaking this function into smaller functions",
                    impact_score=5.0,
                    confidence=1.0,
                    tags=["maintainability", "function-length"]
                ))
        
        # Check parameter count
        arg_count = len(node.args.args)
        if arg_count > 7:
            self.issues.append(CodeIssue(
                id=str(uuid.uuid4()),
                category=IssueCategory.MAINTAINABILITY,
                severity=IssueSeverity.MEDIUM,
                title="Too many parameters",
                description=f"Function '{node.name}' has {arg_count} parameters",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="Consider using a parameter object or reducing parameters",
                impact_score=4.0,
                confidence=1.0,
                tags=["maintainability", "parameters"]
            ))
        
        # Check for missing docstring
        if not ast.get_docstring(node) and not node.name.startswith('_'):
            self.issues.append(CodeIssue(
                id=str(uuid.uuid4()),
                category=IssueCategory.DOCUMENTATION,
                severity=IssueSeverity.LOW,
                title="Missing docstring",
                description=f"Public function '{node.name}' has no docstring",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="Add a docstring to document the function's purpose",
                impact_score=2.0,
                confidence=1.0,
                tags=["documentation", "docstring"]
            ))
        
        self.generic_visit(node)
        self.current_function = None
    
    def visit_ClassDef(self, node):
        """Analyze class definitions"""
        # Check for missing docstring
        if not ast.get_docstring(node):
            self.issues.append(CodeIssue(
                id=str(uuid.uuid4()),
                category=IssueCategory.DOCUMENTATION,
                severity=IssueSeverity.LOW,
                title="Missing class docstring",
                description=f"Class '{node.name}' has no docstring",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="Add a docstring to document the class's purpose",
                impact_score=2.0,
                confidence=1.0,
                tags=["documentation", "docstring", "class"]
            ))
        
        # Check class size
        if hasattr(node, 'end_lineno') and node.end_lineno and node.lineno:
            class_length = node.end_lineno - node.lineno
            if class_length > 200:
                self.issues.append(CodeIssue(
                    id=str(uuid.uuid4()),
                    category=IssueCategory.MAINTAINABILITY,
                    severity=IssueSeverity.MEDIUM,
                    title="Class too large",
                    description=f"Class '{node.name}' is {class_length} lines long",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    suggestion="Consider splitting this class into smaller, more focused classes",
                    impact_score=6.0,
                    confidence=1.0,
                    tags=["maintainability", "class-size"]
                ))
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Track imports"""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Track from imports"""
        if node.module:
            for alias in node.names:
                self.imports.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)
    
    def visit_Try(self, node):
        """Analyze try/except blocks"""
        # Check for bare except
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append(CodeIssue(
                    id=str(uuid.uuid4()),
                    category=IssueCategory.CODE_QUALITY,
                    severity=IssueSeverity.MEDIUM,
                    title="Bare except clause",
                    description="Using bare 'except:' can hide bugs",
                    file_path=self.file_path,
                    line_number=handler.lineno,
                    suggestion="Specify the exception type or use 'except Exception:'",
                    impact_score=5.0,
                    confidence=1.0,
                    tags=["exception-handling", "best-practice"]
                ))
        
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Analyze for loops"""
        self.nested_level += 1
        
        # Check for deeply nested loops
        if self.nested_level > 3:
            self.issues.append(CodeIssue(
                id=str(uuid.uuid4()),
                category=IssueCategory.COMPLEXITY,
                severity=IssueSeverity.MEDIUM,
                title="Deeply nested loop",
                description=f"Loop is nested {self.nested_level} levels deep",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="Consider extracting inner logic to separate functions",
                impact_score=6.0,
                confidence=1.0,
                tags=["complexity", "nesting"]
            ))
        
        self.generic_visit(node)
        self.nested_level -= 1
    
    def visit_While(self, node):
        """Analyze while loops"""
        self.nested_level += 1
        
        # Check for deeply nested loops
        if self.nested_level > 3:
            self.issues.append(CodeIssue(
                id=str(uuid.uuid4()),
                category=IssueCategory.COMPLEXITY,
                severity=IssueSeverity.MEDIUM,
                title="Deeply nested while loop",
                description=f"While loop is nested {self.nested_level} levels deep",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="Consider extracting inner logic to separate functions",
                impact_score=6.0,
                confidence=1.0,
                tags=["complexity", "nesting"]
            ))
        
        self.generic_visit(node)
        self.nested_level -= 1
    
    def visit_If(self, node):
        """Analyze if statements"""
        self.nested_level += 1
        
        # Check for deeply nested conditionals
        if self.nested_level > 4:
            self.issues.append(CodeIssue(
                id=str(uuid.uuid4()),
                category=IssueCategory.COMPLEXITY,
                severity=IssueSeverity.MEDIUM,
                title="Deeply nested conditional",
                description=f"Conditional is nested {self.nested_level} levels deep",
                file_path=self.file_path,
                line_number=node.lineno,
                suggestion="Consider using guard clauses or extracting logic",
                impact_score=5.0,
                confidence=1.0,
                tags=["complexity", "nesting"]
            ))
        
        self.generic_visit(node)
        self.nested_level -= 1