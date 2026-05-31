"""Resonance scoring service for user similarity matching."""
import logging
from numpy import dot
from numpy.linalg import norm
from datetime import datetime

logger = logging.getLogger(__name__)

def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """
    Calculate cosine similarity between two vectors.
    Returns value between -1 and 1, typically 0 to 1 for embeddings.
    """
    try:
        a = [float(x) for x in vec_a]
        b = [float(x) for x in vec_b]
        
        norm_a = norm(a)
        norm_b = norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        similarity = dot(a, b) / (norm_a * norm_b)
        return float(similarity)
    except Exception as e:
        logger.error(f"Cosine similarity calculation failed: {e}")
        return 0.0

def recency_decay(hours_since_posted: float) -> float:
    """
    Calculate recency decay factor.
    Formula: 1 / (1 + hours_since_posted * 0.1)
    """
    try:
        if hours_since_posted < 0:
            return 1.0
        return 1.0 / (1.0 + (hours_since_posted * 0.1))
    except Exception as e:
        logger.error(f"Recency decay calculation failed: {e}")
        return 0.5

def calculate_feed_score(
    resonance_score: float,
    hours_since_posted: float,
    resonance_weight: float = 0.6,
    recency_weight: float = 0.4
) -> float:
    """
    Calculate final feed ranking score.
    Formula: (0.6 * resonance_score) + (0.4 * recency_decay)
    """
    try:
        decay = recency_decay(hours_since_posted)
        score = (resonance_weight * resonance_score) + (recency_weight * decay)
        return float(score)
    except Exception as e:
        logger.error(f"Feed score calculation failed: {e}")
        return 0.0

def compute_top_resonances(
    user_embedding: list,
    other_embeddings: list,
    top_k: int = 20
) -> list:
    """
    Compute top K resonant users for a given user.
    
    Args:
        user_embedding: The user's resonance vector
        other_embeddings: List of (user_id, embedding) tuples
        top_k: Number of top matches to return
    
    Returns:
        List of (user_id, resonance_score) tuples, sorted by score DESC
    """
    try:
        similarities = []
        for user_id, embedding in other_embeddings:
            score = cosine_similarity(user_embedding, embedding)
            similarities.append((user_id, score))
        
        # Sort by score descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    except Exception as e:
        logger.error(f"Resonance computation failed: {e}")
        return []
