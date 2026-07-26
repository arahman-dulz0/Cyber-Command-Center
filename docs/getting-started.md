# Getting started

Two ways to run Cyber Command Center. Pick one.

- **[A. Demo dashboard](#a-demo-dashboard-30-seconds)** — one command, no accounts, no keys. Great for a first look.
- **[B. Full platform](#b-full-platform-discord-bot--ai)** — the complete thing: Discord bot, autonomous CVE/news monitoring, threat fusion, the AI analyst, and the dashboard.

## Prerequisites

- A machine with **Docker** + **Docker Compose** (Linux, macOS, or Windows/WSL2). [Install Docker](https://docs.docker.com/get-docker/).
- **git**.
- ~4 GB RAM for the demo; ~8 GB for the full platform (the local AI model).
- That's it — Postgres, Redis and Ollama all run **inside** the stack. You don't install them.

---

## A. Demo dashboard (30 seconds)

```bash
git clone https://github.com/arahman-dulz0/Cyber-Command-Center.git
cd Cyber-Command-Center
docker compose up -d
```

Open **http://localhost:8080**. The dashboard is fully populated with a **real,
public CVE demo dataset** (Log4Shell, MOVEit, Citrix Bleed, …) — a security score,
charts, fused alerts, tickets and reports. No configuration, no API keys, no
model download.

Stop it with `docker compose down` (add `-v` to also wipe the demo database).

---

## B. Full platform (Discord bot + AI)

This runs everything. You provide one free thing: a **Discord bot**. Total time
~5–10 minutes.

### 1. Clone the repo

```bash
git clone https://github.com/arahman-dulz0/Cyber-Command-Center.git
cd Cyber-Command-Center
```

### 2. Create a Discord bot (free)

1. Go to the **[Discord Developer Portal](https://discord.com/developers/applications)** → **New Application**. Name it (e.g. "Cyber Command Center").
2. Left sidebar → **Bot**.
3. Under **Privileged Gateway Intents**, turn **ON** both:
   - ✅ **Message Content Intent**
   - ✅ **Server Members Intent**

   > The bot will not start without these two enabled.
4. Click **Reset Token** → **Copy**. This is your `DISCORD_TOKEN` — keep it secret.

### 3. Invite the bot to your server

1. Left sidebar → **OAuth2** → **URL Generator**.
2. **Scopes**: check **`bot`** and **`applications.commands`**.
3. **Bot Permissions**: check **View Channels, Send Messages, Embed Links, Attach
   Files, Read Message History, Use Application Commands** (or just **Administrator**
   for a personal test server).
4. Copy the generated URL at the bottom, open it, and add the bot to **your**
   Discord server.

### 4. Get your server (guild) ID

1. In Discord: **User Settings → Advanced → Developer Mode: ON**.
2. Right-click your **server icon** → **Copy Server ID**. This is your
   `DISCORD_GUILD_ID`.

### 5. Create the channels the bot posts into

In your server, create these text channels (default names):

- `#bot-logs` · `#cve-alerts` · `#cyber-news` · `#daily-brief`

> Prefer different names? Set `BOT_LOGS_CHANNEL`, `CVE_ALERTS_CHANNEL`,
> `CYBER_NEWS_CHANNEL`, `DAILY_BRIEF_CHANNEL` in your `.env` to match.

### 6. Configure your `.env`

```bash
cp .env.example .env
```

Open `.env` and set the only two required values:

```env
DISCORD_TOKEN=your-bot-token-from-step-2
DISCORD_GUILD_ID=your-server-id-from-step-4
```

Everything else has a sensible default. Optional but nice:

- `NVD_API_KEY` — a free [NVD key](https://nvd.nist.gov/developers/request-an-api-key) raises the CVE rate limit.
- `HTB_APP_TOKEN` — your HackTheBox app token enables the learning/`/recommend` features.

> You do **not** need to set the Postgres/Redis/Ollama hosts — the stack wires
> those up internally.

### 7. Start everything

```bash
docker compose --profile full up -d
```

Then download the local AI models (one-time, a few minutes):

```bash
docker compose exec ollama ollama pull qwen2.5:3b
docker compose exec ollama ollama pull nomic-embed-text
```

### 8. Verify it's alive

- In Discord, type **`/help`** — you should see all the slash commands.
- Open **http://localhost:8080** for the dashboard.
- Watch the bot boot: `docker compose logs -f discord-bot` (look for
  "Synced … commands" and "Logged in as …").

### 9. First things to try

```
/lab add tech: apache        →  tell it what's in your stack
/analyst query: what should I patch today?
/analyst query: does CVE-2021-44228 affect my lab?
/cve cve-id: CVE-2021-44228
/report                      →  a multi-agent intelligence report
```

CVE alerts and news will start flowing into your channels automatically as the
monitors run.

---

## What's running

| Service | Port | Purpose |
|---|---|---|
| `discord-bot` | — | The platform: commands, monitors, AI analyst, actioning |
| `dashboard` | 8080 | Read-only SOC web dashboard |
| `postgres` | — | All data (internal) |
| `redis` | — | Fast state (internal) |
| `ollama` | 11434 | Local AI (chat + embeddings) |

## Next steps

- **[api.md](api.md)** — every command + the dashboard API.
- **[operations.md](operations.md)** — backups, health, updates.
- **[security.md](security.md)** — lock down the dashboard, go public safely.
- **[troubleshooting.md](troubleshooting.md)** — if something misbehaves.
- **[plugins.md](plugins.md)** — extend it with new monitors/tools.

Stuck? The **[troubleshooting guide](troubleshooting.md)** covers the common
first-run issues (intents, model pulls, command sync).
