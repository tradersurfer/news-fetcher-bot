"""
SEC EDGAR Fetcher Module

Searches SEC EDGAR for recent filings (10-K, 10-Q, 8-K, etc.)
that mention Bitcoin, digital assets, or cryptocurrency.
Uses the SEC's free EDGAR full-text search API.
"""

import os
import json
import time
import requests
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta

from core.config import (
    SEC_CIK_NUMBERS, log, RawStory, _story_hash
)

# ─────────────────────────────────────────────
# SEC EDGAR CONFIG
# ─────────────────────────────────────────────

SEC_BASE_URL = "https://efts.sec.gov/LATEST/search-index?q="
SEC_FULLTEXT_URL = "https://efts.sec.gov/LATEST/search-index?q="
SEC_FILINGS_URL = "https://data.sec.gov/submissions/CIK"

# EDGAR full-text search API endpoint
SEC_ETF_SEARCH = "https://efts.sec.gov/LATEST/search-index"
SEC_EFTS_API = "https://efts.sec.gov/LATEST/search-index?q=%s&dateRange=custom&startdt=%s&enddt=%s&forms=%s"

# More reliable endpoint
SEC_ENTITY_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
SEC_FTS_API = "https://efts.sec.gov/LATEST/search-index?q=%s&forms=%s"


class SECEdgarFetcher:
    """Fetches SEC filings related to Bitcoin/crypto companies."""

    def __init__(self):
        self.headers = {
            "User-Agent": "BitcoinNewsBot/1.0 (adrian.jordan@adrianjordan.io)",
            "Accept-Encoding": "gzip, deflate",
            "Host": "efts.sec.gov",
        }
        self.seen_filings: set = set()

    def search_sec_filings(
        self,
        query: str = "bitcoin OR cryptocurrency OR digital asset",
        forms: str = "10-K,10-Q,8-K",
        date_from: str = None,
        date_to: str = None,
        ciks: List[str] = None,
        results_per_page: int = 20
    ) -> List[dict]:
        """
        Search SEC EDGAR full-text search for filings.

        Args:
            query: Search terms (default: bitcoin/crypto terms)
            forms: Comma-separated SEC forms to search
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            ciks: List of CIK numbers to filter by
            results_per_page: Max results to return

        Returns:
            List of filing dicts
        """
        filings = []

        try:
            # Build the query
            search_query = query
            if ciks:
                for cik in ciks:
                    search_query += f" CIK{cik.strip()}"

            # Construct EDGAR full-text search URL
            url = "https://efts.sec.gov/LATEST/search-index"
            params = {
                "q": search_query,
                "forms": forms,
                "dateRange": "custom",
                "startdt": date_from or self._get_date_days_ago(7),
                "enddt": date_to or self._get_today(),
                "hits": results_per_page,
            }

            resp = requests.get(
                "https://efts.sec.gov/LATEST/search-index",
                params=params,
                headers=self.headers,
                timeout=15,
            )

            if resp.status_code == 404:
                # Try alternate endpoint
                resp = self._search_alternate(query, forms, date_from, date_to, results_per_page)
            elif resp.status_code != 200:
                log.warning(f"SEC EDGAR search returned HTTP {resp.status_code}")
                return []

            data = resp.json()
            for hit in data.get("hits", {}).get("hits", []):
                filing = hit.get("_source", {})
                filings.append({
                    "id": filing.get("accession_number", ""),
                    "title": filing.get("display_names", [""])[0] if filing.get("display_names") else filing.get("name", ""),
                    "form": filing.get("form", ""),
                    "filing_date": filing.get("filing_date", ""),
                    "company": filing.get("name", ""),
                    "cik": filing.get("cik", ""),
                    "url": filing.get("pdf_url", "") or filing.get("accession_number", ""),
                    "abstract": filing.get("abstract", "")[:300],
                    "filed_by": filing.get("filed_by", ""),
                })

            log.info(f"SEC EDGAR: {len(filings)} filings found for query: '{query[:50]}'")

        except Exception as exc:
            log.warning(f"SEC EDGAR search failed: {exc}")
            # Try alternate approach
            filings = self._search_alternate(query, forms, date_from, date_to, results_per_page)

        return filings

    def _search_alternate(
        self, query: str, forms: str, date_from: str, date_to: str, results_per_page: int
    ) -> List[dict]:
        """Fallback search method using EDGAR browse API."""
        filings = []
        try:
            # Try the edgar_search endpoint
            url = f"https://efts.sec.gov/LATEST/search-index?q={query}&forms={forms}"
            params = {
                "dateRange": "custom",
                "startdt": date_from or self._get_date_days_ago(7),
                "enddt": date_to or self._get_today(),
                "hits": results_per_page,
            }
            resp = requests.get(url, params=params, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for hit in data.get("hits", {}).get("hits", []):
                    filing = hit.get("_source", {})
                    filings.append(filing)
        except Exception as exc:
            log.warning(f"SEC alternate search failed: {exc}")
        return filings

    def search_cik_company_filings(self, cik: str, forms: str = "10-K,10-Q,8-K") -> List[dict]:
        """
        Get filings for a specific company by CIK number.
        """
        filings = []
        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                recent = data.get("filings", {}).get("recent", {})
                form_list = forms.split(",")

                for i, form in enumerate(recent.get("form", [])):
                    if form in form_list:
                        filings.append({
                            "id": recent.get("accessionNumber", [""])[i] if recent.get("accessionNumber") else "",
                            "form": form,
                            "filing_date": recent.get("filingDate", [""])[i] if recent.get("filingDate") else "",
                            "title": recent.get("primaryDocDescription", [""])[i] if recent.get("primaryDocDescription") else "",
                            "company": data.get("name", ""),
                            "cik": cik,
                            "url": recent.get("primaryDocument", [""])[i] if recent.get("primaryDocument") else "",
                        })

                log.info(f"SEC EDGAR CIK {cik}: {len(filings)} recent filings found")
        except Exception as exc:
            log.warning(f"SEC CIK {cik} search failed: {exc}")

        return filings

    def get_bitcoin_relevant_filings(
        self,
        date_from: str = None,
        ciks: List[str] = None,
    ) -> List[RawStory]:
        """
        Main method: Get all Bitcoin/crypto relevant SEC filings.

        Args:
            date_from: Start date for filings (defaults to 7 days ago)
            ciks: List of CIK numbers to search (defaults to configured SEC_CIK_NUMBERS)

        Returns:
            List of RawStory objects
        """
        all_stories = []
        seen_ids: set = set()

        effective_ciks = ciks or SEC_CIK_NUMBERS
        date_from = date_from or self._get_date_days_ago(7)

        # Search general Bitcoin/crypto filings
        filings = self.search_sec_filings(
            query="bitcoin OR cryptocurrency OR digital asset OR blockchain",
            forms="10-K,10-Q,8-K",
            date_from=date_from,
            results_per_page=20,
        )

        for filing in filings:
            title = filing.get("title", filing.get("company", ""))
            form = filing.get("form", "")
            filing_id = filing.get("id", "")

            if not title or filing_id in seen_ids:
                continue
            seen_ids.add(filing_id)

            # Check for BTC keywords
            combined = f"{title} {filing.get('abstract', '')}".lower()
            if not any(kw in combined for kw in ["bitcoin", "btc", "cryptocurrency", "digital asset", "blockchain"]):
                continue

            story = RawStory(
                id=_story_hash(title, f"sec:{form}"),
                title=f"[{form}] {title}",
                url=filing.get("url", ""),
                source="SEC EDGAR",
                source_type="sec",
                posted_at=filing.get("filing_date", ""),
            )
            all_stories.append(story)

        # Also search specific CIKs
        for cik in effective_ciks:
            cik_filings = self.search_cik_company_filings(cik)
            for filing in cik_filings:
                filing_id = filing.get("id", "")
                if filing_id in seen_ids:
                    continue
                seen_ids.add(filing_id)

                story = RawStory(
                    id=_story_hash(filing.get("title", ""), f"sec:{cik}"),
                    title=f"[{filing.get('form', '')}] {filing.get('title', '')}",
                    url=filing.get("url", ""),
                    source=f"SEC EDGAR ({filing.get('company', 'Unknown')})",
                    source_type="sec",
                    posted_at=filing.get("filing_date", ""),
                )
                all_stories.append(story)

        log.info(f"SEC EDGAR: Total {len(all_stories)} Bitcoin-relevant filings found")
        return all_stories

    @staticmethod
    def _get_today() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @staticmethod
    def _get_date_days_ago(days: int) -> str:
        return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")


# Convenience function
def fetch_sec_filings(ciks: List[str] = None) -> List[RawStory]:
    """Fetch Bitcoin-relevant SEC filings."""
    fetcher = SECEdgarFetcher()
    return fetcher.get_bitcoin_relevant_filings(ciks=ciks)
