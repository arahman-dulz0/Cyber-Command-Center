-- =============================================================================
-- Cyber Command Center — Phase 7 migration (Multi-Agent Intelligence Reports)
-- Adds: reports (agent-crew output, surfaced on the dashboard)
--
-- Idempotent. Applied automatically on boot (database.py). Manual:
--   docker exec -i postgres psql -U cyber -d cyberdb < docs/migrations/006_phase7.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS reports (
    id         SERIAL PRIMARY KEY,
    title      TEXT NOT NULL,
    summary    TEXT,          -- Report Writer's executive summary
    content    TEXT,          -- full multi-section report
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports (created_at DESC);
