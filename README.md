# Bitcoin News Fetcher Bot v2.0

**Combined bot: Google Search (primary), X profiles, and SEC EDGAR — posts directly to @AdrianJordan_io.**

## Architecture

```
┌─────────────────────────────────────────────────┐
│           SOURCES (every 5 min, configurable)      │
│                                                    │
│  ┌──────────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Google Search│  │ X Profiles│  │ SEC EDGAR │  │
│  │  (PRIMARY)   │  │ (Secondary)│  │ (Secondary)│  │
│  └──────┬───────┘  └─────┬────┘  └─────┬─────┘  │
│         │                 │              │         │
│         └────────┬────────┴──────────────┘         │
│                  ↓                                  │
│          Dedup Engine (seen_stories.json)           │
│                  ↓                                  │
│          AI Processor (Claude)                      │
│          → 3 draft options per story                │
│                  ↓                                  │
│          X Poster (Tweepy)                          │
│          → Posts to @AdrianJordan_io               │
│                                                    │
└─────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Copy .env.template and fill in API keys
cp .env.template .env

# 2. Install deps
pip install -r requirements.txt

# 3. Test (runs cycle, no posting)
python main.py --test

# 4. Single cycle
python main.py --once

# 5. Continuous (default 5 min)
python main.py
python main.py --interval 10  # every 10 min
```

## API Keys Needed

| Service | Key | Where to get |
|---------|-----|-------------|
| **Anthropic** | `ANTHROPIC_API_KEY` | console.anthropic.com |
| **Twitter/X** | 5 tokens (see .env) | developer.x.com |
| **Google** | `GOOGLE_API_KEY` + `GOOGLE_CX` | Google Cloud Console |

## CLI Options

| Flag | Description |
|------|-------------|
| `--once` | Run one cycle and exit |
| `--test` | Single cycle (no posting) |
| `--interval N` | Polling interval (default: 5 min) |

## Sources

### Google Search (PRIMARY)
`modules/google_search.py` — Searches 16 Bitcoin-related queries via Google Custom Search API. This is the **primary** source because it catches breaking news fastest. X profiles and SEC filings are supplementary.

### X Profiles (SECONDARY)
`sources/x_profiles.py` — Monitors ~30 Bitcoin-specific X accounts including @saylor, @APompliano, @lopp, @coindesk, @BlackRock, and more. Edit this file to add/remove handles.

### SEC EDGAR (SECONDARY)
`modules/sec_edgar.py` — Searches 10-K, 10-Q, and 8-K filings mentioning Bitcoin/crypto. Configure `SEC_CIK_NUMBERS` in `.env`.

## X Profiles Included

- **Company/CEO**: @saylor, @Strategy, @Coinbase, @BlackRock, @Fidelity, @ARKInvest
- **News**: @coindesk, @TheBlock, @cointelegraph, @bitcoinmagazine
- **Lightning/Payments**: @geyserfund, @lnbits, @LightningNewsX, @utexo
- **Block/Jacks**: @blocks, @blockIR, @jack
- **Research**: @glxyresearch, @cryptovizart, @ODELLXYZ
- **Analysts**: @WatcherGuru, @coffeebreak_YT, @ZynxBTC (manual review)
- **Policy**: @SenWarren, @SenToomey, @SECGov, @CFTC, @USTreasury

## Brand Voice

- Direct, authoritative, no hashtags, under 280 chars
- Impact first, accuracy always
- Never uses: "supply shock", "what a time to be alive", "it's happening"

## Future Features

- [ ] Telegram channel notifications
- [ ] Webhook-triggered immediate posts
- [ ] Thread posting for longer analysis
- [ ] Media attachments (charts, screenshots)
- [ ] List-based scraping from your X lists

## Part of the JECI Group Stack

Built and maintained by Adrian Jordan · [JECI Group](https://jecigroup.com)
