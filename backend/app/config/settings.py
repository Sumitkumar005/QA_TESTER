from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Environment and Logging
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Code Quality Intelligence Agent"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "code_quality_db"
    
    # Vector Database (FAISS)
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # GitHub
    GITHUB_TOKEN: str = ""
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    TEMP_DIR: str = "./temp"
    
    # Analysis
    SUPPORTED_LANGUAGES: List[str] = [
        "python", "javascript", "typescript", "java", "go", 
        "rust", "cpp", "c", "csharp", "ruby", "php"
    ]
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    return Settings()