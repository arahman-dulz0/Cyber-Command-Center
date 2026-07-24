# Phase 7 — Multi-Agent Intelligence Crew

A team of specialised AI agents that hand off to each other to produce a
synthesised intelligence report — then post it to Discord and surface it on the
dashboard.

```
        gather intel (PostgreSQL)
                 │
   🗺️ Planner ─▶ 🌐 Threat Researcher ─▶ 🎯 CVE Analyst ─▶ 🎓 Learning Coach
                 │            │                 │                │
                 └────────────┴────────┬────────┴────────────────┘
                                   📝 Report Writer  (synthesises everything)
                                        │
                          Discord embed + reports table + dashboard
```

Each agent is a distinct role — its own system prompt over the local model
(`qwen2.5:3b`) with a bounded generation — and each one's output is handed to the
next (the Writer receives all four teammates' notes). This is genuine role
specialisation + handoff, not one prompt pretending to be many.

## The crew

| Agent | Role |
|-------|------|
| 🗺️ **Planner** | Picks the 2-3 things that matter most today from the intel digest. |
| 🌐 **Threat Researcher** | Summarises the current threat landscape from news + CVE activity. |
| 🎯 **CVE Analyst** | Picks the single most important prioritised CVE and the action to take. |
| 🎓 **Learning Coach** | Recommends the next practice focus from your skills + HTB progress. |
| 📝 **Report Writer** | Synthesises all of the above into an executive summary. |

## Trigger & delivery

- **`/report`** — run the crew on demand (deferred; ~1–2 min for 5 sequential
  generations on this CPU-only host). Posts an embed: executive summary +
  per-agent sections.
- **Weekly auto-post** — to `#{REPORT_CHANNEL}` on `REPORT_DAY` at `REPORT_TIME`.
- Every report is stored in `reports` and shown in the dashboard's **Latest
  intelligence reports** panel.

## Architecture

```
agents/                  ← NEW
├── base.py              ← Agent (role system-prompt + bounded run(), metrics)
└── crew.py              ← gather intel → Planner→Researcher→Analyst→Coach→Writer
cogs/reports.py          ← /report + report→embed rendering
bot.py                   ← weekly_report_task (REPORT_DAY / REPORT_TIME)
services/dashboard/      ← /api/latest-reports + "Latest reports" panel
```

Reuses everything already built: the crew reads the CVE-fusion data (Phase 3),
news (Phase 2), learning data (Phase 4). Adding a new agent = add an `Agent` and
a line in the pipeline.

## Database

`reports` (migration `docs/migrations/006_phase7.sql`, auto-applied):
`id, title, summary, content, created_at`.

## Configuration (`.env`)

```
REPORT_CHANNEL=ai-summaries   # where the weekly report is posted
REPORT_DAY=0                  # 0=Mon .. 6=Sun
REPORT_TIME=07:45             # Asia/Colombo
```

## Notes

- Agents run **sequentially** (the host serves one model at a time); the crew is
  intentionally patient rather than parallel.
- Each agent degrades gracefully: if the model is unavailable, that section says
  so and the report still assembles.
- Agent calls are recorded in `ai_metrics` as `agent:<name>` for `/stats`.

## Testing checklist

- [ ] `/report` returns an embed with an executive summary + 4 agent sections.
- [ ] The report references real current data (top CVE, KEV, news).
- [ ] `reports` table gets a row; dashboard "Latest reports" panel shows it.
- [ ] Weekly auto-post lands in `#ai-summaries` on the configured day.

## Rollback

Additive. Remove `cogs.reports` from `INITIAL_COGS` (and the weekly task) to
disable; the `reports` table is harmless to leave.
