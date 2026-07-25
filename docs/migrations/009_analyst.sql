-- =============================================================================
-- Cyber Command Center — AI Analyst interaction log
-- Records every natural-language analyst interaction (query, resolved intent,
-- tools invoked, latency) for observability and audit.
--
-- Idempotent. Applied automatically on boot (database.py).
-- =============================================================================

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
