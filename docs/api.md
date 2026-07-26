# API & command reference

Two surfaces: the **Discord slash commands** (how you drive the platform) and the
**dashboard HTTP API** (read-only JSON the web UI polls).

---

## Discord slash commands (22)

All commands are guild-scoped and sync instantly on boot. Every invocation is
logged to `command_logs`; AI Analyst calls are additionally logged to
`analyst_log` (intent, tools, sources, latency).

### 🤖 AI Security Analyst — the primary interface

| Command | Args | What it does |
|---|---|---|
| `/analyst` | `query` | Natural-language question answered from platform knowledge first (assets → DB → RAG → threat intel → CVE/KEV/EPSS → news → learning), LLM last. Rich embeds. |
| `/chat` | `message` | Same engine, conversational — remembers the last CVE/product/topic for follow-ups ("does *it* affect my lab?"). |

Example prompts: *what should I patch today?* · *does CVE-2021-44228 affect my
lab?* · *summarise overnight threats* · *what's actively exploited?*

### 🔎 Threat intelligence

| Command | Args | What it does |
|---|---|---|
| `/cve` | `cve_id` | Look up a CVE with fused enrichment (CVSS/EPSS/KEV/PoC/priority) + AI risk. |
| `/news` | — | Latest 5 cybersecurity headlines. |

### 🧠 Knowledge base (RAG)

| Command | Args | What it does |
|---|---|---|
| `/ask` | `question` | Answer grounded in your ingested notes/PDFs, with citations; falls back to general knowledge below the similarity threshold. |
| `/kb-add` | `file` | Index a PDF / Markdown / text document (chunked + embedded). |
| `/kb-list` | — | List indexed documents. |
| `/kb-search` | `query` | Semantic search over the knowledge base. |

### 🎓 Learning

| Command | Args | What it does |
|---|---|---|
| `/practiced` | `machine`, … | Log a machine/box you practiced (skills, difficulty, notes). |
| `/progress` | — | Recent practice history + skill coverage. |
| `/recommend` | — | AI recommendation for what to practice next. |

### 🛡️ Automation & actioning

| Command | Args | What it does |
|---|---|---|
| `/lab add` | `tech`, `note?` | Add a product/keyword to your lab inventory (drives asset correlation). |
| `/lab list` | — | Show your lab inventory. |
| `/lab remove` | `tech` | Remove a keyword. |
| `/tickets` | — | Open remediation tickets (CVEs that hit your lab). |
| `/ticket-close` | `ticket_id` | Close a ticket. |

### 📊 General

| Command | Args | What it does |
|---|---|---|
| `/status` | — | System + service health dashboard. |
| `/stats` | — | Usage & intelligence statistics. |
| `/brief` | — | On-demand daily security briefing. |
| `/report` | — | Run the multi-agent crew → executive intelligence report. |
| `/help` | — | List all commands. |

### 🛠️ Admin

| Command | Args | What it does |
|---|---|---|
| `/monitor` | `task` | Run a monitor now (`cve` / `news` / `htb` / `kb`). |
| `/reload` | `cog` | Hot-reload a cog. |
| `/sync` | — | Re-sync slash commands to the guild. |

---

## Dashboard HTTP API

Base URL: `http://<host>:8080`. Read-only over the same Postgres. Served by
`services/dashboard/app.py`; queries live in `db.py`.

### Auth

- **`/`** (the UI) — HTTP Basic (`DASHBOARD_USER` / `DASHBOARD_PASS`).
- **`/api/*`** — Basic **or** `X-API-Key: <DASHBOARD_API_KEY>`.
- **`/healthz`** — unauthenticated, rate-limit-exempt (container healthcheck).
- If `DASHBOARD_USER`/`PASS` are unset the dashboard runs in **open mode** (LAN/localhost demo) and logs a warning.

```bash
# with an API key
curl -H "X-API-Key: $DASHBOARD_API_KEY" http://localhost:8080/api/summary
# with basic auth
curl -u "$DASHBOARD_USER:$DASHBOARD_PASS" http://localhost:8080/api/security-score
```

### Endpoints

| Method · path | Returns |
|---|---|
| `GET /healthz` | `{"ok": true}` |
| `GET /api/summary` | Headline counts + threat level + learning/KB/ticket/asset totals. |
| `GET /api/security-score` | `{score, grade, color, factors[]}` — inverse-risk 0–100 from lab exposure. |
| `GET /api/assets-summary` | `{total, needs_patch, healthy}` — lab inventory posture. |
| `GET /api/priority-distribution` | `{CRITICAL, HIGH, MEDIUM, LOW}` counts (severity mix). |
| `GET /api/activity-trend` | 7-day `[{day, cves, kev}]` for the trend chart. |
| `GET /api/cve-timeline` | 7-day `[{day, count}]` of new CVEs. |
| `GET /api/latest-alerts` | 8 latest fused CVEs (CVSS/EPSS/KEV/PoC/priority). |
| `GET /api/latest-news` | 8 latest news articles. |
| `GET /api/latest-reports` | 5 latest agent-crew reports. |
| `GET /api/top-skills` | Practice skill frequency. |

All JSON responses serialise datetimes to ISO-8601. Rate limiting is per-IP
(`DASHBOARD_RATE_LIMIT` requests / `DASHBOARD_RATE_WINDOW` seconds).

See **[security.md](security.md)** for the full auth/headers/rate-limit model.
