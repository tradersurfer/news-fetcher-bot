# News Fetcher Bot

**White-label AI news aggregation and publishing bot.** Connects to 8+ live data sources, runs an AI agent to filter and frame content, and posts to X (Twitter) on a configurable schedule.

Two tiers: a lightweight Python core (single-file, Tweepy-based) and a full Mastra TypeScript agent stack with multi-source tools, Inngest scheduling, and Slack/Telegram triggers.

---

## What It Does

```
Data Sources (8+)
 ├── Bitcoin on-chain (Bitbo)
 ├── BTC spot price
 ├── Crypto news RSS
 ├── Breaking news feeds
 ├── ETF flow data (Farside)
 ├── Stock market summary
 ├── Earnings calendar
 └── Custom RSS feeds
          ↓
   MoneyVibes Agent
   (Mastra AI — filters, frames, formats)
          ↓
   postTweetTool
   (posts to configured X account)
          ↓
   Optional: Slack + Telegram triggers
```

---

## White-Label Inputs (Planned v2)

Installers configure:

| Input | Description |
|-------|-------------|
| `X_HANDLE` | Target X account to post to |
| `AI_MODEL` | Choose: Claude / GPT-4o / Grok |
| `BRAND_VOICE` | Brand tone and vocabulary prompt |
| `TOPICS` | Which data sources to enable |
| `POST_SCHEDULE` | Cron expression for posting cadence |
| `LOGO_URL` | Brand image for media posts |

One install → fully configured, branded, autonomous content machine.

---

## Tech Stack

### Core (Python)
| Layer | Technology |
|-------|-----------|
| Runtime | Python 3 |
| X API | Tweepy v4 |
| Scheduler | Native schedule loop |
| Deploy | Replit / Railway |

### Full Stack (TypeScript / Mastra)
| Layer | Technology |
|-------|-----------|
| Agent Framework | Mastra |
| Runtime | Node.js / TypeScript |
| Scheduling | Inngest (cron + event-driven) |
| Triggers | Slack, Telegram, Webhook, Cron |
| Deployment | Replit / Railway |

---

## Agent Tools (Mastra Stack)

| Tool | Data Source |
|------|-------------|
| `fetchBitboTool` | Bitcoin on-chain metrics (Bitbo) |
| `fetchBitcoinPriceTool` | BTC spot price |
| `fetchCryptoNewsTool` | Crypto news aggregator |
| `fetchBreakingNewsTool` | Live breaking news |
| `fetchFarsideEtfTool` | Bitcoin ETF flow data (Farside) |
| `fetchRssNewsTool` | Custom RSS feed reader |
| `fetchStockMarketTool` | Equities summary |
| `fetchEarningsTool` | Earnings calendar |
| `postTweetTool` | X/Twitter publishing |

---

## Triggers

| Trigger Type | Behavior |
|-------------|---------|
| Cron | Posts on schedule (configurable interval) |
| Slack | `/post now` command fires immediate post |
| Telegram | Message trigger fires post |
| Webhook | External event fires post |

---

## Setup (Python Core)

```bash
git clone https://github.com/tradersurfer/bitcoin-archive-automation.git
cd bitcoin-archive-automation
pip install tweepy schedule
```

Configure `.env`:
```
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
```

```bash
python main.py
```

---

## Setup (Full Mastra Stack)

```bash
npm install
```

Configure `.env`:
```
ANTHROPIC_API_KEY=
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
INNGEST_EVENT_KEY=
SLACK_BOT_TOKEN=       # optional
TELEGRAM_BOT_TOKEN=    # optional
```

```bash
npm run dev
```

---

## Origin

Forked from the MV Media Bot (`moneyVibesAgent` + `moneyVibesWorkflow`). Bitcoin Archive was the first white-label deployment — posting BTC on-chain data, ETF flows, and market updates to [@BitcoinArchive](https://x.com/BitcoinArchive) on a daily schedule.

---

## Part of the JECI Group Stack

Built and maintained by [Adrian Jordan](https://github.com/tradersurfer) · [JECI Group](https://jecigroup.com)

> *One bot. Any brand. Any topic. Autonomous.*
