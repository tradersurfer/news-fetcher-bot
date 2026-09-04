"""
Core module — re-exports for convenience imports.
"""
from core.config import (
    log, RawStory, DraftPost, mark_seen, is_duplicate,
    ANTHROPIC_API_KEY, TARGET_HANDLE, SEC_CIK_NUMBERS,
    FETCH_INTERVAL_MINUTES,
)

__all__ = [
    "log", "RawStory", "DraftPost", "mark_seen", "is_duplicate",
    "ANTHROPIC_API_KEY", "TARGET_HANDLE", "SEC_CIK_NUMBERS",
    "FETCH_INTERVAL_MINUTES",
]
