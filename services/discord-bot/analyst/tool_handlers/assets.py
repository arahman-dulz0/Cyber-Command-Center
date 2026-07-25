"""
Asset-correlation tool handlers — the platform's key differentiator.

Correlates the user's lab inventory against threat intelligence:
open tickets (authoritative CVE↔asset matches from the action engine) plus a scan
of recent high-priority CVE descriptions for asset keywords.
"""

from __future__ import annotations

from typing import Any

from database import db

from analyst.tool_handlers.common import recent_enriched_cves, word_match


def _risk_from_priority(p: int | None) -> str:
    p = p or 0
    if p >= 80:
        return "Critical"
    if p >= 60:
        return "High"
    if p >= 40:
        return "Medium"
    return "Low"


async def affected() -> dict[str, Any]:
    """Every lab asset with the CVEs that affect it (tickets + recent-CVE scan)."""
    names = await db.lab.names()
    if not names:
        return {"assets": {}, "total_assets": 0, "note": "no lab inventory — add with /lab add"}

    by_asset: dict[str, list[dict]] = {n: [] for n in names}

    for t in await db.tickets.open_tickets(limit=50):
        for a in t.get("assets", []):
            if a in by_asset and not any(x["cve_id"] == t["cve_id"] for x in by_asset[a]):
                by_asset[a].append({
                    "cve_id": t["cve_id"], "priority": t["priority"],
                    "risk": _risk_from_priority(t["priority"]), "source": "ticket",
                })

    for c in await recent_enriched_cves(days=14, min_score=7.0, limit=80):
        desc = c.get("description") or ""
        for a in names:
            if word_match(a, desc) and not any(x["cve_id"] == c["cve_id"] for x in by_asset[a]):
                by_asset[a].append({
                    "cve_id": c["cve_id"], "priority": c.get("priority_score") or 0,
                    "risk": _risk_from_priority(c.get("priority_score")),
                    "severity": c.get("severity"), "source": "cve",
                })

    affected = {a: sorted(v, key=lambda x: x["priority"], reverse=True) for a, v in by_asset.items() if v}
    return {"assets": affected, "total_assets": len(names)}


async def by_cve(cve_id: str) -> dict[str, Any]:
    """Which lab assets a specific CVE affects."""
    from analyst.tool_handlers import cves as cve_tools

    cve = await cve_tools.get(cve_id)
    if cve is None:
        return {"cve": None, "matched": []}
    names = await db.lab.names()
    hay = (cve.get("description") or "") + " " + " ".join(cve.get("products") or [])
    matched = [n for n in names if word_match(n, hay)]
    # An open ticket is authoritative too.
    for t in await db.tickets.open_tickets(limit=50):
        if t["cve_id"].upper() == cve_id.upper():
            matched = sorted(set(matched) | set(t.get("assets", [])))
    return {"cve": cve, "matched": matched, "has_inventory": bool(names)}


async def by_product(product: str) -> dict[str, Any]:
    """CVEs affecting a named product, and whether it's in the lab."""
    names = await db.lab.names()
    in_lab = product.lower() in names
    hits = []
    for c in await recent_enriched_cves(days=30, min_score=7.0, limit=100):
        if word_match(product, c.get("description") or ""):
            hits.append(c)
    return {"product": product, "in_lab": in_lab, "cves": hits[:10]}


async def list_assets() -> list[dict[str, Any]]:
    return await db.lab.all()
