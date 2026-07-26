-- =============================================================================
-- Cyber Command Center — complete database schema (demo init)
--
-- Runs automatically on FIRST Postgres init (docker-entrypoint-initdb.d) for the
-- self-contained demo stack. Idempotent (CREATE ... IF NOT EXISTS), so it is
-- harmless if the Discord bot (profile: full) later applies its own schema.
--
-- SOURCE OF TRUTH: services/discord-bot/database.py `_SCHEMA`. Keep in sync.
-- =============================================================================

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

CREATE TABLE IF NOT EXISTS reports (
    id         SERIAL PRIMARY KEY,
    title      TEXT NOT NULL,
    summary    TEXT,
    content    TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports (created_at DESC);

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

CREATE TABLE IF NOT EXISTS analyst_log (
    id         SERIAL PRIMARY KEY,
    user_id    BIGINT,
    username   TEXT,
    query      TEXT NOT NULL,
    intent     TEXT,
    tools      TEXT[] NOT NULL DEFAULT '{}',
    sources    TEXT[] NOT NULL DEFAULT '{}',
    used_llm   BOOLEAN NOT NULL DEFAULT FALSE,
    elapsed_ms INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_analystlog_created ON analyst_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analystlog_intent  ON analyst_log (intent);
