-- =============================================================================
-- Cyber Command Center — Phase 5 migration (RAG Knowledge Base)
-- Adds: kb_documents + kb_chunks (embeddings stored as float8[]; cosine done in
-- Python since the postgres:16 image has no pgvector).
--
-- Idempotent. Applied automatically on boot (database.py). Manual:
--   docker exec -i postgres psql -U cyber -d cyberdb < docs/migrations/005_phase5.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS kb_documents (
    id           SERIAL PRIMARY KEY,
    title        TEXT NOT NULL,
    source_type  TEXT NOT NULL DEFAULT 'note',  -- pdf | md | txt | note | writeup
    source_ref   TEXT,                          -- filename / url / origin
    content_hash TEXT UNIQUE NOT NULL,          -- dedup key (sha256 of raw text)
    added_by     TEXT,
    chunk_count  INTEGER NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kb_chunks (
    id          SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    embedding   FLOAT8[] NOT NULL,              -- 768-dim (nomic-embed-text)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_kbchunks_doc ON kb_chunks (document_id);
