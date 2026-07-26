# Extending the platform

The three subsystems most people want to extend are **monitors** (new
intelligence feeds), **enrichment sources** (new signals per CVE), and **analyst
tools** (new things `/analyst` can do). Each has a single, small extension point.

---

## 1. Add a monitor

Monitors run inside the bot process on a loop (no cron, no extra containers).
They subclass `BaseMonitor` (`tasks/base.py`) and implement three async methods;
the base class handles scheduling, `monitor_runs` bookkeeping, and error capture.

```python
# tasks/vendor_monitor.py
from tasks.base import BaseMonitor

class VendorMonitor(BaseMonitor):
    name = "vendor"                 # /monitor choice + monitor_runs.task key
    channel_name = "cve-alert"      # Discord channel to post into
    interval = 3600                 # seconds between runs

    async def fetch(self) -> list:
        # Pull raw items from your source (HTTP, RSS, API…).
        ...

    async def process(self, raw: list) -> list:
        # Dedupe, filter, enrich. Return only new items to post.
        ...

    async def post(self, items: list) -> int:
        # Build embeds and send to self.channel; return count posted.
        ...
```

Register it in `build_default_scheduler()` (`tasks/scheduler.py`):

```python
scheduler.register(VendorMonitor(bot))
```

That's it — it now appears in `/monitor`, records runs to `monitor_runs`, and
shows up on the dashboard's last-run panel. Gate it behind a config flag (see the
`config.htb_enabled` / `config.kb_enabled` examples) if it needs a token.

---

## 2. Add an enrichment source

The fusion engine (`enrichment/fusion.py`) correlates free intelligence sources
into one `Enrichment` per CVE. A source is a small client (subclass the pattern
in `enrichment/epss.py` / `kev.py`) plus **one line** in `FusionEngine`.

```python
# enrichment/mysource.py
class MySourceClient:
    async def lookup(self, cve_id: str) -> dict:
        # Return the signal(s) for this CVE.
        ...
```

Wire it into `FusionEngine.__init__` and fold its signal into the score:

```python
# enrichment/fusion.py
class FusionEngine:
    def __init__(self):
        self.epss = EPSSClient()
        self.kev = KEVClient()
        self.exploitdb = ExploitDBClient()
        self.github = GitHubPoCClient()
        self.mysource = MySourceClient()   # <-- add
```

The CCC Priority weighting (CVSS 40 / EPSS 30 / KEV 20 / exploit 10) lives in the
same file — adjust it there if your source should influence the score. Enrichment
is cached in `cve_enrichment`, so keep clients side-effect-free and idempotent.

---

## 3. Add an analyst tool

`/analyst` runs **classify → plan → execute → format**. To teach it something new
you add a *tool* (a thin wrapper over an existing service) and reference it from a
plan.

1. **Write the handler** in `analyst/tool_handlers/` — reuse a repository/service,
   return plain data:

   ```python
   # analyst/tool_handlers/mytool.py
   from database import db
   async def recent_widgets(limit: int = 5) -> list[dict]:
       return await db.widgets.recent(limit)
   ```

2. **Register it** in `analyst/tool_registry.py` with its data-source label:

   ```python
   "widgets.recent": Tool("widgets.recent", "Recent widgets", SRC_DB, mytool.recent_widgets),
   ```

3. **Reference it from a plan** in `analyst/planner.py` for the relevant intent
   (or add a new intent in `analyst/intent_router.py` with a keyword rule), and
   render it in `analyst/response_formatter.py` (`_fmt_<intent>`).

The registry, planner, and formatter are validated together — every tool a plan
references must exist in the registry, and every intent needs a formatter method.

---

## Principles

- **Reuse, don't duplicate** — handlers and monitors call the same repositories
  and services the slash commands use.
- **Degrade gracefully** — a failing source/tool should be skipped, not fatal.
- **Respect the AI budget** — CPU-only Ollama runs one request at a time; keep
  LLM calls to the last step and cap `num_predict`.

See **[developer-guide.md](developer-guide.md)** for the repository pattern and
local setup, and **[phase2.md](phase2.md)** / **[phase3.md](phase3.md)** for the
monitor and fusion internals.
