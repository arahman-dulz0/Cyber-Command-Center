-- =============================================================================
-- Cyber Command Center — audit log (security hardening)
-- Records administrative and security-relevant actions from both the Discord
-- bot and the dashboard (logins, config changes, ticket changes, manual runs).
--
-- Idempotent. Applied automatically on boot (database.py).
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id         SERIAL PRIMARY KEY,
    actor      TEXT,                    -- who: discord username, 'dashboard', 'system'
    action     TEXT NOT NULL,           -- what: monitor.run, ticket.close, cog.reload, auth.login, auth.fail, lab.add …
    target     TEXT,                    -- object acted on
    detail     TEXT,
    source     TEXT NOT NULL DEFAULT 'discord',  -- discord | dashboard | system
    ip         TEXT,                    -- for dashboard events
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action  ON audit_log (action);
