"""AI service for haiku emotional analysis."""
import json
import logging
import asyncio
from anthropic import Anthropic
from config import settings

logger = logging.getLogger(__name__)

client = Anthropic()

async def analyze_haiku(haiku_id: str, haiku_text: str, user_id: str) -> dict:
    """
    Analyze haiku with Claude and store emotional profile in database.
    
    This is meant to be called as an async background task.
    It calls Claude, then stores the result in emotional_profiles table.
    """
    from db.database import get_supabase
    import uuid
    from datetime import datetime
    
    logger.info(f"Starting AI analysis for haiku {haiku_id}")
    
    prompt = f"""You are an emotional intelligence engine. Analyse the following haiku and return a JSON object only — no preamble, no markdown, no explanation.

Haiku:
{haiku_text}

Return this exact JSON structure:
{{
  "tone_tags": ["<tag1>", "<tag2>", "<tag3>"],
  "primary_emotion": "<single dominant emotion>",
  "intensity_score": <float between 0.0 and 1.0>,
  "resonance_vector": [<128 float values between -1.0 and 1.0>]
}}

Rules:
- tone_tags must be single lowercase English words (3-5 tags)
- primary_emotion must be one of the tone_tags
- intensity_score must be between 0.0 and 1.0
- resonance_vector must have exactly 128 values
- Return only valid JSON. Nothing else."""

    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Parse JSON response
        response_text = response.content[0].text
        result = json.loads(response_text)
        
        # Validate response structure
        required_fields = ["tone_tags", "primary_emotion", "intensity_score", "resonance_vector"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate resonance_vector length
        if len(result["resonance_vector"]) != 128:
            logger.warning(f"Resonance vector length is {len(result['resonance_vector'])}, expected 128. Padding/truncating...")
            if len(result["resonance_vector"]) < 128:
                # Pad with zeros
                result["resonance_vector"].extend([0.0] * (128 - len(result["resonance_vector"])))
            else:
                # Truncate
                result["resonance_vector"] = result["resonance_vector"][:128]
        
        # Store emotional profile in database
        supabase = get_supabase()
        profile_id = str(uuid.uuid4())
        
        profile_data = {
            "id": profile_id,
            "haiku_id": haiku_id,
            "user_id": user_id,
            "tone_tags": result["tone_tags"],
            "primary_emotion": result["primary_emotion"],
            "intensity_score": result["intensity_score"],
            "resonance_embedding": result["resonance_vector"],
            "raw_ai_response": result,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("emotional_profiles").insert(profile_data).execute()
        
        if not response.data:
            raise ValueError("Failed to store emotional profile")
        
        logger.info(f"Successfully analyzed haiku {haiku_id}: {result['primary_emotion']}")
        
        # Trigger resonance computation in background
        from services.feed_service import compute_user_resonances
        import asyncio
        asyncio.create_task(compute_user_resonances(user_id))
        
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response as JSON: {e}")
        raise ValueError("AI service returned invalid JSON")
    except Exception as e:
        logger.error(f"AI analysis failed for haiku {haiku_id}: {e}")
        raise

def create_embedding_from_vector(vector: list) -> list:
    """
    Convert a resonance vector to embedding format.
    Used for similarity calculations.
    """
    if len(vector) != 128:
        raise ValueError(f"Vector must have exactly 128 values, got {len(vector)}")
    return vector
