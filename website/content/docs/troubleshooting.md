# Troubleshooting

Symptom → cause → fix. For operational procedures (backups, updates, health) see
**[operations.md](operations.md)**.

---

## Install & startup

### `docker compose up` fails / dashboard shows no data

- **Postgres didn't seed.** The demo data only loads on a **fresh** volume (first
  init). If you changed the seed after first boot, reset it:
  ```bash
  docker compose down -v && docker compose up -d
  ```
  `-v` drops the `pgdata` volume so `docker/demo/initdb/*.sql` re-runs.

### Dashboard returns 401 on the demo

- You (or a `.env` in the project dir) set `DASHBOARD_USER`/`DASHBOARD_PASS`.
  Compose auto-reads `.env` for interpolation. Unset them for open mode, or log in
  with those credentials.

### Port 8080 already in use

- Something else (or a previous stack) owns it. Change the published port:
  ```bash
  DASHBOARD_PORT=8090 docker compose up -d
  ```

---

## The bot

### Slash commands don't appear in Discord

- Commands are **guild-scoped**; check `DISCORD_GUILD_ID` is set and correct.
- Run `/sync` (admin) to force a re-sync, or restart the bot.
- Ensure the bot was invited with the `applications.commands` scope.

### A command "did not respond"

Two usual causes:
1. **The bot container is down/crashed** — `docker ps` and check `#bot-logs` /
   `docker compose -f docker/bot.yml logs discord-bot`.
2. **A long command exceeded Discord's 15-minute interaction token** (e.g.
   `/report` running the 5-agent crew). These deliver via a channel message, not
   the interaction — if you changed that, revert to `channel.send`.

### Stale code after a rebuild

- `docker restart` reuses the **old image**. Always recreate from the new build:
  ```bash
  docker compose -f docker/bot.yml up -d --build
  ```

---

## AI / Ollama

### AI answers time out or are very slow

- **CPU-only Ollama serialises requests.** Keep `OLLAMA_MAX_CONCURRENCY=1`; two
  concurrent requests queue inside Ollama and blow the timeout.
- The **first** call after idle loads the model (~20s cold); subsequent calls are
  ~6–7s warm. `/analyst` defers, so it won't time out — just wait for the spinner.
- Verify the model is pulled: `docker compose exec ollama ollama list`. Pull with
  `ollama pull qwen2.5:3b` and `ollama pull nomic-embed-text`.

### `/ask` never cites my documents

- Confirm ingestion: `/kb-list`. If empty, `/kb-add` a file or drop files in the
  `KNOWLEDGE_DIR` folder for bulk ingest.
- Retrieval only grounds above `KB_MIN_SIMILARITY`; below it, the bot answers from
  general knowledge and says so.

---

## Data & correlation

### "Does my lab have exposure?" always says no inventory

- Your lab is empty. Add keywords: `/lab add tech: apache`. Use product names, not
  versions (`log4j`, not `Log4j 2.14`).

### The dashboard Security Score seems too high/low

- It reflects **your** exposure, not the global feed: open tickets, KEV-in-lab,
  and assets awaiting patch. A clean lab (no open tickets) scores 100. Add lab
  assets so real CVEs correlate into tickets.

---

## Server / connectivity

### SSH "connection timed out" / dashboard unreachable

- On a Proxmox/VM host, the VM may be **powered off/asleep** (common if the host
  laptop sleeps). Start the VM; containers auto-recover via `restart:
  unless-stopped` and Ollama via systemd.

### Postgres/Redis "could not translate host name"

- The bot/dashboard reach them by **service name** over the Docker network
  (`POSTGRES_HOST=postgres`, `REDIS_HOST=redis`), not a LAN IP. Check they share
  the network and the names match.
