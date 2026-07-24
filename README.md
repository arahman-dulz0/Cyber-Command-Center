# 🛡️ Cyber Command Center

A self-hosted, fully automated **cybersecurity intelligence platform** that runs
24/7 on a home server. It monitors the internet for threats, CVEs, news, and CTF
events, then delivers everything to a personal Discord server as a smart,
AI-summarised feed — a personal security operations center that never sleeps.

> Portfolio project demonstrating: Linux server administration (Proxmox +
> Ubuntu), Docker, PostgreSQL design, Discord bot development, REST API
> integration, local AI (Ollama), workflow automation (n8n), and async Python.

## Architecture

```
MSI GF63 laptop (i5 8th gen, 12GB) — Proxmox VE 9.2.4
└── Ubuntu Server 24.04 LTS VM (192.168.8.185)
    ├── Docker
    │   ├── n8n          → :5678
    │   ├── PostgreSQL   → :5432   (db: cyberdb)
    │   ├── Redis        → :6379
    │   └── discord-bot  → this repo (Phase 1)
    └── Ollama           → :11434  (qwen3:4b)
```

The Discord bot is written in fully async Python (`discord.py` 2.x, `asyncpg`,
`aiohttp`, `redis.asyncio`) and talks to the local AI, PostgreSQL, Redis, and the
NVD / RSS APIs.

## Features (Phase 1)

- **`/ask`** — query the local `qwen3:4b` model
- **`/cve`** — NVD CVE lookup with severity-coloured embeds, affected products,
  an AI plain-English summary, and PostgreSQL caching
- **`/news`** — latest headlines from The Hacker News, BleepingComputer, CISA
- **`/status`** — live health check of PostgreSQL, Redis and Ollama
- **`/brief`** — on-demand daily security briefing (also auto-posted at 07:30)
- **`/help`**, **`/reload`**, **`/sync`**

All AI calls are async with a 30s timeout and 3× exponential-backoff retries.
Every command is logged; every error is reported to `#bot-logs` with a full
traceback while users only ever see a friendly message.

## Repository layout

```
cyber-command-center/
├── services/discord-bot/    # the bot (bot.py, cogs/, utils/, Dockerfile)
├── docker/                  # infrastructure.yml (existing) + bot.yml
├── scripts/deploy.sh        # one-command deploy
├── docs/                    # phase1.md, schema.sql
├── .env                     # secrets (gitignored)
└── README.md
```

## Quick start

```bash
cp services/discord-bot/.env.example .env   # then fill in DISCORD_TOKEN etc.
./scripts/deploy.sh
```

See **[docs/phase1.md](docs/phase1.md)** for full setup, deployment, and
troubleshooting instructions.

## Tech stack

Python 3.11 · discord.py 2.4 · asyncpg · aiohttp · feedparser · Redis ·
PostgreSQL · Ollama (qwen3:4b) · Docker · Proxmox · Ubuntu Server

## Autonomous monitoring (Phase 2)

Running inside the bot process (no cron, no extra containers):

- **CVE monitor** — hourly NVD sweep for newly published CVSS ≥ 7 CVEs → AI
  summary → `#cve-alerts` (with a *View on NVD* button).
- **News monitor** — every 2h from The Hacker News, BleepingComputer, CISA,
  Krebs on Security, Schneier on Security → AI summary → `#cyber-news`.
- **`/status`** — full system dashboard (CPU/RAM/disk + services + DB counts +
  last runs). **`/stats`** — usage & intelligence statistics.
  **`/monitor`** — run a monitor on demand (admin).

See **[docs/phase2.md](docs/phase2.md)** for architecture, configuration, and
how to add new monitors (GitHub, YouTube, HTB, ExploitDB, KEV, …).

## Threat Intelligence Fusion (Phase 3)

Each CVE is correlated across multiple free intelligence sources, scored, and
risk-analysed before it's posted — `CVE → EPSS → CISA KEV → ExploitDB → GitHub
PoCs → vendor patch → AI risk → CCC Priority → Discord`:

- **EPSS** exploitation probability · **CISA KEV** active-exploitation + ransomware
- **ExploitDB** & **GitHub PoC** exploit availability · NVD-derived **patch** status
- **CCC Priority** (0–100) drives colour + ordering; local AI writes the risk analysis

Pluggable `enrichment/` layer — a new source is a client + one line in the fusion
engine. See **[docs/phase3.md](docs/phase3.md)**.

## Roadmap

- **Phase 1** — Discord bot foundation ✅
- **Phase 2** — autonomous CVE + news threat intelligence ✅
- **Phase 3** — threat-intelligence fusion engine (EPSS/KEV/ExploitDB/PoC/priority) ✅
- **Phase 4** — personalised learning intelligence (HTB import + `/practiced` journal + AI `/recommend`) ✅
- **Phase 5** — RAG knowledge base: `/ask` grounded in your own notes/writeups/PDFs with citations ✅
- **Phase 6** — self-hosted SOC web dashboard (FastAPI + Chart.js, LAN-only, read-only over Postgres) ✅
- **Phase 7** — multi-agent intelligence crew (Planner→Researcher→Analyst→Coach→Writer → `/report`) ✅
- **Phase 8** — automation & actioning: lab inventory match → auto-ticket + AI remediation checklist → `#announcements` escalation (+ optional email) ✅

**All 8 phases complete** — a self-hosted, AI-powered cybersecurity operations platform: autonomous threat-intel collection & fusion, a personal RAG brain, a multi-agent report crew, a SOC dashboard, and closed-loop actioning.
