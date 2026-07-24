-- =============================================================================
-- Cyber Command Center — PostgreSQL schema (Phase 1)
-- Database: cyberdb   User: cyber
--
-- The bot runs these statements automatically on startup (see database.py),
-- but you can also apply them manually:
--   psql -h 192.168.8.185 -U cyber -d cyberdb -f docs/schema.sql
-- =============================================================================

-- Store fetched CVEs (also acts as a cache for the /cve command).
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
CREATE INDEX IF NOT EXISTS idx_cves_cve_id    ON cves (cve_id);
CREATE INDEX IF NOT EXISTS idx_cves_severity  ON cves (severity);
CREATE INDEX IF NOT EXISTS idx_cves_published ON cves (published_date DESC);

-- Store fetched news articles.
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
CREATE INDEX IF NOT EXISTS idx_news_url       ON news_articles (url);
CREATE INDEX IF NOT EXISTS idx_news_source    ON news_articles (source);
CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles (published_date DESC);

-- Store bot command usage logs.
CREATE TABLE IF NOT EXISTS command_logs (
    id         SERIAL PRIMARY KEY,
    user_id    BIGINT,
    username   TEXT,
    command    TEXT,
    guild_id   BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cmdlogs_command ON command_logs (command);
CREATE INDEX IF NOT EXISTS idx_cmdlogs_created ON command_logs (created_at DESC);
