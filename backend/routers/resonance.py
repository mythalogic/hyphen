"""Resonance routes."""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.schemas import ResonanceMatchResponse
from middleware import get_current_user
from services.feed_service import get_discovery_users
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/my-matches", response_model=List[ResonanceMatchResponse])
async def get_my_matches(
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user)
):
    """Get users most resonant with current user."""
    try:
        users = await get_discovery_users(user_id, limit)
        
        return [
            ResonanceMatchResponse(
                user_id=user["id"],
                username=user["username"],
                display_name=user["display_name"],
                resonance_score=user["resonance_score"],
                identity_haiku=user["identity_haiku"],
                primary_emotion=None
            )
            for user in users
        ]
    
    except Exception as e:
        logger.error(f"Failed to get matches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch matches"
        )

@router.get("/score/{other_user_id}")
async def get_resonance_score(
    other_user_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get resonance score with another user."""
    from db.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        # Query resonances table (handle bidirectional)
        response = supabase.table("resonances").select(
            "resonance_score"
        ).or_(
            f"user_a.eq.{min(user_id, other_user_id)},user_b.eq.{max(user_id, other_user_id)}"
        ).execute()
        
        if not response.data:
            return {"resonance_score": None}
        
        return {"resonance_score": response.data[0]["resonance_score"]}
    
    except Exception as e:
        logger.error(f"Failed to get resonance score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch resonance score"
        )
