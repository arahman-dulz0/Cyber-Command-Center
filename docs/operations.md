# Operations runbook (Stage 2 — production readiness)

Everything needed to run the platform like operable software: health, recovery,
backups, monitoring, logs and safe updates.

## Health & automatic recovery

Three layers, so no single failure mode is unrecoverable:

| Failure | Handled by |
|---------|-----------|
| Process crash / exit | `restart: unless-stopped` (Docker) |
| Container **unhealthy** (event loop stuck, `/healthz` failing) | `willfarrell/autoheal` restarts it (label `autoheal=true`) |
| Container **removed** entirely (interrupted deploy) | `scripts/autoheal.sh` recreates it via cron (every 5 min) |

**Healthchecks**
- **Bot** — no HTTP port, so it writes a heartbeat file every 30s from its event
  loop; `healthcheck.py` fails if that heartbeat is stale. This proves the loop
  is *actually running*, not just that the process exists.
- **Dashboard** — polls its own `/healthz`.

```bash
docker inspect --format '{{.State.Health.Status}}' cyber-discord-bot   # healthy
docker inspect --format '{{.State.Health.Status}}' cyber-dashboard
```

## Backups & restore

Logical backups of the whole database (bot + n8n share `cyberdb`) plus the
knowledge base, gzip-compressed, with retention.

```bash
./scripts/backup.sh                       # dump -> backups/cyberdb-<ts>.sql.gz
./scripts/restore.sh backups/cyberdb-<ts>.sql.gz   # destructive, confirmed
```
`BACKUP_RETAIN` (default 14) controls how many are kept.

## Scheduled jobs

Installed into the **user crontab** (no sudo):

```bash
./scripts/install-crons.sh     # autoheal every 5 min, backup daily 03:17
crontab -l                     # view
```

## Monitoring & logs (ops stack)

```bash
docker compose -f docker/ops.yml up -d
```

| Service | URL | Purpose |
|---------|-----|---------|
| **Uptime Kuma** | `http://<server>:3001` | uptime monitors + status page |
| **Dozzle** | `http://<server>:8888` | live, searchable logs for every container |
| **autoheal** | — | restarts unhealthy containers |

Suggested Uptime Kuma monitors (add in its UI):
- HTTP `http://cyber-dashboard:8080/healthz`
- TCP `postgres:5432`, `redis:6379`
- HTTP `http://192.168.8.185:11434/api/tags` (Ollama)

> These containers mount the Docker socket (autoheal writes, Dozzle read-only).
> Keep ports 3001/8888 on the LAN only.

## Environment validation

Run before any deploy — checks required `.env` keys and that Postgres, Redis and
the Ollama model are all reachable:

```bash
./scripts/validate-env.sh      # exits non-zero if anything is wrong
```

## Updating safely

Auto-updater for the locally-built app containers (backs up first, validates,
then rebuilds):

```bash
./scripts/update.sh
```
Databases and other registry images are **not** auto-updated — bump those
deliberately. To automate app updates, add `update.sh` to cron (weekly is
sensible), but review the first few runs.

## Deploy from scratch

```bash
./scripts/validate-env.sh          # 1. preflight
docker compose -f docker/bot.yml up -d --build
docker compose -f docker/dashboard.yml up -d --build
docker compose -f docker/ops.yml up -d
./scripts/install-crons.sh         # 2. schedule autoheal + backups
```
