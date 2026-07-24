-- =============================================================================
-- Cyber Command Center — Phase 3 migration
-- Adds: cve_enrichment (threat-intelligence fusion results, 1:1 with cves.cve_id)
--
-- Idempotent. Applied automatically on boot (database.py). Manual:
--   docker exec -i postgres psql -U cyber -d cyberdb < docs/migrations/003_phase3.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS cve_enrichment (
    cve_id            TEXT PRIMARY KEY,
    epss              REAL,        -- 0..1 exploitation probability
    epss_percentile   REAL,        -- 0..1
    kev               BOOLEAN NOT NULL DEFAULT FALSE,   -- CISA Known Exploited
    kev_ransomware    BOOLEAN NOT NULL DEFAULT FALSE,
    exploitdb_count   INTEGER NOT NULL DEFAULT 0,
    exploitdb_ids     TEXT[],
    github_poc_count  INTEGER NOT NULL DEFAULT 0,
    github_poc_urls   TEXT[],
    patch_available   BOOLEAN NOT NULL DEFAULT FALSE,
    priority_score    INTEGER NOT NULL DEFAULT 0,       -- 0..100 CCC Priority
    priority_label    TEXT,                             -- CRITICAL/HIGH/MEDIUM/LOW
    ai_risk           TEXT,
    enriched_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_enrich_priority ON cve_enrichment (priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_enrich_kev      ON cve_enrichment (kev);
