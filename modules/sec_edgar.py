"""
SEC EDGAR Fetcher — 10-K, 10-Q, 8-K filings mentioning Bitcoin/crypto.
"""

import requests
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from core.config import SEC_CIK_NUMBERS, log, RawStory, _story_hash

SEC_HEADERS = {"User-Agent": "BitcoinNewsBot/1.0 (adrian.jordan@adrianjordan.io)"}

class SECEdgarFetcher:
    def __init__(self):
        self.headers = SEC_HEADERS

    def search_sec_filings(self, query: str = "bitcoin OR cryptocurrency OR digital asset",
                           forms: str = "10-K,10-Q,8-K", date_from: str = None,
                           results_per_page: int = 20) -> List[dict]:
        filings = []
        try:
            params = {
                "q": query, "forms": forms,
                "dateRange": "custom",
                "startdt": date_from or self._days_ago(7),
                "enddt": self._today(),
                "hits": results_per_page,
            }
            resp = requests.get("https://efts.sec.gov/LATEST/search-index",
                                params=params, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for hit in data.get("hits", {}).get("hits", []):
                    f = hit.get("_source", {})
                    filings.append({"title": f.get("display_names", [""])[0] if f.get("display_names") else f.get("name",""),
                                    "form": f.get("form",""), "filing_date": f.get("filing_date",""),
                                    "url": f.get("pdf_url","") or f.get("accession_number",""),
                                    "company": f.get("name",""), "cik": f.get("cik",""),
                                    "abstract": f.get("abstract","")[:300]})
            log.info(f"SEC EDGAR: {len(filings)} filings")
        except Exception as exc:
            log.warning(f"SEC EDGAR: {exc}")
        return filings

    def get_bitcoin_relevant_filings(self) -> List[RawStory]:
        all_stories = []
        seen_ids = set()
        filings = self.search_sec_filings()
        for f in filings:
            title = f.get("title","")
            if not title or f.get("id","") in seen_ids:
                continue
            seen_ids.add(f.get("id",""))
            combined = f"{title} {f.get('abstract','')}".lower()
            if not any(kw in combined for kw in ["bitcoin","btc","cryptocurrency","digital asset","blockchain"]):
                continue
            all_stories.append(RawStory(
                id=_story_hash(title, f"sec:{f.get('form','')}"),
                title=f"[{f.get('form','')}] {title}",
                url=f.get("url",""), source="SEC EDGAR", source_type="sec",
                posted_at=f.get("filing_date",""),
            ))
        for cik in SEC_CIK_NUMBERS:
            cik_filings = self.search_cik_company_filings(cik)
            for f in cik_filings:
                if f.get("id","") in seen_ids:
                    continue
                seen_ids.add(f.get("id",""))
                all_stories.append(RawStory(
                    id=_story_hash(f.get("title",""), f"sec:{cik}"),
                    title=f"[{f.get('form','')}] {f.get('title','')}",
                    url=f.get("url",""), source=f"SEC EDGAR ({f.get('company','')})",
                    source_type="sec", posted_at=f.get("filing_date",""),
                ))
        log.info(f"SEC EDGAR: {len(all_stories)} Bitcoin-relevant filings")
        return all_stories

    def search_cik_company_filings(self, cik: str) -> List[dict]:
        filings = []
        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                recent = data.get("filings", {}).get("recent", {})
                for i, form in enumerate(recent.get("form", [])):
                    if form in ["10-K", "10-Q", "8-K"]:
                        filings.append({"id": recent.get("accessionNumber",[""])[i],
                                        "form": form, "title": recent.get("primaryDocDescription",[""])[i],
                                        "filing_date": recent.get("filingDate",[""])[i],
                                        "url": recent.get("primaryDocument",[""])[i],
                                        "company": data.get("name","")})
        except Exception as exc:
            log.warning(f"SEC CIK {cik}: {exc}")
        return filings

    @staticmethod
    def _today(): return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    @staticmethod
    def _days_ago(d): return (datetime.now(timezone.utc) - timedelta(days=d)).strftime("%Y-%m-%d")

def fetch_sec_filings() -> List[RawStory]:
    return SECEdgarFetcher().get_bitcoin_relevant_filings()
