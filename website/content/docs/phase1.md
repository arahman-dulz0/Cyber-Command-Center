# Phase 1 — Discord Bot Foundation

This document covers setting up and running the Cyber Command Center Discord
bot on your home server.

## What Phase 1 delivers

A production-ready, fully async `discord.py` bot exposing these slash commands:

| Command   | Description                                                        |
|-----------|--------------------------------------------------------------------|
| `/ask`    | Ask the local Ollama model (`qwen3:4b`) any question.              |
| `/cve`    | Look up a CVE from NVD, with an AI plain-English summary + caching. |
| `/news`   | Latest 5 headlines from The Hacker News, BleepingComputer, CISA.  |
| `/status` | Health check for PostgreSQL, Redis, Ollama + uptime + masked IP.  |
| `/brief`  | On-demand daily security briefing.                                |
| `/help`   | Lists all commands by category.                                   |
| `/reload` | Reload a cog (admin only).                                        |
| `/sync`   | Re-sync slash commands (admin only).                              |

Plus: a scheduled **daily briefing** posted to `#daily-brief` at `DAILY_BRIEF_TIME`
(Asia/Colombo), full error reporting to `#bot-logs`, command-usage logging, and
daily-rotated log files.

## Prerequisites (already running on your server)

- PostgreSQL @ `192.168.8.185:5432` (db `cyberdb`, user `cyber`)
- Redis @ `192.168.8.185:6379`
- Ollama @ `192.168.8.185:11434` with `qwen3:4b` pulled
- Docker + Docker Compose on the Ubuntu VM

## 1. Configure secrets

From the project root:

```bash
cp services/discord-bot/.env.example .env
```

Edit `.env` and set at minimum:

- `DISCORD_TOKEN` — from the Discord Developer Portal
- `DISCORD_GUILD_ID` — your server ID (enables instant command sync)
- `NVD_API_KEY` — optional, but raises the NVD rate limit

The database/Redis/Ollama values are pre-filled to match your infrastructure.

## 2. Database schema

The bot creates all tables automatically on first boot. To apply them manually:

```bash
psql -h 192.168.8.185 -U cyber -d cyberdb -f docs/schema.sql
```

## 3. Run with Docker (recommended)

```bash
./scripts/deploy.sh
# or directly:
docker compose -f docker/bot.yml up -d --build
docker compose -f docker/bot.yml logs -f
```

The container uses `network_mode: host` so it can reach the `192.168.8.185`
services directly, and mounts `services/discord-bot/logs/` for persistent logs.

## 4. Run locally (development)

```bash
cd services/discord-bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# .env is read from the project root automatically
python bot.py
```

## Slash-command syncing

On startup the bot copies global commands to your guild and syncs them, so they
appear almost instantly. If a command is missing, run `/sync` (admin only) or
restart the bot.

## Troubleshooting

- **Commands don't appear:** confirm `DISCORD_GUILD_ID` is set and the bot was
  invited with the `applications.commands` scope. Run `/sync`.
- **`/status` shows a service offline:** verify the host/port in `.env` and that
  the service is reachable from the VM (`nc -vz 192.168.8.185 5432`, etc.).
- **Ollama timeouts:** `qwen3:4b` can be slow on first load. Increase
  `OLLAMA_TIMEOUT`. The client already retries 3× with backoff.
- **Errors:** check `#bot-logs` in Discord and `services/discord-bot/logs/bot.log`.

## Logs

- Console + `services/discord-bot/logs/bot.log`
- Rotated daily at midnight, 7 days retained
- Format: `[2026-07-22 07:30:00] [INFO] [cve.py] User abdul used /cve CVE-2021-44228`
