"""Learning tool handlers — reuse the recommender + practice data."""

from __future__ import annotations

from typing import Any

from database import db
from learning.recommender import recommender

from analyst.tool_handlers.common import recent_enriched_cves

_FOCUS_KEYWORDS = (
    "active directory", "kerberos", "rce", "sql injection", "xss",
    "privilege escalation", "authentication", "deserialization", "ssrf", "lfi",
)


async def plan() -> dict[str, Any]:
    """Today's learning focus: recent-threat theme + the recommender embed."""
    # A 'hot theme' derived from what's driving recent critical CVEs.
    hot: dict[str, int] = {}
    for c in await recent_enriched_cves(days=7, min_score=8.0, limit=40):
        desc = (c.get("description") or "").lower()
        for kw in _FOCUS_KEYWORDS:
            if kw in desc:
                hot[kw] = hot.get(kw, 0) + 1
    focus = max(hot, key=hot.get) if hot else None

    # Reuse the existing recommender (handles HTB config + AI internally).
    embed = await recommender.build_recommendation_embed()
    skills = await db.practice.skill_counts(days=90)
    return {
        "focus": focus,
        "focus_hits": hot.get(focus, 0) if focus else 0,
        "skills": skills[:8],
        "embed": embed,
    }
