# Phase 4 — Learning Intelligence

Turns the platform into a **personalised practice coach**: it learns what you've
worked on and recommends what to do next, targeting your weak/least-recent areas.

## Commands

| Command | What it does |
|---------|--------------|
| `/practiced <machine> <skills> [platform] [difficulty] [notes]` | Log a box/room you worked on. Builds your study journal. |
| `/progress` | Your recent sessions + skill coverage (last 90d) + HTB owns. |
| `/recommend` | AI recommendation for what to practice next. |

Plus a **weekly auto-post** to `#htb-ctf` (day/time configurable) and
`/monitor htb` to refresh the HTB catalog on demand (admin).

## How the recommendation works

It fuses three inputs and asks the local AI to pick the single best next step:

1. **Your `/practiced` logs** — the explicit skills you've tagged.
2. **Your HTB own-status** — OS balance (Windows vs Linux) from the imported catalog.
3. **The HTB machine catalogue** — candidate unowned machines (+ AI-derived skill tags).

Works with logs alone; the HTB catalogue makes recommendations concrete
("do **Forest** — Windows/AD/Kerberoasting").

## HackTheBox integration

Set `HTB_APP_TOKEN` (JWT from **HTB → Profile Settings → App Tokens → Create**) in
`.env`. When present:

- The **HTB import monitor** (`tasks/htb_monitor.py`) syncs the machine catalogue +
  your own-status into `htb_machines` every `HTB_REFRESH_HOURS`, and lazily
  AI-tags machines with technique areas (bounded per run).
- `/recommend` and the weekly post use real machines you haven't rooted yet.

> The HTB API is undocumented/semi-private (v4, `Authorization: Bearer <token>`).
> The client parses defensively and degrades to empty rather than crashing. Own-
> status is read from the per-machine flags the list returns. Fine-grained
> technique tags aren't in the API, so they're AI-derived.
>
> Without a token, everything still works from your `/practiced` journal.

## Architecture

```
learning/                    ← NEW
├── htb_client.py            ← HTB v4 API (catalog + owns), defensive parsing
└── recommender.py           ← fuse logs + owns + catalog → AI recommendation
tasks/htb_monitor.py         ← catalog/owns import (BaseMonitor, posts nothing)
cogs/learning.py             ← /practiced, /progress, /recommend
```

`bot.py` runs the **weekly recommendation** loop (checked daily, posts on
`RECOMMEND_DAY` at `RECOMMEND_TIME`). The HTB monitor only registers when a token
is set, so the scheduler stays clean otherwise.

## Database

New tables (migration `docs/migrations/004_phase4.sql`, auto-applied):

- `practice_log` — your study journal (machine, skills[], difficulty, notes, source).
- `htb_machines` — HTB catalogue + own flags + AI skill areas.

## Configuration (`.env`)

```
HTB_APP_TOKEN=           # empty → manual-journal mode only
HTB_API_BASE=https://labs.hackthebox.com/api/v4
HTB_REFRESH_HOURS=24
RECOMMEND_DAY=0          # 0=Mon .. 6=Sun
RECOMMEND_TIME=08:00     # Asia/Colombo
```

## Testing checklist

- [ ] `/practiced Forest windows,active-directory,kerberoasting` logs a session.
- [ ] `/progress` shows the session + skill counts.
- [ ] `/recommend` returns an AI suggestion (from logs; from catalogue once token set).
- [ ] With `HTB_APP_TOKEN` set: `/monitor htb` imports machines; `htb_machines` populates.
- [ ] Weekly post lands in `#htb-ctf` on the configured day.

## Rollback

Phase 4 is purely additive. To disable the HTB API layer, clear `HTB_APP_TOKEN`
(manual journal still works). Tables are harmless to leave; drop with
`DROP TABLE IF EXISTS practice_log, htb_machines;` if desired.
