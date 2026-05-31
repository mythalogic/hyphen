"""Admin routes (role-gated)."""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.schemas import AdminStatsResponse
from middleware import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

async def check_admin_role(user_id: str = Depends(get_current_user)) -> str:
    """Verify user has admin role."""
    from db.database import get_supabase
    
    supabase = get_supabase()
    response = supabase.table("admin_users").select("user_id").eq(
        "user_id", user_id
    ).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user_id

@router.get("/users")
async def list_users(
    limit: int = Query(50, ge=1, le=1000),
    user_id: str = Depends(check_admin_role)
):
    """List all users (admin only)."""
    from db.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        response = supabase.table("profiles").select(
            """
            id, username, email, created_at, display_name
            """
        ).limit(limit).execute()
        
        # Count haikus per user
        users = []
        for user in response.data:
            haiku_count_response = supabase.table("haikus").select(
                "id"
            ).eq("user_id", user["id"]).execute()
            
            profile_response = supabase.table("emotional_profiles").select(
                "id"
            ).eq("user_id", user["id"]).limit(1).execute()
            
            users.append({
                **user,
                "haiku_count": len(haiku_count_response.data) if haiku_count_response.data else 0,
                "has_emotional_profile": bool(profile_response.data)
            })
        
        return users
    
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )

@router.get("/haikus")
async def list_haikus(
    limit: int = Query(50, ge=1, le=1000),
    user_id: str = Depends(check_admin_role)
):
    """List all haikus (admin only)."""
    from db.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        response = supabase.table("haikus").select(
            """
            id, user_id, full_text, created_at,
            profiles(username),
            emotional_profiles(tone_tags, primary_emotion, intensity_score)
            """
        ).order("created_at", desc=True).limit(limit).execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        logger.error(f"Failed to list haikus: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch haikus"
        )

@router.get("/analytics", response_model=AdminStatsResponse)
async def get_analytics(user_id: str = Depends(check_admin_role)):
    """Get platform analytics (admin only)."""
    from db.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        # Get platform stats view
        stats_response = supabase.table("platform_stats").select(
            "*"
        ).execute()
        
        if stats_response.data:
            stats = stats_response.data[0]
            return AdminStatsResponse(
                total_users=stats.get("total_users", 0),
                total_haikus=stats.get("total_haikus", 0),
                avg_intensity_score=stats.get("avg_intensity_score", 0.0),
                most_common_emotion="unknown"  # Would need additional query
            )
        
        return AdminStatsResponse(
            total_users=0,
            total_haikus=0,
            avg_intensity_score=0.0,
            most_common_emotion="unknown"
        )
    
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analytics"
        )
