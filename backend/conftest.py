import pytest
import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from app.config.settings import get_settings
from app.core.analyzer import CodeQualityAnalyzer
from app.core.ast_parser import ASTAnalyzer
from app.core.severity_scorer import SeverityScorer
from app.core.rag_engine import RAGEngine
from app.services.analysis_service import AnalysisService
from app.services.qa_service import QAService

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def settings():
    """Get test settings"""
    return get_settings()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_python_code():
    """Sample Python code for testing"""
    return '''
import os
import sys

class Calculator:
    def add(self, a, b):
        return a + b
    
    def divide(self, a, b):
        return a / b  # Potential division by zero
    
    def unsafe_eval(self, expression):
        return eval(expression)  # Security vulnerability

def long_function_with_many_parameters(param1, param2, param3, param4, param5, param6, param7, param8):
    """This function has too many parameters"""
    # TODO: Refactor this function
    for i in range(len(param1)):  # Should use enumerate
        if param1[i] == param2:
            print("Found match")
    return param1 + param2

# Missing docstring
def undocumented_function():
    pass
'''

@pytest.fixture
def sample_javascript_code():
    """Sample JavaScript code for testing"""
    return '''
function Calculator() {
    this.add = function(a, b) {
        return a + b;
    };
    
    this.divide = function(a, b) {
        return a / b; // No zero check
    };
}

// Using == instead of ===
function compareValues(a, b) {
    if (a == b) {
        return true;
    }
    return false;
}

// Using var instead of let/const
function oldStyleVariable() {
    var x = 10;
    return x;
}

// Potential XSS vulnerability
function updateHTML(content) {
    document.getElementById('content').innerHTML = content;
}
'''