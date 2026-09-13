"""
Google Advanced Search Module — PRIMARY news source
Uses Google Custom Search API (with Serper fallback) to find Bitcoin news.
"""

import os
import requests
from typing import List, Optional
from datetime import datetime, timezone

from core.config import GOOGLE_API_KEY, GOOGLE_CX, log, RawStory, _story_hash

BTC_KEYWORDS = ["bitcoin", "btc", "satoshi", "lightning", "etf", "coinbase",
    "microstrategy", "strategy", "blackrock", "sec", "treasury", "crypto",
    "stablecoin", "halving", "mining", "blockchain", "digital asset",
    "spot etf", "bitcoin etf", "hash rate", "nakamoto", "saylor",
]

BITCOIN_QUERIES = [
    "bitcoin news today",
    "BTC price surge crash rally",
    "bitcoin ETF approval filing",
    "microstrategy strategy bitcoin treasury",
    "SEC bitcoin ETF decision",
    "bitcoin halving 2026",
    "BlackRock bitcoin IBIT",
    "Fidelity bitcoin FBTC",
    "ARK 21Shares bitcoin ETF",
    "SEC cryptocurrency regulation",
    "CFTC bitcoin",
    "treasury digital asset policy",
    "bitcoin network hash rate",
    "bitcoin lightning network",
    "bitcoin mining difficulty",
]

def _is_btc_relevant(text: str) -> bool:
    lowered = f"{text}".lower()
    return any(kw in lowered for kw in BTC_KEYWORDS)

class GoogleAdvancedSearch:
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        self.cx = GOOGLE_CX

    def search_google_api(self, query: str, num: int = 5) -> List[dict]:
        if not self.api_key or not self.cx:
            return []
        results = []
        try:
            resp = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": self.api_key, "cx": self.cx, "q": query, "num": min(num, 10)},
                timeout=10,
            )
            resp.raise_for_status()
            for item in resp.json().get("items", []):
                results.append({"title": item.get("title",""), "link": item.get("link",""), "snippet": item.get("snippet","")})
        except Exception as exc:
            log.warning(f"GoogleAPI: {exc}")
        return results

    def search_with_serper(self, query: str, num: int = 5) -> List[dict]:
        try:
            from serper import Serper
            client = Serper(api_key=os.getenv("GOOGLE_API_KEY",""))
            response = client.search(query, num_results=num)
            return [{"title": i.get("title",""), "link": i.get("link",""), "snippet": i.get("snippet","")}
                    for i in response.get("results", [])]
        except Exception:
            return []

    def search_bitcoin_news(self, num_per_query: int = 5) -> List[RawStory]:
        all_stories = []
        seen_ids = set()
        use_api = bool(self.api_key and self.cx)
        for query in BITCOIN_QUERIES:
            results = self.search_google_api(query, num_per_query) if use_api else []
            if not results:
                results = self.search_with_serper(query, num_per_query)
            for item in results:
                title = item.get("title","").strip()
                if not title or len(title) < 10:
                    continue
                combined = f"{title} {item.get('snippet','')}".lower()
                if not _is_btc_relevant(combined):
                    continue
                story_id = _story_hash(title, "google")
                if story_id in seen_ids:
                    continue
                seen_ids.add(story_id)
                all_stories.append(RawStory(
                    id=story_id, title=title, url=item.get("link",""),
                    source="Google Search", source_type="google",
                ))
        log.info(f"GoogleSearch: {len(all_stories)} BTC stories found")
        return all_stories
