"""
Bitcoin News Fetcher Bot — Core Configuration & Shared Utilities

All modules import from this file for shared constants and helpers.
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional, Set
from dataclasses import dataclass, field, asdict

from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bitcoin_fetcher")

# ─────────────────────────────────────────────
# CONFIG FROM ENV
# ─────────────────────────────────────────────

# AI
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# X / Twitter
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
TWITTER_API_KEY      = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET   = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET= os.getenv("TWITTER_ACCESS_SECRET", "")
TARGET_HANDLE        = os.getenv("TARGET_HANDLE", "AdrianJordan_io")

# Google Search
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CX      = os.getenv("GOOGLE_CX", "")

# Scheduler
FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", "5"))

# SEC EDGAR
SEC_CIK_NUMBERS = os.getenv("SEC_CIK_NUMBERS", "").split(",")
SEC_CIK_NUMBERS = [c.strip() for c in SEC_CIK_NUMBERS if c.strip()]

# Dedup
SEEN_STORIES_FILE = os.getenv("SEEN_STORIES_FILE", "seen_stories.json")
MIN_POST_GAP_SECONDS = int(os.getenv("MIN_POST_GAP_SECONDS", "300"))

# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────

@dataclass
class RawStory:
    """A story as fetched from any source before AI processing."""
    id:          str
    title:       str
    url:         str
    source:      str
    source_type: str = "unknown"  # twitter, google, sec, rss
    posted_at:   Optional[str]   = None
    fetched_at:  str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class DraftPost:
    """Three headline options produced by Claude, ready for review or posting."""
    story_id:   str
    raw_title:  str
    source:     str
    source_type: str = "unknown"
    option_1:   str = ""
    option_2:   str = ""
    option_3:   str = ""
    credit_line:str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ─────────────────────────────────────────────
# DEDUP ENGINE
# ─────────────────────────────────────────────

def _load_seen() -> Set[str]:
    if os.path.exists(SEEN_STORIES_FILE):
        try:
            with open(SEEN_STORIES_FILE) as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()

def _save_seen(seen: Set[str]) -> None:
    with open(SEEN_STORIES_FILE, "w") as f:
        json.dump(list(seen), f)

def _story_hash(title: str, source: str = "") -> str:
    return hashlib.md5(f"{source}:{title.strip().lower()}".encode()).hexdigest()

def is_duplicate(title: str, source: str = "") -> bool:
    seen = _load_seen()
    h = _story_hash(title, source)
    return h in seen

def mark_seen(title: str, source: str = "") -> None:
    seen = _load_seen()
    h = _story_hash(title, source)
    seen.add(h)
    _save_seen(seen)

def prune_seen(keep_days: int = 7) -> None:
    """Remove old entries from seen_stories.json to prevent unbounded growth."""
    if not os.path.exists(SEEN_STORIES_FILE):
        return
    with open(SEEN_STORIES_FILE) as f:
        seen = json.load(f)
    if len(seen) > 10000:
        # Keep only the last 5000
        with open(SEEN_STORIES_FILE, "w") as f:
            json.dump(seen[-5000:], f)
        log.info(f"Pruned seen_stories.json to {len(seen[-5000:])} entries")

# ─────────────────────────────────────────────
# X PROFILE SCRAPING HELPERS
# ─────────────────────────────────────────────

def parse_tweet_text(tweet: dict) -> Optional[str]:
    """Extract clean text from a tweet dict (handles extended tweets)."""
    # Handle extended retweets
    if "retweeted_status" in tweet:
        text = tweet["retweeted_status"].get("full_text") or tweet["retweeted_status"].get("text", "")
    else:
        text = tweet.get("full_text") or tweet.get("text", "")
    return text.strip() if text else None

def parse_tweet_timestamp(tweet: dict) -> Optional[str]:
    """Extract ISO timestamp from tweet."""
    created = tweet.get("created_at")
    if created:
        return created
    return None
