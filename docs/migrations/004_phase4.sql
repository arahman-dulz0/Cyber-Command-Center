-- =============================================================================
-- Cyber Command Center — Phase 4 migration (Learning Intelligence)
-- Adds: practice_log (manual study journal) + htb_machines (HTB catalog + owns)
--
-- Idempotent. Applied automatically on boot (database.py). Manual:
--   docker exec -i postgres psql -U cyber -d cyberdb < docs/migrations/004_phase4.sql
-- =============================================================================

-- What you've practiced (from /practiced and, optionally, HTB own-imports).
CREATE TABLE IF NOT EXISTS practice_log (
    id           SERIAL PRIMARY KEY,
    user_id      BIGINT,
    username     TEXT,
    machine      TEXT NOT NULL,
    platform     TEXT NOT NULL DEFAULT 'HTB',   -- HTB | TryHackMe | CTF | other
    skills       TEXT[] NOT NULL DEFAULT '{}',   -- e.g. {linux, privesc, kerberoasting}
    difficulty   TEXT,
    notes        TEXT,
    source       TEXT NOT NULL DEFAULT 'manual', -- manual | htb-import
    practiced_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_practice_when   ON practice_log (practiced_at DESC);
CREATE INDEX IF NOT EXISTS idx_practice_skills ON practice_log USING GIN (skills);

-- HTB machine catalog (from the HTB API) plus your own status + AI skill areas.
CREATE TABLE IF NOT EXISTS htb_machines (
    machine_id   INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    os           TEXT,
    difficulty   TEXT,
    points       INTEGER,
    retired      BOOLEAN NOT NULL DEFAULT FALSE,
    active       BOOLEAN NOT NULL DEFAULT FALSE,
    release_date TIMESTAMPTZ,
    skill_areas  TEXT[] NOT NULL DEFAULT '{}',   -- AI-derived technique tags
    user_owned   BOOLEAN NOT NULL DEFAULT FALSE, -- user flag captured
    root_owned   BOOLEAN NOT NULL DEFAULT FALSE, -- root/system flag captured
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_htb_os        ON htb_machines (os);
CREATE INDEX IF NOT EXISTS idx_htb_owned     ON htb_machines (user_owned, root_owned);
