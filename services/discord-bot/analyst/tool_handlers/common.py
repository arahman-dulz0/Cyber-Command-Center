"""Shared helpers for analyst tool handlers."""

from __future__ import annotations

import re
from typing import Any

from database import db


def word_match(keyword: str, text: str) -> bool:
    if not keyword or not text:
        return False
    return re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE) is not None


async def recent_enriched_cves(
    *, days: int = 7, min_score: float = 7.0, limit: int = 50
) -> list[dict[str, Any]]:
    """Recent CVEs joined with their fusion enrichment, priority-sorted."""
    rows = await db.pool.fetch(
        """
        SELECT c.cve_id, c.description, c.cvss_score, c.severity, c.published_date,
               e.priority_score, e.priority_label, e.kev, e.kev_ransomware,
               e.epss, e.github_poc_count, e.exploitdb_count, e.patch_available, e.ai_risk
        FROM cves c
        LEFT JOIN cve_enrichment e ON e.cve_id = c.cve_id
        WHERE c.created_at >= NOW() - ($1::text || ' days')::interval
          AND c.cvss_score >= $2
        ORDER BY COALESCE(e.priority_score, 0) DESC, c.cvss_score DESC NULLS LAST
        LIMIT $3;
        """,
        str(days), min_score, limit,
    )
    return [dict(r) for r in rows]
