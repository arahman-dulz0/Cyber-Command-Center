# Phase 2 — Autonomous Threat Intelligence

Phase 2 turns the bot into a self-running threat-intelligence platform. All work
happens **inside the existing Discord bot process** via `discord.py` background
tasks — no new containers, no cron, no external schedulers.

## What's new

| Feature | Summary |
|---------|---------|
| **CVE monitor** | Every hour: fetch newly published CVSS ≥ 7 CVEs from NVD, summarise, post to `#cve-alerts` with a *View on NVD* button. |
| **News monitor** | Every 2 hours: pull ≤ 3 articles/feed from 5 sources, summarise, post to `#cyber-news` (30s between posts). |
| **Upgraded `/brief`** | Morning briefing at 07:30 Asia/Colombo, assembled **entirely from PostgreSQL** (never refetches APIs). |
| **Upgraded `/status`** | CPU, RAM, disk, Docker, Postgres, Redis, Ollama, bot latency, DB counts, last monitor runs, AI model. |
| **`/stats`** | Today's CVEs/news, AI summaries generated, commands used, DB size, average AI response time, top command. |
| **`/monitor cve\|news`** | Admin-only: run a monitor immediately; returns time taken, items found/posted, errors. |

## Architecture

```
services/discord-bot/
├── tasks/                     ← background monitors (NEW)
│   ├── base.py                ← BaseMonitor: fetch() → process() → post() → run()
│   ├── cve_monitor.py
│   ├── news_monitor.py
│   └── scheduler.py           ← registers monitors, one discord.py loop each
├── repositories/              ← repository pattern (NEW)
│   ├── base.py
│   ├── cve_repository.py
│   ├── news_repository.py
│   ├── monitor_repository.py
│   ├── command_repository.py
│   └── ai_repository.py       ← summary cache + AI metrics
├── utils/
│   ├── summarizer.py          ← cached AI summaries + metrics (NEW)
│   ├── ollama_client.py       ← + concurrency semaphore, config retries, ping()
│   ├── nvd_client.py          ← + fetch_recent() (published-date, severity-filtered)
│   ├── rss_client.py          ← + fetch_per_feed(), 5 feeds
│   └── logger.py              ← named component loggers
├── cogs/
│   ├── general.py             ← upgraded /status + /brief
│   ├── stats.py               ← /stats (NEW)
│   └── monitor.py             ← /monitor (NEW)
└── database.py                ← + monitor_runs, ai_summaries, ai_metrics; repos wired
```

### Adding a future monitor (GitHub, YouTube, HTB, ExploitDB, KEV, …)

1. Subclass `BaseMonitor`, set `name`, `channel_name`, `interval`, and implement
   `fetch()`, `process()`, `post()`.
2. Register it in `tasks/scheduler.py::build_default_scheduler`.

The scheduler and `/monitor` need **no other changes** — `run()` (state
recording, error capture) and the loop wiring are inherited.

## How the CVE monitor stays fast & cheap

NVD's `lastModStartDate` over 24h returns thousands of records (bulk re-scores)
and times out. Instead the monitor queries by **published date** with NVD's
server-side `cvssV3Severity` filter (one small request per severity band ≥ the
threshold), de-duplicates, filters to the exact score, and caps posts per run.

## Performance & safety

- **AI concurrency** capped at `OLLAMA_MAX_CONCURRENCY` (default 2) via a global
  semaphore in the Ollama client.
- **Summary cache** (`ai_summaries`, keyed by `sha256(model+prompt)`) — the same
  content is never summarised twice.
- **Graceful AI failure** — if Ollama is down, monitors post **without** a
  summary; the bot is never blocked (45s timeout, 3 retries, exponential backoff).
- **No Discord spam** — `CVE_MAX_POSTS_PER_RUN`, `NEWS_MAX_PER_FEED`, and inter-post
  delays (`CVE_POST_DELAY`, `NEWS_POST_DELAY`).
- **De-duplication** — CVEs by `cve_id`, news by `url`; nothing is reposted.
- Each monitor run is wrapped so a failure **never kills the loop**, and is
  recorded in `monitor_runs`.

## Configuration (all via `.env`)

```
MONITORS_ENABLED=true          # master switch for all background monitors
CVE_FETCH_INTERVAL=3600        # CVE monitor cadence (seconds)
NEWS_FETCH_INTERVAL=7200       # News monitor cadence (seconds)
CVE_MIN_SCORE=7.0              # CVSS threshold
CVE_LOOKBACK_HOURS=24          # window used on the first run
CVE_MAX_POSTS_PER_RUN=10
CVE_POST_DELAY=3
NEWS_MAX_PER_FEED=3
NEWS_POST_DELAY=30
OLLAMA_MODEL=qwen2.5:3b        # instruct-tuned, fast
OLLAMA_TIMEOUT=45
OLLAMA_RETRIES=3
OLLAMA_MAX_CONCURRENCY=2
CVE_ALERTS_CHANNEL=cve-alerts
CYBER_NEWS_CHANNEL=cyber-news
DAILY_BRIEF_CHANNEL=daily-brief
RSS_FEEDS=                     # optional JSON override of the 5 built-in feeds
```

## Database

New tables (see `docs/migrations/002_phase2.sql`; applied automatically on boot):

- `monitor_runs` — one row per monitor execution + `last_success` state.
- `ai_summaries` — content-hash → summary cache.
- `ai_metrics` — per-call kind/model/latency/cache_hit for `/stats`.

## Deploy

```bash
# from the project root on the server
./scripts/deploy.sh
# or:
docker compose -f docker/bot.yml up -d --build
docker compose -f docker/bot.yml logs -f
```

The bot creates the new tables on startup. Monitors begin shortly after
(`cve` ~20s, `news` ~60s) and then run on their intervals.

## Testing checklist

- [ ] `docker compose -f docker/bot.yml logs -f` shows both monitors scheduled.
- [ ] `#cve-alerts` receives severity-coloured CVE embeds with a *View on NVD* button.
- [ ] `#cyber-news` receives article embeds (≤ 3 per feed).
- [ ] `/status` shows CPU/RAM/disk, all services green, DB counts, last run times.
- [ ] `/stats` shows today's counts, DB size, avg AI response, top command.
- [ ] `/monitor cve` and `/monitor news` (as admin) return a run summary.
- [ ] `/brief` renders from DB (counts, highest CVSS, headlines, AI tip).
- [ ] Re-running a monitor posts nothing new (de-duplication works).
- [ ] `monitor_runs`, `ai_summaries`, `ai_metrics` tables are populated.

## Rollback

Phase 2 only **adds** tables/columns and code; Phase 1 commands are unchanged.

```bash
# Option A — disable just the autonomous monitors (keep everything else):
#   set MONITORS_ENABLED=false in .env, then:
docker compose -f docker/bot.yml up -d

# Option B — roll the code back to the previous image/commit:
git checkout <phase1-commit> -- services/discord-bot docker/bot.yml
docker compose -f docker/bot.yml up -d --build

# The new tables are harmless if left in place. To remove them entirely:
#   docker exec -i postgres psql -U cyber -d cyberdb \
#     -c "DROP TABLE IF EXISTS monitor_runs, ai_summaries, ai_metrics;"
```
