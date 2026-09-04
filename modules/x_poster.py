"""
X / Twitter Poster Module

Posts content directly to @AdrianJordan_io using Tweepy.
Supports single tweets, thread posting, and media attachments.
"""

import os
import time
from typing import Optional, List
from datetime import datetime, timezone

import tweepy

from core.config import (
    TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TARGET_HANDLE, log
)


class XPoster:
    """Posts content directly to X (Twitter) for @AdrianJordan_io."""

    def __init__(self):
        self.auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_SECRET,
        )
        self.api = tweepy.API(self.auth)
        self.client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
        )
        self.target_handle = TARGET_HANDLE

    def verify_credentials(self) -> bool:
        """Verify we can authenticate to X."""
        try:
            user = self.api.verify_credentials()
            log.info(f"XPoster: Authenticated as @{user.screen_name}")
            return True
        except Exception as exc:
            log.error(f"XPoster: Auth failed: {exc}")
            return False

    def post_tweet(self, text: str) -> Optional[object]:
        """
        Post a single tweet to @AdrianJordan_io.

        Args:
            text: The tweet text (max 280 chars)

        Returns:
            Tweepy Tweet object or None on failure
        """
        if len(text) > 280:
            log.warning(f"XPoster: Tweet too long ({len(text)} chars), truncating")
            text = text[:277] + "..."

        try:
            # Verify auth first
            if not self.verify_credentials():
                log.error("XPoster: Cannot post — authentication failed")
                return None

            status = self.api.update_status(status=text)
            log.info(f"XPoster: Posted tweet ID {status.id} — '{text[:60]}...'")
            return status

        except tweepy.TweepyException as exc:
            log.error(f"XPoster: Failed to post: {exc}")
            return None

    def post_thread(self, texts: List[str]) -> Optional[List[object]]:
        """
        Post a thread of tweets.

        Args:
            texts: List of tweet texts

        Returns:
            List of Status objects or None on failure
        """
        if not texts:
            return None

        statuses = []
        try:
            # Post first tweet
            first = self.api.update_status(status=texts[0])
            statuses.append(first)
            prev_id = first.id

            # Reply to post subsequent tweets
            for text in texts[1:]:
                # Keep replies under 280 chars
                remaining = 280 - 40  # ~40 chars for "@handle RT:" overhead
                if len(text) > remaining:
                    text = text[:remaining-3] + "..."

                status = self.api.update_status(
                    status=text,
                    in_reply_to_status_id=prev_id,
                    auto_populate_reply_metadata=True,
                )
                statuses.append(status)
                prev_id = status.id
                time.sleep(1)  # Brief pause between tweets

            log.info(f"XPoster: Posted thread of {len(statuses)} tweets")
            return statuses

        except tweepy.TweepyException as exc:
            log.error(f"XPoster: Thread failed: {exc}")
            return statuses if statuses else None

    def post_draft(self, draft_text: str, credit_line: str = "") -> Optional[object]:
        """
        Convenience method: format and post a single draft.

        Args:
            draft_text: The draft text
            credit_line: Credit attribution line

        Returns:
            Tweet object or None
        """
        # Build the final post
        post_text = draft_text
        if credit_line:
            post_text = f"{draft_text}\n\n{credit_line.strip()}"

        # Truncate to 280
        if len(post_text) > 280:
            post_text = post_text[:277] + "..."

        return self.post_tweet(post_text)

    def post_drafts(self, drafts, prefer_urgency: bool = True) -> List[object]:
        """
        Post multiple drafts. Returns list of results.

        Args:
            drafts: List of DraftPost objects
            prefer_urgency: Whether to pick option_1 (most impactful)

        Returns:
            List of posted Tweet objects
        """
        results = []
        for draft in drafts:
            text = draft.option_1 if prefer_urgency else draft.option_2 or draft.option_1
            credit = draft.credit_line
            result = self.post_draft(text, credit)
            if result:
                results.append(result)
            time.sleep(2)  # Pause between posts
        return results

    def delete_tweet(self, tweet_id: int) -> bool:
        """Delete a tweet by ID."""
        try:
            self.api.destroy_status(tweet_id)
            log.info(f"XPoster: Deleted tweet {tweet_id}")
            return True
        except Exception as exc:
            log.error(f"XPoster: Delete failed: {exc}")
            return False


# Convenience function
def post_to_x(text: str) -> Optional:
    """Quick post to X."""
    poster = XPoster()
    return poster.post_tweet(text)
