-- =============================================================================
-- Cyber Command Center — Phase 8 migration (Automation & Actioning)
-- Adds: lab_assets (your inventory) + tickets (auto-raised remediation items)
--
-- Idempotent. Applied automatically on boot (database.py). Manual:
--   docker exec -i postgres psql -U cyber -d cyberdb < docs/migrations/007_phase8.sql
-- =============================================================================

-- What's in your lab / stack (matched against CVE products + descriptions).
CREATE TABLE IF NOT EXISTS lab_assets (
    id         SERIAL PRIMARY KEY,
    name       TEXT UNIQUE NOT NULL,   -- keyword, e.g. 'vmware', 'apache', 'wordpress'
    note       TEXT,
    added_by   TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auto-raised action items when a high-priority CVE hits your lab.
CREATE TABLE IF NOT EXISTS tickets (
    id         SERIAL PRIMARY KEY,
    cve_id     TEXT NOT NULL,
    assets     TEXT[] NOT NULL DEFAULT '{}',   -- which lab assets matched
    priority   INTEGER NOT NULL DEFAULT 0,     -- CCC priority at creation
    status     TEXT NOT NULL DEFAULT 'open',   -- open | closed
    checklist  TEXT,                           -- AI-generated remediation steps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status, created_at DESC);
-- One open ticket per CVE (dedup repeated detections).
CREATE UNIQUE INDEX IF NOT EXISTS uq_tickets_open_cve ON tickets (cve_id) WHERE status = 'open';
