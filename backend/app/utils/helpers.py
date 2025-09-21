import re
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_hash(content: str) -> str:
    """Generate SHA256 hash of content"""
    return hashlib.sha256(content.encode()).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
    return safe_name[:255]  # Limit length

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def extract_code_snippets(content: str, line_number: int, context_lines: int = 3) -> str:
    """Extract code snippet around a specific line"""
    lines = content.split('\n')
    total_lines = len(lines)
    
    start_line = max(0, line_number - context_lines - 1)
    end_line = min(total_lines, line_number + context_lines)
    
    snippet_lines = []
    for i in range(start_line, end_line):
        line_num = i + 1
        prefix = ">>> " if line_num == line_number else "    "
        snippet_lines.append(f"{prefix}{line_num:4d}: {lines[i]}")
    
    return '\n'.join(snippet_lines)

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def parse_severity_from_text(text: str) -> str:
    """Parse severity level from text description"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['critical', 'severe', 'dangerous', 'exploit']):
        return 'critical'
    elif any(word in text_lower for word in ['high', 'important', 'security', 'vulnerability']):
        return 'high'
    elif any(word in text_lower for word in ['medium', 'moderate', 'warning']):
        return 'medium'
    elif any(word in text_lower for word in ['low', 'minor', 'style', 'format']):
        return 'low'
    else:
        return 'info'

def calculate_technical_debt_hours(issues: List[Any]) -> float:
    """Calculate estimated technical debt in hours"""
    severity_hours = {
        'critical': 8.0,  # 1 day
        'high': 4.0,      # Half day
        'medium': 2.0,    # 2 hours
        'low': 0.5,       # 30 minutes
        'info': 0.25      # 15 minutes
    }
    
    total_hours = 0.0
    for issue in issues:
        severity = getattr(issue, 'severity', 'medium')
        if hasattr(severity, 'value'):
            severity = severity.value
        total_hours += severity_hours.get(severity, 2.0)
    
    return round(total_hours, 1)

def group_issues_by_file(issues: List[Any]) -> Dict[str, List[Any]]:
    """Group issues by file path"""
    grouped = {}
    for issue in issues:
        file_path = getattr(issue, 'file_path', 'unknown')
        if file_path not in grouped:
            grouped[file_path] = []
        grouped[file_path].append(issue)
    
    return grouped

def calculate_complexity_score(complexity: float) -> str:
    """Convert complexity number to descriptive score"""
    if complexity <= 5:
        return "Low"
    elif complexity <= 10:
        return "Medium"
    elif complexity <= 20:
        return "High"
    else:
        return "Very High"

def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for special types"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'model_dump'):
            return obj.model_dump()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)