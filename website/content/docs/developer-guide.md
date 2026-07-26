# Developer guide

How the codebase is laid out, the patterns it follows, and how to work on it
locally. For extending specific subsystems see **[plugins.md](plugins.md)**.

---

## Repository layout

```
Cyber-Command-Center/
├── docker-compose.yml         # top-level, self-contained (demo + --profile full)
├── docker/                    # live-server compose (bot/dashboard/ops) + demo seed
│   ├── bot.yml dashboard.yml ops.yml
│   └── demo/initdb/           # 01_schema.sql + 02_seed.sql (auto-run on init)
├── services/
│   ├── discord-bot/           # the platform (Python 3.11)
│   └── dashboard/             # FastAPI read-only web UI
├── website/                   # Next.js 16 marketing site
├── scripts/                   # deploy, backup, restore, validate-env, update…
├── docs/                      # this documentation
└── knowledge/                 # bulk KB ingest folder (bind-mounted)
```

### Bot internals (`services/discord-bot/`)

```
bot.py            # entrypoint: loads cogs, starts scheduler, syncs commands
config.py         # env-driven config (dataclass, sensible defaults)
database.py       # asyncpg pool + _SCHEMA + wires all repositories
repositories/     # one class per table-group; ALL DB access goes through here
cogs/             # discord.py command groups (one file per feature area)
tasks/            # autonomous monitors + scheduler (Phase 2)
enrichment/       # threat-intel fusion: EPSS/KEV/ExploitDB/PoC (Phase 3)
learning/         # HTB import + practice recommender (Phase 4)
knowledge/        # RAG: chunking, embeddings, retriever (Phase 5)
agents/           # multi-agent report crew (Phase 7)
actioning/        # lab-match → ticket → escalate (Phase 8)
analyst/          # AI Security Analyst orchestration (intent→plan→execute→format)
utils/            # embeds, ollama client, nvd client, logger, validation
```

---

## Core patterns

### The repository pattern

**All database access goes through a repository** — cogs, monitors, and analyst
tools never write SQL inline. `database.py` owns the pool and instantiates one
repository per table-group, exposed as `db.<name>`:

```python
from database import db
await db.cves.recent_critical(hours=24, min_score=7.0)
await db.tickets.open_tickets(limit=15)
await db.lab.names()
```

Add a new table-group by subclassing `BaseRepository` (`repositories/base.py`),
adding it to `_SCHEMA`, and wiring it in `Database.init()`.

### Configuration

Everything is env-driven through `config.py` (a dataclass with defaults). Never
read `os.getenv` scattered through the code — add a field to `config` and
reference `config.<name>`. Secrets live only in `.env` (gitignored).

### AI calls

Go through `utils/ollama_client.ollama`. It uses `/api/chat`, caps `num_predict`,
retries, and respects a concurrency semaphore. On CPU-only hosts keep
`OLLAMA_MAX_CONCURRENCY=1`. Always make the LLM the **last** step — search
platform data first.

### Embeds

Every Discord embed is built via `utils/embeds` helpers (`base_embed`,
`severity_color`, `build_fused_cve_embed`, …) so the look stays consistent.

---

## Local development

The bot needs Postgres, Redis, and Ollama. The fastest full-stack loop:

```bash
cp .env.example .env               # set DISCORD_TOKEN + DISCORD_GUILD_ID
docker compose --profile full up -d --build
docker compose exec ollama ollama pull qwen2.5:3b
docker compose exec ollama ollama pull nomic-embed-text
docker compose logs -f discord-bot
```

Iterating on the **dashboard** only? Its own stack is enough:

```bash
docker compose up -d               # postgres (seeded) + dashboard
# edit services/dashboard/*, then:
docker compose up -d --build dashboard
```

Quick checks without a full run:

```bash
python -m py_compile services/dashboard/app.py services/dashboard/db.py
# byte-compile the bot package before deploying
cd services/discord-bot && python -m py_compile **/*.py
```

The dashboard's `templates/index.html` is loaded once at import — **restart the
container** to see template changes.

---

## Deploying

- **Live server** (existing Postgres/Redis/Ollama on `docker_cyber-net`):
  `./scripts/deploy.sh` (bot) and `docker compose -f docker/dashboard.yml up -d
  --build` (dashboard). `docker restart` reuses the old image — always
  `up -d --build`.
- **Standalone / demo**: the top-level `docker-compose.yml`.

Run `scripts/validate-env.sh` first to preflight required vars + service
reachability. See **[operations.md](operations.md)** for backups, health, and
safe updates, and **[security.md](security.md)** for the hardening model.

---

## Conventions

- Match the surrounding style — comment density, naming, and idiom.
- Reuse existing services/repositories rather than duplicating logic.
- Fail gracefully: an optional source/tool that errors is skipped, not fatal.
- Never commit `.env`; scan diffs for secrets before pushing.
