"""Haiku routes."""
from fastapi import APIRouter, HTTPException, status, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from models.schemas import HaikuSubmitRequest, HaikuResponse, SyllableCheckResponse
from services.syllable_service import count_syllables, validate_haiku_syllables
from services.ai_service import analyze_haiku as analyze_haiku_ai
from middleware import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/syllable-check")
async def check_syllables(line: str = Query(..., min_length=1)):
    """
    Check syllable count for a line in real-time.
    Called by frontend as user types each line.
    """
    try:
        syllable_count = count_syllables(line)
        return {
            "line": line,
            "syllable_count": syllable_count,
            "is_valid": syllable_count > 0
        }
    except Exception as e:
        logger.error(f"Syllable check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Failed to count syllables",
                "code": "SYLLABLE_CHECK_FAILED"
            }
        )

@router.post("", response_model=HaikuResponse)
async def submit_haiku(
    request: HaikuSubmitRequest,
    user_id: str = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Submit a new haiku.
    
    1. Validate syllable counts (5-7-5)
    2. Store haiku in database
    3. Trigger async AI analysis (in background)
    4. Return haiku response immediately
    """
    from db.database import get_supabase
    import uuid
    from datetime import datetime
    
    try:
        # Validate syllable counts
        validation = validate_haiku_syllables(request.line1, request.line2, request.line3)
        
        if not validation['is_valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid syllable pattern. Got {validation['syllable_counts']}, expected [5, 7, 5]"
            )
        
        # Get Supabase client
        supabase = get_supabase()
        
        # Generate UUID for haiku
        haiku_id = str(uuid.uuid4())
        
        # Insert haiku
        haiku_data = {
            "id": haiku_id,
            "user_id": user_id,
            "line1": request.line1.strip(),
            "line2": request.line2.strip(),
            "line3": request.line3.strip(),
            "syllable_counts": validation['syllable_counts'],
            "is_identity_haiku": False,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("haikus").insert(haiku_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store haiku"
            )
        
        # Trigger async AI analysis in background
        full_text = f"{request.line1}\n{request.line2}\n{request.line3}"
        background_tasks.add_task(analyze_haiku_ai, haiku_id, full_text, user_id)
        logger.info(f"Queued AI analysis for haiku {haiku_id}")
        
        haiku = response.data[0]
        
        return HaikuResponse(
            id=haiku["id"],
            user_id=haiku["user_id"],
            line1=haiku["line1"],
            line2=haiku["line2"],
            line3=haiku["line3"],
            full_text=haiku["full_text"],
            syllable_counts=haiku["syllable_counts"],
            is_identity_haiku=haiku["is_identity_haiku"],
            created_at=haiku["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Haiku submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit haiku"
        )

@router.get("/{haiku_id}", response_model=HaikuResponse)
async def get_haiku(haiku_id: str):
    """Get a haiku by ID."""
    # TODO: Implement haiku retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented"
    )

@router.delete("/{haiku_id}")
async def delete_haiku(
    haiku_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a haiku."""
    # TODO: Implement haiku deletion
    return {"message": "Haiku deleted"}

@router.get("/{haiku_id}/profile")
async def get_haiku_profile(haiku_id: str):
    """Get emotional profile for a haiku."""
    # TODO: Implement to return emotional profile
    # This endpoint is used for polling if AI analysis is pending
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented"
    )
