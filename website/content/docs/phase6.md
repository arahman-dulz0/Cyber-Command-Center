# Phase 6 — Web Dashboard

A dark, SOC-style web dashboard that visualises everything the platform collects.
Self-hosted, read-only over the same PostgreSQL, LAN-only.

```
http://<server-ip>:8080
┌ 🛡️ Cyber Command Center ───────────── 🟥 HIGH ┐
│ Critical CVEs · News · KEVs · Exploits · Priority │
│ [CVE 7-day timeline]   [priority distribution]    │
│ Latest fused alerts    Learning progress · News   │
└ dark theme · auto-refresh 30s ────────────────────┘
```

## Stack

FastAPI + uvicorn backend serving one dark HTML page (Tailwind + Chart.js via
CDN). One lightweight container on `docker_cyber-net`, publishing port **8080**
to the LAN. It reads the same tables the bot fills — **no writes, no new infra**.

```
services/dashboard/
├── app.py                ← FastAPI: HTML page + /api/* JSON endpoints
├── db.py                 ← read-only asyncpg queries (summary, charts, lists)
├── templates/index.html  ← dark SOC UI, Chart.js, 30s auto-refresh
├── Dockerfile            ← multi-stage, non-root
└── requirements.txt
docker/dashboard.yml      ← compose service (docker_cyber-net, :8080)
```

## What it shows

- **Threat level** badge (LOW → GUARDED → ELEVATED → HIGH), derived from recent
  KEV hits / top priority / exploited counts.
- **Stat tiles**: critical CVEs (24h), news (24h), KEVs, exploited, top priority,
  commands used.
- **CVE timeline** (7-day line chart) and **priority distribution** (bar chart).
- **Latest fused CVE alerts** (priority-coloured, with KEV/PoC/EDB/EPSS badges,
  linking to NVD).
- **Learning** panel: HTB owned vs goal (progress bar), sessions, distinct
  skills, KB docs/chunks.
- **Latest news** headlines.

## Endpoints

| Path | Returns |
|------|---------|
| `/` | the dashboard HTML |
| `/healthz` | liveness |
| `/api/summary` | tiles + threat level + learning |
| `/api/cve-timeline` | 7-day CVE counts |
| `/api/priority-distribution` | counts per priority label |
| `/api/latest-alerts` | recent fused CVE alerts |
| `/api/latest-news` | recent headlines |
| `/api/top-skills` | practised-skill counts |

## Deploy

```bash
docker compose -f docker/dashboard.yml up -d --build
docker compose -f docker/dashboard.yml logs -f
# then open http://<server-ip>:8080 on your LAN
```

## Security notes

- **XSS**: all untrusted strings (news titles/sources from RSS, CVE ids) are
  HTML-escaped before rendering; links are restricted to `http(s)` (no
  `javascript:`/`data:` URLs).
- **LAN-only**: the port is published to the local network only. Going public
  is a deliberate later step and needs, together: a reverse proxy + TLS,
  authentication, and bundling the Tailwind/Chart.js assets locally with
  Subresource Integrity (the CDN scripts currently have no SRI, acceptable on a
  private single-user LAN but not for public exposure).

## Testing checklist

- [ ] `curl http://<server-ip>:8080/healthz` → `{"ok":true}`.
- [ ] `curl .../api/summary` returns live counts + a threat level.
- [ ] Browser shows tiles, both charts render, latest alerts + news populate.
- [ ] Threat badge colour matches the data (KEV present → HIGH/red).
- [ ] Auto-refresh updates the "updated HH:MM:SS" stamp every 30s.

## Rollback

Independent container — stop it any time with
`docker compose -f docker/dashboard.yml down`. It never writes to the database,
so removing it has zero effect on the bot or data.
