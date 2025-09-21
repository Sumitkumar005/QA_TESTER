import subprocess
import logging
import os
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class GitUtils:
    """Utilities for Git operations"""
    
    @staticmethod
    def is_git_repository(path: str) -> bool:
        """Check if path is a git repository"""
        git_dir = os.path.join(path, '.git')
        return os.path.exists(git_dir)
    
    @staticmethod
    def get_git_info(repo_path: str) -> Optional[Dict[str, str]]:
        """Get git repository information"""
        if not GitUtils.is_git_repository(repo_path):
            return None
        
        try:
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Get latest commit hash
            commit_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            latest_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
            
            # Get remote URL
            remote_result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            remote_url = remote_result.stdout.strip() if remote_result.returncode == 0 else "unknown"
            
            return {
                'branch': current_branch,
                'commit': latest_commit,
                'remote_url': remote_url
            }
            
        except Exception as e:
            logger.error(f"Failed to get git info for {repo_path}: {str(e)}")
            return None
    
    @staticmethod
    def get_changed_files(repo_path: str, base_branch: str = "main") -> List[str]:
        """Get list of changed files compared to base branch"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', f'{base_branch}...HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.split('\n') if f.strip()]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get changed files: {str(e)}")
            return []
    
    @staticmethod
    def get_file_history(repo_path: str, file_path: str, max_commits: int = 10) -> List[Dict[str, str]]:
        """Get commit history for a specific file"""
        try:
            result = subprocess.run([
                'git', 'log', '--oneline', f'-{max_commits}', '--', file_path
            ], cwd=repo_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        commits.append({
                            'hash': parts[0],
                            'message': parts[1]
                        })
            
            return commits
            
        except Exception as e:
            logger.error(f"Failed to get file history: {str(e)}")
            return []