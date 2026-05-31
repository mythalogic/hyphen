"""Resonance matching and feed ranking logic."""
import logging
from db.database import get_supabase
from services.resonance_service import cosine_similarity, calculate_feed_score, recency_decay
from datetime import datetime

logger = logging.getLogger(__name__)

async def compute_user_resonances(user_id: str):
    """
    Compute resonance scores between a user and all other users.
    
    Called after a user creates their emotional profile.
    Stores top 20 matches in resonances table.
    """
    supabase = get_supabase()
    
    try:
        # Get user's emotional profile
        user_profile_response = supabase.table("emotional_profiles").select(
            "resonance_embedding"
        ).eq("user_id", user_id).limit(1).execute()
        
        if not user_profile_response.data:
            logger.warning(f"No emotional profile found for user {user_id}")
            return
        
        user_embedding = user_profile_response.data[0]["resonance_embedding"]
        
        # Get all other users' emotional profiles
        other_profiles_response = supabase.table("emotional_profiles").select(
            "user_id, resonance_embedding"
        ).neq("user_id", user_id).execute()
        
        if not other_profiles_response.data:
            logger.info(f"No other users found for resonance matching")
            return
        
        # Compute resonance scores
        resonances = []
        for profile in other_profiles_response.data:
            other_user_id = profile["user_id"]
            other_embedding = profile["resonance_embedding"]
            
            score = cosine_similarity(user_embedding, other_embedding)
            resonances.append({
                "user_a": min(user_id, other_user_id),
                "user_b": max(user_id, other_user_id),
                "resonance_score": score
            })
        
        # Sort by score and take top 20
        resonances.sort(key=lambda x: x["resonance_score"], reverse=True)
        top_resonances = resonances[:20]
        
        # Insert or update in database
        for resonance in top_resonances:
            # Check if already exists
            existing = supabase.table("resonances").select("id").eq(
                "user_a", resonance["user_a"]
            ).eq("user_b", resonance["user_b"]).execute()
            
            if existing.data:
                # Update
                supabase.table("resonances").update({
                    "resonance_score": resonance["resonance_score"],
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("user_a", resonance["user_a"]).eq(
                    "user_b", resonance["user_b"]
                ).execute()
            else:
                # Insert
                supabase.table("resonances").insert(
                    resonance
                ).execute()
        
        logger.info(f"Computed resonances for user {user_id}: {len(top_resonances)} matches")
    
    except Exception as e:
        logger.error(f"Failed to compute resonances for user {user_id}: {e}")

async def rank_feed_haikus(user_id: str, limit: int = 20, offset: int = 0):
    """
    Rank feed haikus by resonance score + recency.
    
    Formula: final_score = (0.6 * resonance_score) + (0.4 * recency_decay)
    
    Returns list of ranked haiku posts.
    """
    supabase = get_supabase()
    
    try:
        # Get all feed haikus with user info and emotional profile
        feed_response = supabase.table("feed_haikus").select(
            """
            id, user_id, haiku_id, published_at,
            haikus(line1, line2, line3, full_text),
            profiles(username, display_name),
            emotional_profiles(primary_emotion, intensity_score)
            """
        ).order("published_at", desc=True).range(offset, offset + limit - 1).execute()
        
        if not feed_response.data:
            return []
        
        # Get user's resonance scores with each poster
        resonances = {}
        for item in feed_response.data:
            poster_id = item["user_id"]
            
            # Query resonance score (handle bidirectional query)
            res_response = supabase.table("resonances").select(
                "resonance_score"
            ).or_(
                f"user_a.eq.{min(user_id, poster_id)},user_b.eq.{max(user_id, poster_id)}"
            ).execute()
            
            if res_response.data:
                # Normalize to 0-1 range (cosine similarity is -1 to 1)
                raw_score = res_response.data[0]["resonance_score"]
                normalized_score = (raw_score + 1) / 2
            else:
                normalized_score = 0.5  # Default for unknown users
            
            resonances[poster_id] = normalized_score
        
        # Calculate feed scores and rank
        ranked_items = []
        now = datetime.utcnow()
        
        for item in feed_response.data:
            posted_at = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
            hours_since = (now - posted_at).total_seconds() / 3600
            
            resonance_score = resonances.get(item["user_id"], 0.5)
            final_score = calculate_feed_score(resonance_score, hours_since)
            
            item["resonance_score"] = resonance_score
            item["feed_score"] = final_score
            ranked_items.append(item)
        
        # Sort by final score
        ranked_items.sort(key=lambda x: x["feed_score"], reverse=True)
        
        return ranked_items
    
    except Exception as e:
        logger.error(f"Failed to rank feed haikus: {e}")
        return []

async def get_discovery_users(user_id: str, limit: int = 20):
    """
    Get users ranked by resonance with current user.
    Used for discovery tab.
    """
    supabase = get_supabase()
    
    try:
        # Get resonances for current user, ordered by score
        resonances_response = supabase.table("resonances").select(
            """
            user_a, user_b, resonance_score
            """
        ).or_(
            f"user_a.eq.{user_id},user_b.eq.{user_id}"
        ).order("resonance_score", desc=True).limit(limit).execute()
        
        if not resonances_response.data:
            return []
        
        # Extract other user IDs
        other_user_ids = []
        for res in resonances_response.data:
            if res["user_a"] == user_id:
                other_user_ids.append(res["user_b"])
            else:
                other_user_ids.append(res["user_a"])
        
        # Get user profiles and identity haikus
        discovery_users = []
        for i, other_id in enumerate(other_user_ids):
            profile_response = supabase.table("profiles").select(
                """
                id, username, display_name,
                haikus(line1, line2, line3)
                """
            ).eq("id", other_id).limit(1).execute()
            
            if profile_response.data:
                user_data = profile_response.data[0]
                resonance_score = resonances_response.data[i]["resonance_score"]
                
                # Get identity haiku
                identity_haiku = None
                if user_data.get("haikus"):
                    haiku = user_data["haikus"][0]
                    identity_haiku = f"{haiku['line1']}\n{haiku['line2']}\n{haiku['line3']}"
                
                discovery_users.append({
                    "id": user_data["id"],
                    "username": user_data["username"],
                    "display_name": user_data["display_name"],
                    "identity_haiku": identity_haiku,
                    "resonance_score": resonance_score
                })
        
        return discovery_users
    
    except Exception as e:
        logger.error(f"Failed to get discovery users: {e}")
        return []
