"""Middleware and authentication utilities."""
import logging
from fastapi import Request, HTTPException, Depends, status
from typing import Optional

logger = logging.getLogger(__name__)

def get_current_user(request: Request) -> str:
    """
    Dependency to get current authenticated user ID from request.
    
    Usage in routes:
        @router.get("/me")
        async def get_me(user_id: str = Depends(get_current_user)):
            ...
    """
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user_id

def get_token(request: Request) -> Optional[str]:
    """Get JWT token from request."""
    return getattr(request.state, 'token', None)

