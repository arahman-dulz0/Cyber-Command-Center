"""CVE tool handlers — reuse the CVE DB, fusion enrichment, and live NVD/fusion."""

from __future__ import annotations

from typing import Any

from database import db
from enrichment import fusion
from utils.nvd_client import CVENotFound, NVDError, nvd

from analyst.tool_handlers.common import recent_enriched_cves


async def counts_24h() -> dict[str, Any]:
    cves = await db.cves.count_since(24)
    news = await db.news.count_since(24)
    crit = await db.cves.count_by_severity_since("CRITICAL", 24)
    high = await db.cves.count_by_severity_since("HIGH", 24)
    kev = await db.enrichment.count_kev_since(24)
    exploited = await db.enrichment.count_exploited_since(24)
    top = await db.enrichment.max_priority_since(24)
    return {
        "cves": cves, "news": news, "critical": crit, "high": high,
        "kev": kev, "exploited": exploited, "top_priority": top,
    }


async def top_priority(limit: int = 5) -> list[dict[str, Any]]:
    return await recent_enriched_cves(days=7, min_score=7.0, limit=limit)


async def critical(hours: int = 48) -> list[dict[str, Any]]:
    rows = await recent_enriched_cves(days=max(1, hours // 24), min_score=7.0, limit=30)
    return [r for r in rows if (r.get("priority_label") == "CRITICAL") or (r.get("cvss_score") or 0) >= 9.0]


async def kev(limit: int = 10) -> list[dict[str, Any]]:
    rows = await recent_enriched_cves(days=30, min_score=0.0, limit=100)
    return [r for r in rows if r.get("kev")][:limit]


async def pocs(limit: int = 10) -> list[dict[str, Any]]:
    rows = await recent_enriched_cves(days=14, min_score=0.0, limit=100)
    got = [r for r in rows if (r.get("github_poc_count") or 0) > 0 or (r.get("exploitdb_count") or 0) > 0]
    return got[:limit]


async def get(cve_id: str) -> dict[str, Any] | None:
    """Full CVE picture: stored data + enrichment; falls back to a live fetch."""
    cve_id = cve_id.upper()
    stored = await db.cves.get(cve_id)
    enr = await db.enrichment.get(cve_id)

    if stored is None:
        # Not in our DB — fetch live from NVD and enrich on the fly.
        try:
            data = await nvd.fetch_cve(cve_id)
        except (CVENotFound, NVDError):
            return None
        stored = {
            "cve_id": data.cve_id, "description": data.description,
            "cvss_score": data.cvss_score, "severity": data.severity,
            "published_date": data.published, "products": data.products,
        }
        if enr is None:
            e = await fusion.enrich_one({
                "cve_id": data.cve_id, "cvss_score": data.cvss_score,
                "severity": data.severity, "references": data.references,
            })
            enr = {
                "priority_score": e.priority_score, "priority_label": e.priority_label,
                "kev": e.kev, "kev_ransomware": e.kev_ransomware, "epss": e.epss,
                "github_poc_count": e.github_poc_count, "exploitdb_count": e.exploitdb_count,
                "patch_available": e.patch_available, "ai_risk": e.ai_risk,
            }
    return {**stored, **(enr or {})}
