"""Report tool handlers — reuse the multi-agent crew (exec) + fusion data (tech)."""

from __future__ import annotations

from typing import Any

from database import db
from utils import embeds

from analyst.tool_handlers.common import recent_enriched_cves
from analyst.tool_handlers import assets as asset_tools


async def executive() -> dict[str, Any]:
    """Run the agent crew for an executive report and persist it (reuses cogs.reports)."""
    from cogs.reports import run_and_store

    now = embeds.now_local().strftime("%Y-%m-%d %H:%M")
    report = await run_and_store(f"Executive Intelligence Report — {now}")
    return {"kind": "executive", "report": report}


async def technical() -> dict[str, Any]:
    """A structured technical report built deterministically from fusion data."""
    top = await recent_enriched_cves(days=7, min_score=7.0, limit=8)
    affected = await asset_tools.affected()
    counts = {
        "critical": await db.cves.count_by_severity_since("CRITICAL", 24),
        "kev": await db.enrichment.count_kev_since(24),
        "exploited": await db.enrichment.count_exploited_since(24),
    }
    return {"kind": "technical", "top": top, "affected": affected, "counts": counts}
