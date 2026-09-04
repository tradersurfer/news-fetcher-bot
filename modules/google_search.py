"""
Google Advanced Search Module

Searches Google for Bitcoin news using the Google Custom Search API
and also provides a fallback to Serper (google-search-results package).
"""

import os
import re
import requests
from typing import List, Optional
from datetime import datetime, timezone

from core.config import (
    GOOGLE_API_KEY, GOOGLE_CX, log, RawStory, _story_hash
)

# ─────────────────────────────────────────────
# GOOGLE ADVANCED SEARCH
# ─────────────────────────────────────────────

BITCOIN_SEARCH_QUERIES = [
    # Main Bitcoin news
    "bitcoin news site:coindesk.com OR site:theblock.co OR site:cointelegraph.com",
    "bitcoin news today",
    "BTC price surge OR crash OR rally",
    "bitcoin ETF approval OR filing OR application",
    "microstrategy OR strategy bitcoin treasury",
    "sec bitcoin ETF decision",
    "bitcoin halving 2026",
    # Institutional / Corporate
    "BlackRock bitcoin IBIT",
    "Fidelity bitcoin FBTC",
    "ARK 21Shares bitcoin ETF",
    # Regulatory
    "SEC cryptocurrency regulation",
    "CFTC bitcoin",
    "treasury digital asset policy",
    # Technical / On-chain
    "bitcoin network hash rate",
    "bitcoin lightning network",
    "bitcoin mining difficulty",
]

BTC_KEYWORDS = [
    "bitcoin", "btc", "satoshi", "lightning", "sats", "etf",
    "coinbase", "microstrategy", "strategy", "blackrock", "sec",
    "treasury", "crypto", "stablecoin", "halving", "mining",
    "blockchain", "nakamoto", "saylor", "digital asset",
    "spot etf", "bitcoin etf", "hash rate",
]


class GoogleAdvancedSearch:
    """Performs advanced Google searches for Bitcoin news."""

    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        self.cx = GOOGLE_CX

    def search_google_api(self, query: str, num_results: int = 5) -> List[dict]:
        """
        Use Google Programmable Search API.
        Returns list of result dicts with title, link, snippet.
        """
        if not self.api_key or not self.cx:
            log.warning("Google API credentials not configured")
            return []

        results = []
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.cx,
                "q": query,
                "num": min(num_results, 10),
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })
            log.info(f"GoogleAPI: '{query[:50]}...' → {len(results)} results")
        except Exception as exc:
            log.warning(f"GoogleAPI search failed for '{query[:40]}': {exc}")
        return results

    def search_with_serper(self, query: str, num_results: int = 5) -> List[dict]:
        """
        Fallback: Use google-search-results (Serper) package.
        """
        try:
            from serper import Serper
            client = Serper(api_key=os.getenv("GOOGLE_API_KEY", ""))
            response = client.search(query, num_results=num_results)
            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })
            log.info(f"Serper: '{query[:50]}...' → {len(results)} results")
            return results
        except Exception as exc:
            log.warning(f"Serper search failed for '{query[:40]}': {exc}")
            return []

    def search_bitcoin_news(self, num_results_per_query: int = 5) -> List[RawStory]:
        """
        Run all Bitcoin search queries and return combined stories.
        Uses both Google API and Serper fallback.
        """
        all_stories = []
        seen_ids: set = set()

        # Try Google API first
        use_api = bool(self.api_key and self.cx)

        for query in BITCOIN_SEARCH_QUERIES:
            results = []
            if use_api:
                results = self.search_google_api(query, num_results_per_query)
            if not results:
                results = self.search_with_serper(query, num_results_per_query)

            for item in results:
                title = item.get("title", "").strip()
                link = item.get("link", "").strip()
                snippet = item.get("snippet", "").strip()

                if not title or len(title) < 10:
                    continue

                # Filter for BTC-relevant
                combined_text = f"{title} {snippet}".lower()
                if not any(kw in combined_text for kw in BTC_KEYWORDS):
                    continue

                story_id = _story_hash(title, "google")
                if story_id in seen_ids:
                    continue
                seen_ids.add(story_id)

                story = RawStory(
                    id=story_id,
                    title=title,
                    url=link,
                    source="Google Search",
                    source_type="google",
                )
                all_stories.append(story)

        log.info(f"GoogleSearch: Total {len(all_stories)} unique BTC stories found")
        return all_stories


# Convenience function
def search_google_bitcoin_news(usernames: List[str] = None, num_results_per_query: int = 5) -> List[RawStory]:
    """Search Google for Bitcoin news across multiple angles."""
    searcher = GoogleAdvancedSearch()
    stories = searcher.search_bitcoin_news(num_results_per_query)
    return stories
