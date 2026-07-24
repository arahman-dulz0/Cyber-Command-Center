-- =============================================================================
-- Cyber Command Center — Phase 2 migration
-- Adds: monitor_runs, ai_summaries, ai_metrics
--
-- Idempotent. The bot applies this automatically on startup (database.py), but
-- it can also be run manually:
--   psql -h 192.168.8.185 -U cyber -d cyberdb -f docs/migrations/002_phase2.sql
-- (Or, since Postgres is only on the docker network:)
--   docker exec -i postgres psql -U cyber -d cyberdb < docs/migrations/002_phase2.sql
-- =============================================================================

-- Background-task run history + monitoring state.
CREATE TABLE IF NOT EXISTS monitor_runs (
    id           SERIAL PRIMARY KEY,
    task         TEXT NOT NULL,
    started      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished     TIMESTAMPTZ,
    status       TEXT NOT NULL DEFAULT 'running',   -- running | success | error
    items_found  INTEGER NOT NULL DEFAULT 0,
    items_posted INTEGER NOT NULL DEFAULT 0,
    errors       TEXT,
    last_success TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_monruns_task    ON monitor_runs (task, started DESC);
CREATE INDEX IF NOT EXISTS idx_monruns_success ON monitor_runs (task, last_success DESC);

-- AI summary cache — never summarise the same content twice.
CREATE TABLE IF NOT EXISTS ai_summaries (
    content_hash TEXT PRIMARY KEY,   -- sha256(model + '\0' + prompt)
    model        TEXT NOT NULL,
    summary      TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- AI call metrics — powers /stats (count + average response time).
CREATE TABLE IF NOT EXISTS ai_metrics (
    id         SERIAL PRIMARY KEY,
    kind       TEXT NOT NULL,        -- cve | news | tip | ask
    model      TEXT,
    elapsed_ms INTEGER NOT NULL DEFAULT 0,
    cache_hit  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_aimetrics_created ON ai_metrics (created_at DESC);
