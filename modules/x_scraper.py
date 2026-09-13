"""
X Profile Scraper Module
Fetches BTC-relevant posts from specified X profiles via Tweepy API v2.
Google Search is the PRIMARY news source; X profiles are secondary.
"""

import tweepy
from typing import List, Optional
from datetime import datetime, timezone

from core.config import (
    TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, log, RawStory, _story_hash
)

BTC_KEYWORDS = [
    "bitcoin", "btc", "satoshi", "lightning", "sats", "etf", "coinbase",
    "microstrategy", "strategy", "blackrock", "sec", "treasury", "crypto",
    "stablecoin", "halving", "mining", "blockchain", "nakamoto", "saylor",
    "digital asset", "spot etf", "bitcoin etf", "hash rate",
]

def _is_btc_relevant(text: str) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in BTC_KEYWORDS)

class XProfileScraper:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
        )

    def fetch_profile_tweets(self, username: str, max_results: int = 10) -> List[RawStory]:
        stories = []
        try:
            user = self.client.get_user(username=username)
            if not user.data:
                return []
            tweets = self.client.get_users_tweets(
                id=user.data.id, max_results=max_results,
                tweet_fields=["created_at"], exclude=["retweets"],
            )
            if not tweets.data:
                return []
            for tweet in tweets.data:
                text = tweet.data.get("full_text") or tweet.data.get("text", "")
                if not text or len(text.strip()) < 10 or not _is_btc_relevant(text):
                    continue
                created_at = tweet.data.get("created_at")
                created_at = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
                stories.append(RawStory(
                    id=_story_hash(text, f"twitter:{username}"),
                    title=text, url=f"https://x.com/{username}/status/{tweet.data.get('id', '')}",
                    source=username, source_type="twitter", posted_at=created_at,
                ))
        except Exception as exc:
            log.warning(f"XProfileScraper: @{username} failed: {exc}")
        return stories

    def fetch_multiple_profiles(self, usernames: List[str], max_results: int = 10) -> List[RawStory]:
        all_stories = []
        for username in usernames:
            all_stories.extend(self.fetch_profile_tweets(username, max_results))
        log.info(f"XProfileScraper: {len(all_stories)} stories from {len(usernames)} profiles")
        return all_stories

def fetch_x_profiles(usernames: List[str], max_results: int = 10) -> List[RawStory]:
    return XProfileScraper().fetch_multiple_profiles(usernames, max_results)
