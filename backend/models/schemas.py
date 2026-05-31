"""Pydantic models for API requests/responses."""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Auth schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=30)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    username: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

# Haiku schemas
class HaikuLineRequest(BaseModel):
    line: str = Field(..., max_length=100)

class HaikuSubmitRequest(BaseModel):
    line1: str
    line2: str
    line3: str
    
    @validator('line1', 'line2', 'line3')
    def validate_lines(cls, v):
        if not v or not v.strip():
            raise ValueError('Line cannot be empty')
        return v.strip()

class HaikuResponse(BaseModel):
    id: str
    user_id: str
    line1: str
    line2: str
    line3: str
    full_text: str
    syllable_counts: List[int]
    is_identity_haiku: bool
    created_at: datetime

class SyllableCheckResponse(BaseModel):
    line: str
    syllable_count: int
    target: int
    is_valid: bool

# Emotional Profile schemas
class ToneTag(BaseModel):
    tag: str
    category: Optional[str]

class EmotionalProfileResponse(BaseModel):
    id: str
    haiku_id: str
    user_id: str
    tone_tags: List[str]
    primary_emotion: str
    intensity_score: float
    created_at: datetime

# Profile schemas
class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileResponse(BaseModel):
    id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio_haiku_id: Optional[str]
    created_at: datetime

# Feed schemas
class FeedHaikuResponse(BaseModel):
    id: str
    user_id: str
    haiku_id: str
    line1: str
    line2: str
    line3: str
    full_text: str
    username: str
    primary_emotion: Optional[str]
    resonance_score: Optional[float]
    reaction_count: int
    published_at: datetime

class ReactionRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=24)

# Resonance schemas
class ResonanceMatchResponse(BaseModel):
    user_id: str
    username: str
    display_name: Optional[str]
    resonance_score: float
    identity_haiku: Optional[str]
    primary_emotion: Optional[str]

# Admin schemas
class AdminStatsResponse(BaseModel):
    total_users: int
    total_haikus: int
    avg_intensity_score: float
    most_common_emotion: str

# Error schemas
class ErrorResponse(BaseModel):
    error: str
    code: str
