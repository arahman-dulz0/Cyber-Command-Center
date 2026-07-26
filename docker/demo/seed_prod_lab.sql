-- =============================================================================
-- Production lab inventory — REAL assets only (no fake CVEs/tickets).
--
-- Apply to the LIVE database so the dashboard's exposure/assets panels correlate
-- against the genuine CVE feed already flowing in. Safe & idempotent.
--
--   docker exec -i postgres psql -U cyber -d cyberdb < docker/demo/seed_prod_lab.sql
--
-- Edit this list to match YOUR actual stack before running.
-- =============================================================================

INSERT INTO lab_assets (name, note, added_by) VALUES
('apache','Web / reverse-proxy tier','seed'),
('nginx','Ingress / static hosting','seed'),
('openssl','TLS across services','seed'),
('log4j','Java logging in app services','seed'),
('postgres','Primary datastore','seed'),
('redis','Cache / queue','seed'),
('docker','Container runtime','seed'),
('wordpress','Marketing site','seed')
ON CONFLICT (name) DO NOTHING;
