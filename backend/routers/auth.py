"""Authentication routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import RegisterRequest, LoginRequest, AuthResponse, UserResponse
from middleware import get_current_user
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    from db.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        # Check if username already exists
        existing_user = supabase.table("profiles").select("id").eq(
            "username", request.username
        ).execute()
        
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        
        # Create user in Supabase Auth
        # Note: This would typically be done via Supabase client SDK
        # For now, we'll create a profile with a UUID
        user_id = str(uuid.uuid4())
        
        # Create profile
        profile_data = {
            "id": user_id,
            "username": request.username,
            "display_name": request.username,
            "avatar_url": None,
            "bio_haiku_id": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("profiles").insert(profile_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create profile"
            )
        
        # Return auth response (in production, return actual Supabase JWT)
        return AuthResponse(
            access_token=user_id,  # Placeholder
            user_id=user_id,
            username=request.username
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user."""
    # TODO: Implement login with Supabase Auth
    # This would validate email/password against Supabase Auth
    # and return a JWT token
    
    from db.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        # For now, just find the user by email
        # In production, validate password via Supabase Auth
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Login not yet implemented (use Supabase SDK on frontend)"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/logout")
async def logout(user_id: str = Depends(get_current_user)):
    """Logout user."""
    # Logout is typically handled on the frontend by clearing the token
    return {"message": "Logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    """Get current authenticated user."""
    from db.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        response = supabase.table("profiles").select(
            "id, username, display_name, avatar_url, created_at"
        ).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = response.data[0]
        
        return UserResponse(
            id=user["id"],
            email="",  # Email not stored in profiles table
            username=user["username"],
            display_name=user["display_name"],
            avatar_url=user["avatar_url"],
            created_at=user["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )
