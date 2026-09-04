"""
X Profile Scraper Module

Fetches recent posts from specified X (Twitter) profiles using Tweepy.
User provides the list of profiles to monitor (e.g., @saylor, @APompliano, @lopp, etc.)
"""

import os
import tweepy
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from core.config import (
    TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, log, RawStory,
    parse_tweet_text, parse_tweet_timestamp, _story_hash
)

# ─────────────────────────────────────────────
# X PROFILE SCRAPER
# ─────────────────────────────────────────────

class XProfileScraper:
    """Scrapes recent posts from specified X profiles."""

    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
        )
        self.me = None

    def _get_client(self) -> tweepy.Client:
        return self.client

    def fetch_profile_tweets(self, username: str, max_results: int = 10) -> List[RawStory]:
        """
        Fetch recent tweets from a specific X profile.

        Args:
            username: X handle without @ (e.g., "saylor")
            max_results: Number of tweets to fetch (max 100 per API call)

        Returns:
            List of RawStory objects
        """
        stories = []
        try:
            # Fetch user ID first
            user = self.client.get_user(username=username)
            if not user.data:
                log.warning(f"XProfileScraper: Could not find user @{username}")
                return []

            user_id = user.data.id
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "entities"],
                exclude=["retweets"],
            )

            if not tweets.data:
                log.info(f"XProfileScraper: No tweets from @{username}")
                return []

            for tweet in tweets.data:
                text = parse_tweet_text(tweet.data)
                if not text or len(text.strip()) < 10:
                    continue

                # Only include BTC-relevant posts
                if not self._is_btc_relevant(text):
                    continue

                created_at = tweet.data.get("created_at")
                if created_at:
                    created_at = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)

                story = RawStory(
                    id=_story_hash(text, f"twitter:{username}"),
                    title=text,
                    url=f"https://x.com/{username}/status/{tweet.data.get('id', '')}",
                    source=username,
                    source_type="twitter",
                    posted_at=created_at,
                )
                stories.append(story)

            log.info(f"XProfileScraper: @{username} → {len(stories)} BTC-relevant tweets")

        except Exception as exc:
            log.warning(f"XProfileScraper: Failed to fetch @{username}: {exc}")

        return stories

    def fetch_multiple_profiles(self, usernames: List[str], max_results: int = 10) -> List[RawStory]:
        """Fetch from multiple X profiles."""
        all_stories = []
        for username in usernames:
            stories = self.fetch_profile_tweets(username, max_results)
            all_stories.extend(stories)
        log.info(f"XProfileScraper: Total {len(all_stories)} stories across {len(usernames)} profiles")
        return all_stories

    def _is_btc_relevant(self, text: str) -> bool:
        """Check if tweet text contains Bitcoin/crypto keywords."""
        btc_keywords = [
            "bitcoin", "btc", "satoshi", "lightning", "sats",
            "etf", "coinbase", "microstrategy", "strategy",
            "blackrock", "sec", "treasury", "crypto", "stablecoin",
            "halving", "mining", "blockchain", "web3", "defi",
            "nakamoto", "saylor", "michael saylor", "bitcoin treasury",
            "spot etf", "bitcoin etf", "digital asset",
        ]
        lowered = text.lower()
        return any(kw in lowered for kw in btc_keywords)


# Convenience function
def fetch_x_profiles(usernames: List[str], max_results: int = 10) -> List[RawStory]:
    """Fetch BTC-relevant tweets from a list of X profiles."""
    scraper = XProfileScraper()
    return scraper.fetch_multiple_profiles(usernames, max_results)
