"""Feed routes."""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.schemas import FeedHaikuResponse, ReactionRequest
from middleware import get_current_user
from services.feed_service import rank_feed_haikus, get_discovery_users
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("", response_model=List[dict])
async def get_feed(
    tab: str = Query("for-you", regex="^(for-you|new)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user)
):
    """Get paginated feed."""
    from db.database import get_supabase
    from datetime import datetime
    
    try:
        supabase = get_supabase()
        
        if tab == "for-you":
            # Rank by resonance + recency
            feed_items = await rank_feed_haikus(user_id, limit, offset)
        else:
            # Chronological order (new)
            response = supabase.table("feed_haikus").select(
                """
                id, user_id, haiku_id, published_at,
                haikus(line1, line2, line3, full_text),
                profiles(username, display_name),
                emotional_profiles(primary_emotion, intensity_score)
                """
            ).order("published_at", desc=True).range(offset, offset + limit - 1).execute()
            
            if not response.data:
                return []
            
            feed_items = response.data
        
        # Count reactions for each haiku
        enriched_items = []
        for item in feed_items:
            reactions_response = supabase.table("resonance_reactions").select(
                "id"
            ).eq("feed_haiku_id", item["id"]).execute()
            
            enriched_items.append({
                **item,
                "reaction_count": len(reactions_response.data) if reactions_response.data else 0
            })
        
        return enriched_items
    
    except Exception as e:
        logger.error(f"Failed to get feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch feed"
        )

@router.get("/discover", response_model=List[dict])
async def discover_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user)
):
    """Get discovery page: users ranked by resonance with current user."""
    try:
        users = await get_discovery_users(user_id, limit)
        return users[offset:offset + limit]
    except Exception as e:
        logger.error(f"Failed to get discovery users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch discovery"
        )

@router.post("/{feed_haiku_id}/react")
async def react_to_haiku(
    feed_haiku_id: str,
    request: ReactionRequest,
    user_id: str = Depends(get_current_user)
):
    """React to a haiku with a single word."""
    from db.database import get_supabase
    import uuid
    from datetime import datetime
    
    try:
        # Validate word is single word
        words = request.word.strip().split()
        if len(words) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reaction must be a single word"
            )
        
        supabase = get_supabase()
        
        # Check if user already reacted
        existing = supabase.table("resonance_reactions").select(
            "id"
        ).eq("feed_haiku_id", feed_haiku_id).eq("reactor_id", user_id).execute()
        
        if existing.data:
            # Update reaction
            supabase.table("resonance_reactions").update({
                "word": request.word
            }).eq("feed_haiku_id", feed_haiku_id).eq("reactor_id", user_id).execute()
        else:
            # Insert new reaction
            reaction_data = {
                "id": str(uuid.uuid4()),
                "feed_haiku_id": feed_haiku_id,
                "reactor_id": user_id,
                "word": request.word,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.table("resonance_reactions").insert(reaction_data).execute()
        
        return {"message": "Reacted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to react to haiku: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save reaction"
        )

@router.post("")
async def post_to_feed(
    haiku_id: str,
    user_id: str = Depends(get_current_user)
):
    """Post a haiku to the feed."""
    from db.database import get_supabase
    import uuid
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
        
        # Get emotional profile for the haiku
        profile_response = supabase.table("emotional_profiles").select(
            "id"
        ).eq("haiku_id", haiku_id).execute()
        
        emotional_profile_id = profile_response.data[0]["id"] if profile_response.data else None
        
        # Insert feed haiku
        feed_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "haiku_id": haiku_id,
            "emotional_profile_id": emotional_profile_id,
            "published_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("feed_haikus").insert(feed_data).execute()
        
        return {"message": "Posted to feed"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to post to feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to post to feed"
        )
