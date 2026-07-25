"""
PostgreSQL access layer.

Owns the asyncpg connection pool, ensures the schema exists on startup, and
exposes the repository instances (repository pattern). Phase-1 convenience
methods are retained and now delegate to the repositories so existing cogs keep
working unchanged.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import asyncpg

from config import config
from repositories import (
    AIRepository,
    AuditRepository,
    CommandRepository,
    CVERepository,
    EnrichmentRepository,
    KBRepository,
    LabRepository,
    MachineRepository,
    MonitorRepository,
    NewsRepository,
    PracticeRepository,
    ReportRepository,
    TicketRepository,
)
from utils.logger import db_log as log

# --- Schema ---------------------------------------------------------------
# Kept in sync with docs/schema.sql and docs/migrations/002_phase2.sql.
# Every statement is idempotent so the bot can run it on each boot. This DB is
# shared with n8n, so we only ever touch our own tables.
_SCHEMA = """
CREATE TABLE IF NOT EXISTS cves (
    id                SERIAL PRIMARY KEY,
    cve_id            TEXT UNIQUE NOT NULL,
    title             TEXT,
    description       TEXT,
    cvss_score        REAL,
    severity          TEXT,
    published_date    TIMESTAMPTZ,
    ai_summary        TEXT,
    posted_to_discord BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cves_cve_id      ON cves (cve_id);
CREATE INDEX IF NOT EXISTS idx_cves_severity    ON cves (severity);
CREATE INDEX IF NOT EXISTS idx_cves_published   ON cves (published_date DESC);

CREATE TABLE IF NOT EXISTS news_articles (
    id                SERIAL PRIMARY KEY,
    title             TEXT NOT NULL,
    url               TEXT UNIQUE NOT NULL,
    source            TEXT,
    description       TEXT,
    ai_summary        TEXT,
    published_date    TIMESTAMPTZ,
    posted_to_discord BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_news_url         ON news_articles (url);
CREATE INDEX IF NOT EXISTS idx_news_source      ON news_articles (source);
CREATE INDEX IF NOT EXISTS idx_news_published   ON news_articles (published_date DESC);

CREATE TABLE IF NOT EXISTS command_logs (
    id         SERIAL PRIMARY KEY,
    user_id    BIGINT,
    username   TEXT,
    command    TEXT,
    guild_id   BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cmdlogs_command  ON command_logs (command);
CREATE INDEX IF NOT EXISTS idx_cmdlogs_created  ON command_logs (created_at DESC);

-- Phase 2 -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS monitor_runs (
    id           SERIAL PRIMARY KEY,
    task         TEXT NOT NULL,
    started      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished     TIMESTAMPTZ,
    status       TEXT NOT NULL DEFAULT 'running',
    items_found  INTEGER NOT NULL DEFAULT 0,
    items_posted INTEGER NOT NULL DEFAULT 0,
    errors       TEXT,
    last_success TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_monruns_task    ON monitor_runs (task, started DESC);
CREATE INDEX IF NOT EXISTS idx_monruns_success ON monitor_runs (task, last_success DESC);

CREATE TABLE IF NOT EXISTS ai_summaries (
    content_hash TEXT PRIMARY KEY,
    model        TEXT NOT NULL,
    summary      TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_metrics (
    id         SERIAL PRIMARY KEY,
    kind       TEXT NOT NULL,
    model      TEXT,
    elapsed_ms INTEGER NOT NULL DEFAULT 0,
    cache_hit  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_aimetrics_created ON ai_metrics (created_at DESC);

-- Phase 3 -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cve_enrichment (
    cve_id            TEXT PRIMARY KEY,
    epss              REAL,
    epss_percentile   REAL,
    kev               BOOLEAN NOT NULL DEFAULT FALSE,
    kev_ransomware    BOOLEAN NOT NULL DEFAULT FALSE,
    exploitdb_count   INTEGER NOT NULL DEFAULT 0,
    exploitdb_ids     TEXT[],
    github_poc_count  INTEGER NOT NULL DEFAULT 0,
    github_poc_urls   TEXT[],
    patch_available   BOOLEAN NOT NULL DEFAULT FALSE,
    priority_score    INTEGER NOT NULL DEFAULT 0,
    priority_label    TEXT,
    ai_risk           TEXT,
    enriched_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_enrich_priority ON cve_enrichment (priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_enrich_kev      ON cve_enrichment (kev);

-- Phase 4 -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS practice_log (
    id           SERIAL PRIMARY KEY,
    user_id      BIGINT,
    username     TEXT,
    machine      TEXT NOT NULL,
    platform     TEXT NOT NULL DEFAULT 'HTB',
    skills       TEXT[] NOT NULL DEFAULT '{}',
    difficulty   TEXT,
    notes        TEXT,
    source       TEXT NOT NULL DEFAULT 'manual',
    practiced_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_practice_when   ON practice_log (practiced_at DESC);
CREATE INDEX IF NOT EXISTS idx_practice_skills ON practice_log USING GIN (skills);

CREATE TABLE IF NOT EXISTS htb_machines (
    machine_id   INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    os           TEXT,
    difficulty   TEXT,
    points       INTEGER,
    retired      BOOLEAN NOT NULL DEFAULT FALSE,
    active       BOOLEAN NOT NULL DEFAULT FALSE,
    release_date TIMESTAMPTZ,
    skill_areas  TEXT[] NOT NULL DEFAULT '{}',
    user_owned   BOOLEAN NOT NULL DEFAULT FALSE,
    root_owned   BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_htb_os    ON htb_machines (os);
CREATE INDEX IF NOT EXISTS idx_htb_owned ON htb_machines (user_owned, root_owned);

-- Phase 5 -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kb_documents (
    id           SERIAL PRIMARY KEY,
    title        TEXT NOT NULL,
    source_type  TEXT NOT NULL DEFAULT 'note',
    source_ref   TEXT,
    content_hash TEXT UNIQUE NOT NULL,
    added_by     TEXT,
    chunk_count  INTEGER NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kb_chunks (
    id          SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    embedding   FLOAT8[] NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_kbchunks_doc ON kb_chunks (document_id);

-- Phase 7 -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    id         SERIAL PRIMARY KEY,
    title      TEXT NOT NULL,
    summary    TEXT,
    content    TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports (created_at DESC);

-- Phase 8 -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lab_assets (
    id         SERIAL PRIMARY KEY,
    name       TEXT UNIQUE NOT NULL,
    note       TEXT,
    added_by   TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tickets (
    id         SERIAL PRIMARY KEY,
    cve_id     TEXT NOT NULL,
    assets     TEXT[] NOT NULL DEFAULT '{}',
    priority   INTEGER NOT NULL DEFAULT 0,
    status     TEXT NOT NULL DEFAULT 'open',
    checklist  TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status, created_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS uq_tickets_open_cve ON tickets (cve_id) WHERE status = 'open';

-- Security: audit log ------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_log (
    id         SERIAL PRIMARY KEY,
    actor      TEXT,
    action     TEXT NOT NULL,
    target     TEXT,
    detail     TEXT,
    source     TEXT NOT NULL DEFAULT 'discord',
    ip         TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action  ON audit_log (action);
"""


class Database:
    """Thin async wrapper around an asyncpg pool + the repository instances."""

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None
        # Repositories (populated in init()).
        self.cves: CVERepository | None = None
        self.news: NewsRepository | None = None
        self.monitors: MonitorRepository | None = None
        self.commands: CommandRepository | None = None
        self.ai: AIRepository | None = None
        self.enrichment: EnrichmentRepository | None = None
        self.practice: PracticeRepository | None = None
        self.machines: MachineRepository | None = None
        self.kb: KBRepository | None = None
        self.reports: ReportRepository | None = None
        self.lab: LabRepository | None = None
        self.tickets: TicketRepository | None = None
        self.audit: AuditRepository | None = None

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Database pool is not initialised. Call init() first.")
        return self._pool

    async def init(self) -> None:
        """Create the connection pool, ensure the schema, and wire repositories."""
        self._pool = await asyncpg.create_pool(
            dsn=config.postgres_dsn,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
        async with self._pool.acquire() as conn:
            await conn.execute(_SCHEMA)

        self.cves = CVERepository(self._pool)
        self.news = NewsRepository(self._pool)
        self.monitors = MonitorRepository(self._pool)
        self.commands = CommandRepository(self._pool)
        self.ai = AIRepository(self._pool)
        self.enrichment = EnrichmentRepository(self._pool)
        self.practice = PracticeRepository(self._pool)
        self.machines = MachineRepository(self._pool)
        self.kb = KBRepository(self._pool)
        self.reports = ReportRepository(self._pool)
        self.lab = LabRepository(self._pool)
        self.tickets = TicketRepository(self._pool)
        self.audit = AuditRepository(self._pool)
        log.info("PostgreSQL pool ready, schema ensured, repositories wired.")

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            log.info("PostgreSQL pool closed.")

    async def ping(self) -> None:
        """Raise if the database is unreachable (used by /status)."""
        async with self.pool.acquire() as conn:
            await conn.execute("SELECT 1;")

    async def database_size_pretty(self) -> str:
        """Human-readable size of the current database (used by /stats)."""
        return await self.pool.fetchval("SELECT pg_size_pretty(pg_database_size(current_database()));")

    # =====================================================================
    # Backward-compatible Phase-1 helpers (delegate to repositories).
    # =====================================================================
    async def log_command(self, *, user_id: int, username: str, command: str, guild_id: int | None) -> None:
        await self.commands.log(user_id=user_id, username=username, command=command, guild_id=guild_id)

    async def get_cached_cve(self, cve_id: str) -> dict[str, Any] | None:
        return await self.cves.get(cve_id)

    async def upsert_cve(
        self,
        *,
        cve_id: str,
        title: str | None,
        description: str | None,
        cvss_score: float | None,
        severity: str | None,
        published_date: datetime | None,
        ai_summary: str | None,
    ) -> None:
        await self.cves.upsert(
            cve_id=cve_id, title=title, description=description, cvss_score=cvss_score,
            severity=severity, published_date=published_date, ai_summary=ai_summary,
        )

    async def recent_critical_cves(self, hours: int = 24) -> list[dict[str, Any]]:
        return await self.cves.recent_critical(hours=hours, min_score=config.cve_min_score)

    async def upsert_news(
        self,
        *,
        title: str,
        url: str,
        source: str | None,
        description: str | None,
        ai_summary: str | None,
        published_date: datetime | None,
    ) -> None:
        await self.news.upsert(
            title=title, url=url, source=source, description=description,
            ai_summary=ai_summary, published_date=published_date,
        )


# Shared instance.
db = Database()
