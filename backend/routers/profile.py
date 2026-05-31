"""Profile routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import ProfileUpdateRequest, ProfileResponse
from middleware import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{username}", response_model=ProfileResponse)
async def get_profile(username: str):
    """Get public profile by username."""
    from db.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        response = supabase.table("profiles").select(
            "*"
        ).eq("username", username).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = response.data[0]
        
        return ProfileResponse(
            id=user["id"],
            username=user["username"],
            display_name=user["display_name"],
            avatar_url=user["avatar_url"],
            bio_haiku_id=user["bio_haiku_id"],
            created_at=user["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )

@router.get("/me")
async def get_my_profile(user_id: str = Depends(get_current_user)):
    """Get current user's profile."""
    from db.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        response = supabase.table("profiles").select(
            "*"
        ).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        user = response.data[0]
        
        return ProfileResponse(
            id=user["id"],
            username=user["username"],
            display_name=user["display_name"],
            avatar_url=user["avatar_url"],
            bio_haiku_id=user["bio_haiku_id"],
            created_at=user["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get my profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )

@router.put("/me", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user)
):
    """Update current user's profile."""
    from db.database import get_supabase
    from datetime import datetime
    
    try:
        supabase = get_supabase()
        
        update_data = {}
        if request.display_name is not None:
            update_data["display_name"] = request.display_name
        if request.bio is not None:
            # bio is not in schema, but we can store it in display_name for now
            pass
        if request.avatar_url is not None:
            update_data["avatar_url"] = request.avatar_url
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("profiles").update(update_data).eq(
            "id", user_id
        ).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        user = response.data[0]
        
        return ProfileResponse(
            id=user["id"],
            username=user["username"],
            display_name=user["display_name"],
            avatar_url=user["avatar_url"],
            bio_haiku_id=user["bio_haiku_id"],
            created_at=user["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.post("/me/identity-haiku/{haiku_id}")
async def set_identity_haiku(
    haiku_id: str,
    user_id: str = Depends(get_current_user)
):
    """Set the haiku that defines the user's profile."""
    from db.database import get_supabase
    from datetime import datetime
    
    try:
        supabase = get_supabase()
        
        # Verify haiku belongs to user
        haiku_response = supabase.table("haikus").select(
            "id, user_id"
        ).eq("id", haiku_id).execute()
        
        if not haiku_response.data or haiku_response.data[0]["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your haiku"
            )
        
        # Update profile
        supabase.table("profiles").update({
            "bio_haiku_id": haiku_id,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", user_id).execute()
        
        # Mark haiku as identity haiku
        supabase.table("haikus").update({
            "is_identity_haiku": True
        }).eq("id", haiku_id).execute()
        
        return {"message": "Identity haiku set"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set identity haiku: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set identity haiku"
        )
