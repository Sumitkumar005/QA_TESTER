from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from app.config.settings import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Dependency to get current user from JWT token
    Currently optional - for future authentication implementation
    """
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except jwt.PyJWTError:
        return None

async def get_database():
    """Database dependency"""
    from app.database.mongodb import get_database
    return await get_database()

async def get_vector_engine():
    """Vector database dependency"""
    from app.database.vector_db import get_vector_engine
    return await get_vector_engine()

def get_settings_dependency():
    """Settings dependency"""
    return get_settings()