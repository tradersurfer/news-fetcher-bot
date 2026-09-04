"""
Scheduler & Main Orchestrator

Runs the full pipeline every N minutes:
1. Fetch from X profiles
2. Search Google for Bitcoin news
3. Search SEC EDGAR for filings
4. Process through AI (Claude)
5. Post to @AdrianJordan_io

Dedup engine prevents duplicate posts.
"""

import os
import time
import json
import schedule
from datetime import datetime, timezone
from typing import List

from core.config import (
    FETCH_INTERVAL_MINUTES, log, mark_seen, prune_seen, is_duplicate,
)
from sources.x_profiles import X_PROFILES
from modules.x_scraper import fetch_x_profiles
from modules.google_search import GoogleAdvancedSearch
from modules.sec_edgar import SECEdgarFetcher
from modules.ai_processor import AIContentProcessor
from modules.x_poster import XPoster


class NewsFetcherBot:
    """Main bot orchestrator — fetches, processes, and posts Bitcoin news."""

    def __init__(self):
        self.ai = AIContentProcessor()
        self.poster = XPoster()
        self.sec = SECEdgarFetcher()
        self.google = GoogleAdvancedSearch()
        self.running = False

    def run_cycle(self):
        """Execute one full fetch-process-post cycle."""
        log.info("=" * 60)
        log.info(f"NewsFetcherBot: Starting cycle at {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
        log.info("=" * 60)

        all_stories: List = []

        # ── 1. Fetch from X profiles ──
        log.info("── Step 1: Fetching from X profiles ──")
        try:
            twitter_stories = fetch_x_profiles(
                usernames=X_PROFILES,
                max_results=20,
            )
            for story in twitter_stories:
                if not is_duplicate(story.title, story.source):
                    all_stories.append(story)
            log.info(f"X profiles → {len(twitter_stories)} stories fetched")
        except Exception as exc:
            log.warning(f"X profile fetch error: {exc}")

        # ── 2. Search Google for Bitcoin news ──
        log.info("── Step 2: Searching Google ──")
        try:
            google_stories = self.google.search_bitcoin_news(num_results_per_query=5)
            for story in google_stories:
                if not is_duplicate(story.title, story.source):
                    all_stories.append(story)
            log.info(f"Google → {len(google_stories)} stories found")
        except Exception as exc:
            log.warning(f"Google search error: {exc}")

        # ── 3. Search SEC EDGAR for filings ──
        log.info("── Step 3: Searching SEC EDGAR ──")
        try:
            sec_stories = self.sec.get_bitcoin_relevant_filings()
            for story in sec_stories:
                if not is_duplicate(story.title, story.source):
                    all_stories.append(story)
            log.info(f"SEC EDGAR → {len(sec_stories)} filings found")
        except Exception as exc:
            log.warning(f"SEC EDGAR error: {exc}")

        # ── 4. Process through AI ──
        log.info(f"── Step 4: Processing {len(all_stories)} stories through AI ──")
        drafts = []
        for story in all_stories:
            if is_duplicate(story.title, story.source):
                continue
            draft = self.ai.generate_drafts(story)
            if draft:
                drafts.append(draft)
                mark_seen(story.title, story.source)

        log.info(f"AI Processing → {len(drafts)} drafts generated")

        # ── 5. Post to X ──
        if drafts:
            log.info(f"── Step 5: Posting {len(drafts)} drafts to @{self.poster.target_handle} ──")
            results = self.poster.post_drafts(drafts, prefer_urgency=True)
            posted_count = len([r for r in results if r is not None])
            log.info(f"Posted {posted_count}/{len(drafts)} drafts to X")
        else:
            log.info("── Step 5: No new stories to post ──")

        # ── Cleanup ──
        prune_seen()
        log.info(f"Cycle complete. Total stories processed: {len(all_stories)}")
        log.info("=" * 60)

    def start(self):
        """Start the scheduler loop."""
        self.running = True
        log.info(f"NewsFetcherBot: Starting — polling every {FETCH_INTERVAL_MINUTES} minutes")

        # Run immediately on start
        self.run_cycle()

        # Schedule recurring runs
        schedule.every(FETCH_INTERVAL_MINUTES).minutes.do(self.run_cycle)

        log.info("NewsFetcherBot: Scheduler running. Press Ctrl+C to stop.")
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        log.info("NewsFetcherBot: Stopped.")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    """Entry point for the bot."""
    bot = NewsFetcherBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.stop()
        log.info("Bot shut down gracefully.")


if __name__ == "__main__":
    main()
