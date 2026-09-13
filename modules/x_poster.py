"""
X Poster — posts directly to @AdrianJordan_io via Tweepy.
"""

import tweepy
from typing import Optional, List

from core.config import (
    TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TARGET_HANDLE, log
)

class XPoster:
    def __init__(self):
        self.api = tweepy.API(tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET,
        ))
        self.client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY, consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_SECRET,
        )
        self.target_handle = TARGET_HANDLE

    def verify_credentials(self) -> bool:
        try:
            user = self.api.verify_credentials()
            log.info(f"XPoster: Authenticated as @{user.screen_name}")
            return True
        except Exception as exc:
            log.error(f"XPoster: Auth failed: {exc}")
            return False

    def post_tweet(self, text: str) -> Optional[object]:
        if len(text) > 280:
            text = text[:277] + "..."
        try:
            if not self.verify_credentials():
                return None
            status = self.api.update_status(status=text)
            log.info(f"XPoster: Posted {status.id}")
            return status
        except Exception as exc:
            log.error(f"XPoster: Failed: {exc}")
            return None

    def post_drafts(self, drafts, prefer_urgency: bool = True) -> List:
        results = []
        for d in drafts:
            text = d.option_1 if prefer_urgency else (d.option_2 or d.option_1)
            credit = d.credit_line
            post_text = f"{text}\n\n{credit.strip()}" if credit else text
            result = self.post_tweet(post_text)
            if result: results.append(result)
        return results
