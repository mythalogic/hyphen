"""Syllable counting service using pyphen."""
import logging
from pyphen import Pyphen

logger = logging.getLogger(__name__)

# Initialize hyphenator for English
dic = Pyphen(lang='en')

def count_syllables(text: str) -> int:
    """
    Count syllables in a line of text.
    Uses pyphen library for accurate syllable counting.
    """
    if not text or not text.strip():
        return 0
    
    text = text.strip().lower()
    # Use pyphen to hyphenate the text
    hyphenated = dic.inserted(text)
    
    # Count syllables by counting hyphens + 1
    syllable_count = hyphenated.count('-') + 1 if hyphenated else 1
    
    return syllable_count

def validate_haiku_syllables(line1: str, line2: str, line3: str) -> dict:
    """
    Validate that a haiku follows 5-7-5 syllable pattern.
    Returns validation result with details.
    """
    counts = [
        count_syllables(line1),
        count_syllables(line2),
        count_syllables(line3)
    ]
    
    target = [5, 7, 5]
    is_valid = counts == target
    
    return {
        "syllable_counts": counts,
        "target": target,
        "is_valid": is_valid,
        "errors": [
            f"Line {i+1}: {counts[i]} syllables (expected {target[i]})"
            for i in range(3)
            if counts[i] != target[i]
        ]
    }

def get_syllable_info(line: str, line_number: int) -> dict:
    """Get syllable info for a single line."""
    count = count_syllables(line)
    target = [5, 7, 5][line_number - 1] if 1 <= line_number <= 3 else 0
    
    return {
        "line": line,
        "syllable_count": count,
        "target": target,
        "is_valid": count == target
    }
