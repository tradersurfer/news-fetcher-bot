# Bitcoin News Fetcher Bot v2.0

**Combined bot that fetches Bitcoin news from X profiles, Google Advanced Search, and SEC EDGAR — then posts directly to @AdrianJordan_io.**

## What It Does

```
┌─────────────────────────────────────────────────┐
│              SOURCES (every 5 min)               │
│                                                   │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ X Profiles   │  │ Google      │  │ SEC EDGAR│ │
│  │ (fetch posts │  │ Advanced    │  │ 10-K/8-K/│ │
│  │  from list)  │  │ Search      │  │  10-Q    │ │
│  └──────┬───────┘  └──────┬──────┘  └────┬─────┘ │
│         │                 │               │       │
│         └────────┬────────┴───────────────┘       │
│                  ↓                                │
│          Dedup Engine                             │
│          (seen_stories.json)                      │
│                  ↓                                │
│          AI Processor (Claude)                    │
│          → 3 draft options per story              │
│                  ↓                                │
│          X Poster (Tweepy)                        │
│          → Posts to @AdrianJordan_io              │
│                                                   │
└─────────────────────────────────────────────────┘
```

## Architecture

```
news-fetcher-bot/
├── main.py                  # Entry point with CLI args
├── requirements.txt         # Python dependencies
├── .env.template            # Environment template
├── README.md               # This file
├── core/
│   ├── __init__.py         # Core module exports
│   └── config.py           # Shared config, models, dedup engine
├── modules/
│   ├── x_scraper.py        # Fetch posts from X profiles
│   ├── google_search.py    # Google Advanced Search for Bitcoin news
│   ├── sec_edgar.py        # SEC EDGAR filings (10-K, 8-K, 10-Q)
│   ├── ai_processor.py     # Claude-based headline rewriting
│   ├── x_poster.py         # Direct posting to @AdrianJordan_io
│   └── orchestrator.py     # Main scheduler + pipeline
└── sources/
    └── x_profiles.py       # X profiles to monitor
```

## Quick Start

```bash
# 1. Copy .env.template and fill in your keys
cp .env.template .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run once to test (no posting)
python main.py --test

# 4. Run single cycle
python main.py --once

# 5. Run continuously (default: every 5 min)
python main.py

# 6. Custom interval
python main.py --interval 10  # every 10 minutes
```

## CLI Options

| Flag | Description |
|------|-------------|
| `--once` | Run one cycle and exit |
| `--test` | Quick smoke test (no posting) |
| `--interval N` | Set polling interval in minutes |

## Configuration (.env)

```env
# AI
ANTHROPIC_API_KEY=your_claude_api_key

# X/Twitter
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
TARGET_HANDLE=AdrianJordan_io

# Google Search
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_custom_search_engine_id

# Scheduler
FETCH_INTERVAL_MINUTES=5

# SEC EDGAR
SEC_CIK_NUMBERS=0001350862,0000320193
```

## Sources

### X Profiles (`sources/x_profiles.py`)
Edit this file to add/remove X handles. The bot fetches recent posts from each profile and filters for Bitcoin/crypto-relevant content.

### Google Advanced Search (`modules/google_search.py`)
Uses Google Programmable Search API (or Serper fallback) to search for Bitcoin news across crypto outlets, institutional sources, and regulatory news.

### SEC EDGAR (`modules/sec_edgar.py`)
Searches SEC EDGAR full-text search for 10-K, 10-Q, and 8-K filings mentioning Bitcoin, cryptocurrency, or digital assets. Also supports filtering by specific CIK numbers.

### AI Processing (`modules/ai_processor.py`)
Every story passes through Claude which generates 3 draft X posts following the @AdrianJordan_io brand voice.

### X Posting (`modules/x_poster.py`)
Direct posting to @AdrianJordan_io using Tweepy. Supports single tweets and thread posting with rate limiting.

## Brand Voice

- **Tone**: Direct, authoritative, knowledgeable
- **Style**: Headline-only, no preamble, no hashtags
- **Length**: Under 280 characters
- **Impact**: Stack the most important fact first
- **Accuracy**: Never invent facts or sensationalize

## Planned Features

- [ ] Add webhook triggers for immediate posting
- [ ] Add Telegram/Slack notifications
- [ ] Add media attachments (charts, screenshots)
- [ ] Add thread threading for longer analysis
- [ ] Add sentiment scoring for draft selection
- [ ] Add posting history database

## Part of the JECI Group Stack

Built and maintained by [Adrian Jordan](https://github.com/tradersurfer) · [JECI Group](https://jecigroup.com)
