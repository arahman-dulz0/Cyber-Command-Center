"""System / posture tool handler — aggregate live platform metrics."""

from __future__ import annotations

from typing import Any

from database import db


async def status() -> dict[str, Any]:
    """A snapshot of platform health and threat posture."""
    kev_24 = await db.enrichment.count_kev_since(24)
    max_priority = await db.enrichment.max_priority_since(24)
    critical_24 = await db.cves.count_by_severity_since("CRITICAL", 24)

    # Threat level derived from the last 24h.
    if kev_24 > 0 or max_priority >= 80:
        level, color_key = "ELEVATED", "critical"
    elif critical_24 > 0 or max_priority >= 60:
        level, color_key = "GUARDED", "high"
    else:
        level, color_key = "STABLE", "low"

    return {
        "threat_level": level,
        "color_key": color_key,
        "cves_24h": await db.cves.count_since(24),
        "critical_24h": critical_24,
        "kev_24h": kev_24,
        "max_priority_24h": max_priority,
        "news_24h": await db.news.count_since(24),
        "open_tickets": await db.tickets.open_count(),
        "lab_assets": await db.lab.total(),
        "total_cves": await db.cves.total(),
        "kb_documents": await db.kb.total_documents(),
        "commands_24h": await db.commands.count_since(24),
    }
