# Phase 3 — Threat Intelligence Fusion Engine

Phase 3 turns a raw CVE into a **prioritised, correlated threat alert**. Instead of
`CVE → Discord`, each CVE is enriched through multiple free intelligence sources,
scored, risk-analysed by the local AI, and only then posted.

```
CVE → EPSS → CISA KEV → ExploitDB → GitHub PoCs → Vendor patch → AI risk → Priority → Discord
```

## The alert

```
🚨 CRITICAL — CVE-2021-44228            [CCC Priority 100/100]
CVSS 10.0 (CRITICAL) · EPSS 99% · Known Exploited ✅ 🦠 ransomware
Exploit Available ✅ · GitHub PoC 413 repos · ExploitDB 3 · Vendor Patch Available
🤖 AI Risk Analysis: … immediate patch recommended, public exploit exists, active exploitation observed.
```

## Sources (all free, no new dependencies)

| Source | What it adds | Notes |
|--------|--------------|-------|
| **EPSS** (FIRST.org) | Exploitation probability (`97%`) | Batched API, no auth |
| **CISA KEV** | "Known Exploited" + ransomware flag | Cached catalog, refresh `KEV_REFRESH_HOURS` |
| **ExploitDB** | Public exploit count | CSV index, refresh `EXPLOITDB_REFRESH_HOURS` |
| **GitHub PoCs** | PoC repo count | Curated PoC-in-GitHub dataset, no auth |
| **Vendor patch** | Patch availability | Derived from NVD `Patch` reference tag |
| **AI risk** | 2-3 sentence analysis + recommendation | Local Ollama, cached |

> Honesty note: "active exploitation" == CISA KEV membership (the authoritative
> free signal); true threat-actor attribution needs paid TI and is intentionally
> not faked. Vendor-patch is best-effort from NVD reference tags.

## Priority score (0-100 "CCC Priority")

```
CVSS    → up to 40   (cvss/10 × 40)
EPSS    → up to 30   (epss × 30)
KEV     → +20        (actively exploited)
Exploit → +10        (ExploitDB entry or GitHub PoC)
```
Labels: **CRITICAL** ≥ 80 · **HIGH** ≥ 60 · **MEDIUM** ≥ 40 · **LOW** < 40. The
label drives the embed colour, and alerts are posted highest-priority first.

## Architecture

```
enrichment/                 ← pluggable intelligence layer (NEW)
├── base.py                 ← Enrichment dataclass
├── epss.py                 ← EPSSClient (batched)
├── kev.py                  ← KEVClient (cached catalog)
├── exploitdb.py            ← ExploitDBClient (cached CSV)
├── github_poc.py           ← GitHubPoCClient (curated dataset)
└── fusion.py               ← FusionEngine: correlate → score → AI risk
```

Enrichment slots into the existing CVE pipeline: `cve_monitor.process()` selects the
unposted backlog, fuses each item, stores the result in `cve_enrichment`, and
`post()` renders the fused embed. **`/cve` does the same on demand.** Scheduler
unchanged.

### Adding a new intelligence source

Write a client in `enrichment/`, add one lookup line in `FusionEngine.enrich_many`,
and (optionally) a scoring term. Nothing else changes — this is the "extensible
plugin architecture" in practice.

## Database

New table `cve_enrichment` (1:1 with `cves.cve_id`) — see
`docs/migrations/003_phase3.sql`; applied automatically on boot. Stores EPSS, KEV
flags, exploit/PoC counts + URLs, patch flag, priority score/label, and the AI risk
text. `/stats` now also reports KEVs, exploited count, and top priority (24h).

## Configuration (`.env`)

```
ENRICHMENT_ENABLED=true       # master switch (false → Phase-2 basic alerts)
KEV_REFRESH_HOURS=6
EXPLOITDB_REFRESH_HOURS=24
# Optional source overrides: EPSS_URL, KEV_URL, EXPLOITDB_CSV_URL, GITHUB_POC_BASE
```

## Testing checklist

- [ ] `#cve-alert` shows fused embeds with a CCC Priority, EPSS %, KEV/exploit flags, PoC count.
- [ ] `/cve CVE-2021-44228` returns a Priority-100 CRITICAL fused embed.
- [ ] Highest-priority CVEs post first.
- [ ] `cve_enrichment` rows are populated; `/stats` shows KEVs / Exploited / Top priority.
- [ ] KEV + ExploitDB catalogs load once and refresh on their intervals (see logs).
- [ ] With a source down, the alert still posts (degraded fields), never blocking.

## Rollback

```
# Disable fusion, keep everything else (reverts to Phase-2 basic CVE alerts):
ENRICHMENT_ENABLED=false   # in .env, then: docker compose -f docker/bot.yml up -d
# Or drop the table (harmless to leave):
#   docker exec -i postgres psql -U cyber -d cyberdb -c "DROP TABLE IF EXISTS cve_enrichment;"
```
