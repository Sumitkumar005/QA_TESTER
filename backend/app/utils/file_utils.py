import os
import shutil
import tempfile
import zipfile
import tarfile
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def get_file_language(file_path: str) -> str:
    """Determine programming language from file extension"""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.cpp': 'cpp',
        '.cxx': 'cpp',
        '.cc': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.cs': 'csharp',
        '.rb': 'ruby',
        '.php': 'php',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.swift': 'swift',
        '.m': 'objective-c',
        '.r': 'r',
        '.sql': 'sql',
        '.sh': 'shell',
        '.bash': 'shell',
        '.ps1': 'powershell',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less'
    }
    
    _, ext = os.path.splitext(file_path)
    return extension_map.get(ext.lower(), 'text')

def count_lines_of_code(content: str) -> int:
    """Count lines of code (excluding empty lines and comments)"""
    lines = content.split('\n')
    loc = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
            loc += 1
    
    return loc

async def extract_archive(archive_path: str) -> str:
    """Extract archive file and return path to extracted directory"""
    try:
        extract_dir = tempfile.mkdtemp()
        
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif archive_path.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
        elif archive_path.endswith('.tar'):
            with tarfile.open(archive_path, 'r') as tar_ref:
                tar_ref.extractall(extract_dir)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path}")
        
        # Find the actual content directory (archives often have a root folder)
        contents = os.listdir(extract_dir)
        if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
            return os.path.join(extract_dir, contents[0])
        
        return extract_dir
        
    except Exception as e:
        logger.error(f"Failed to extract archive {archive_path}: {str(e)}")
        raise

async def cleanup_temp_files(path: str):
    """Clean up temporary files and directories"""
    try:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            logger.info(f"Cleaned up temporary path: {path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup {path}: {str(e)}")

def is_text_file(file_path: str) -> bool:
    """Check if file is likely a text file"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return False  # Binary file
        return True
    except:
        return False

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def safe_read_file(file_path: str, max_size: int = 10 * 1024 * 1024) -> Optional[str]:
    """Safely read a text file with size limit"""
    try:
        if get_file_size(file_path) > max_size:
            logger.warning(f"File {file_path} too large, skipping")
            return None
        
        if not is_text_file(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        logger.warning(f"Failed to read file {file_path}: {str(e)}")
        return None