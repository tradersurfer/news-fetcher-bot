"""
Scheduler & Main Orchestrator — fetches, processes, posts.
Google Search is PRIMARY; X profiles and SEC EDGAR are supplementary.
"""

import time
import schedule
from datetime import datetime, timezone
from typing import List

from core.config import FETCH_INTERVAL_MINUTES, log, mark_seen, prune_seen
from sources.x_profiles import X_PROFILES
from modules.x_scraper import fetch_x_profiles
from modules.google_search import GoogleAdvancedSearch
from modules.sec_edgar import SECEdgarFetcher
from modules.ai_processor import AIContentProcessor
from modules.x_poster import XPoster

class NewsFetcherBot:
    def __init__(self):
        self.ai = AIContentProcessor()
        self.poster = XPoster()
        self.sec = SECEdgarFetcher()
        self.google = GoogleAdvancedSearch()
        self.running = False

    def run_cycle(self):
        log.info("=" * 60)
        log.info(f"NewsFetcherBot: Cycle at {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
        log.info("=" * 60)

        all_stories = []

        # PRIMARY: Google Search
        log.info("── Step 1: Google Search (PRIMARY) ──")
        try:
            stories = self.google.search_bitcoin_news(num_per_query=5)
            for s in stories:
                if not self._is_duplicate(s):
                    all_stories.append(s)
            log.info(f"Google → {len(stories)} stories")
        except Exception as exc:
            log.warning(f"Google error: {exc}")

        # SECONDARY: X profiles
        log.info("── Step 2: X Profiles ──")
        try:
            stories = fetch_x_profiles(X_PROFILES, max_results=20)
            for s in stories:
                if not self._is_duplicate(s):
                    all_stories.append(s)
            log.info(f"X profiles → {len(stories)} stories")
        except Exception as exc:
            log.warning(f"X error: {exc}")

        # SECONDARY: SEC EDGAR
        log.info("── Step 3: SEC EDGAR ──")
        try:
            stories = self.sec.get_bitcoin_relevant_filings()
            for s in stories:
                if not self._is_duplicate(s):
                    all_stories.append(s)
            log.info(f"SEC EDGAR → {len(stories)} filings")
        except Exception as exc:
            log.warning(f"SEC error: {exc}")

        # AI PROCESSING
        log.info(f"── Step 4: AI Processing ({len(all_stories)} stories) ──")
        drafts = []
        for s in all_stories:
            if self._is_duplicate(s):
                continue
            draft = self.ai.generate_drafts(s)
            if draft:
                drafts.append(draft)
                mark_seen(s.title, s.source)
        log.info(f"AI → {len(drafts)} drafts")

        # POST TO X
        if drafts:
            log.info(f"── Step 5: Posting to @{self.poster.target_handle} ──")
            self.poster.post_drafts(drafts, prefer_urgency=True)
            log.info(f"Posted {len(drafts)} drafts")
        else:
            log.info("── No new stories to post ──")

        prune_seen()
        log.info(f"Cycle complete. {len(all_stories)} stories, {len(drafts)} posted.")
        log.info("=" * 60)

    def _is_duplicate(self, story) -> bool:
        from core.config import is_duplicate
        return is_duplicate(story.title, story.source)

    def start(self):
        self.running = True
        log.info(f"NewsFetcherBot: Every {FETCH_INTERVAL_MINUTES} min")
        self.run_cycle()
        schedule.every(FETCH_INTERVAL_MINUTES).minutes.do(self.run_cycle)
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False
        log.info("Bot stopped.")
