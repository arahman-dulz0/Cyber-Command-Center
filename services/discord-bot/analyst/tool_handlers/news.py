"""News tool handlers — reuse the stored news feed."""

from __future__ import annotations

from typing import Any

from database import db

_RANSOM = ("ransom", "lockbit", "blackcat", "alphv", "cl0p", "clop", "extort", "encrypt")


async def recent(limit: int = 6) -> list[dict[str, Any]]:
    return await db.news.recent(limit=limit)


async def ransomware(limit: int = 6) -> list[dict[str, Any]]:
    rows = await db.news.recent(limit=40)
    hits = [r for r in rows if any(k in (r.get("title") or "").lower() for k in _RANSOM)]
    return hits[:limit]
