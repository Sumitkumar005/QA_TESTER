import os
import tempfile
import subprocess
import logging
from typing import Optional
from pathlib import Path

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class GitHubService:
    """Service for GitHub operations"""
    
    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
    
    async def clone_repository(self, repo_url: str) -> str:
        """Clone a GitHub repository - OPTIMIZED FOR SPEED"""
        try:
            # Parse repository URL
            if repo_url.startswith("https://github.com/"):
                repo_name = repo_url.split("/")[-1].replace(".git", "")
            else:
                raise ValueError("Invalid GitHub URL")

            # Create temporary directory
            temp_path = self.temp_dir / f"repo_{repo_name}_{os.getpid()}"
            temp_path.mkdir(exist_ok=True)

            # Prepare clone URL with authentication if token is available
            clone_url = repo_url
            if settings.GITHUB_TOKEN and settings.GITHUB_TOKEN != "your_github_token_here":
                clone_url = repo_url.replace(
                    "https://",
                    f"https://oauth2:{settings.GITHUB_TOKEN}@"
                )

            # OPTIMIZED CLONE COMMAND - FASTER OPTIONS
            cmd = [
                "git", "clone",
                "--depth", "1",           # Shallow clone
                "--single-branch",        # Only main branch
                "--no-tags",             # Skip tags
                "--filter=blob:none",    # Skip large files initially
                clone_url,
                str(temp_path)
            ]

            logger.info(f"Fast cloning repository: {repo_url}")

            # REDUCED TIMEOUT
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes instead of 5
            )

            if process.returncode != 0:
                logger.error(f"Git clone failed: {process.stderr}")
                raise Exception(f"Git clone failed: {process.stderr}")

            logger.info(f"Successfully cloned repository to {temp_path}")
            return str(temp_path)

        except subprocess.TimeoutExpired:
            logger.error(f"Git clone timed out for {repo_url}")
            raise Exception("Repository clone timed out - repository may be too large")
        except Exception as e:
            logger.error(f"Failed to clone repository {repo_url}: {str(e)}")
            raise
    
    def is_valid_github_url(self, url: str) -> bool:
        """Check if URL is a valid GitHub repository URL"""
        return (
            url.startswith("https://github.com/") and
            url.count("/") >= 4 and
            not url.endswith("/")
        )
    
    def cleanup_temp_directory(self, temp_path: str) -> None:
        """Clean up temporary directory after analysis"""
        try:
            import shutil
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
                logger.info(f"Cleaned up temporary directory: {temp_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup directory {temp_path}: {str(e)}")