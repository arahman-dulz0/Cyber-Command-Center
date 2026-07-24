"""Repository for the ``cves`` table."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from repositories.base import BaseRepository


class CVERepository(BaseRepository):
    """All persistence operations for CVE records."""

    async def get(self, cve_id: str) -> dict[str, Any] | None:
        row = await self.pool.fetchrow(
            "SELECT * FROM cves WHERE cve_id = $1;", cve_id.upper()
        )
        return dict(row) if row else None

    async def exists(self, cve_id: str) -> bool:
        val = await self.pool.fetchval(
            "SELECT 1 FROM cves WHERE cve_id = $1;", cve_id.upper()
        )
        return val is not None

    async def is_posted(self, cve_id: str) -> bool:
        """True only if this CVE was already posted to Discord (dedup key)."""
        val = await self.pool.fetchval(
            "SELECT posted_to_discord FROM cves WHERE cve_id = $1;", cve_id.upper()
        )
        return bool(val)

    async def upsert(
        self,
        *,
        cve_id: str,
        title: str | None,
        description: str | None,
        cvss_score: float | None,
        severity: str | None,
        published_date: datetime | None,
        ai_summary: str | None,
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO cves (cve_id, title, description, cvss_score,
                              severity, published_date, ai_summary)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (cve_id) DO UPDATE SET
                title          = EXCLUDED.title,
                description    = EXCLUDED.description,
                cvss_score     = EXCLUDED.cvss_score,
                severity       = EXCLUDED.severity,
                published_date = EXCLUDED.published_date,
                ai_summary     = COALESCE(EXCLUDED.ai_summary, cves.ai_summary);
            """,
            cve_id.upper(), title, description, cvss_score,
            severity, published_date, ai_summary,
        )

    async def mark_posted(self, cve_id: str) -> None:
        await self.pool.execute(
            "UPDATE cves SET posted_to_discord = TRUE WHERE cve_id = $1;",
            cve_id.upper(),
        )

    async def unposted(self, min_score: float, limit: int) -> list[dict[str, Any]]:
        """Stored CVEs at/above the threshold not yet posted (highest first)."""
        rows = await self.pool.fetch(
            """
            SELECT * FROM cves
            WHERE posted_to_discord = FALSE
              AND cvss_score >= $1
            ORDER BY cvss_score DESC, published_date DESC NULLS LAST
            LIMIT $2;
            """,
            min_score, limit,
        )
        return [dict(r) for r in rows]

    async def recent_critical(self, hours: int, min_score: float, limit: int = 5) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            """
            SELECT * FROM cves
            WHERE published_date >= NOW() - ($1::text || ' hours')::interval
              AND cvss_score >= $2
            ORDER BY cvss_score DESC, published_date DESC
            LIMIT $3;
            """,
            str(hours), min_score, limit,
        )
        return [dict(r) for r in rows]

    # --- Aggregations used by /brief and /stats --------------------------
    async def count_since(self, hours: int) -> int:
        return await self.pool.fetchval(
            "SELECT COUNT(*) FROM cves WHERE created_at >= NOW() - ($1::text || ' hours')::interval;",
            str(hours),
        )

    async def count_by_severity_since(self, severity: str, hours: int) -> int:
        return await self.pool.fetchval(
            """
            SELECT COUNT(*) FROM cves
            WHERE UPPER(severity) = $1
              AND created_at >= NOW() - ($2::text || ' hours')::interval;
            """,
            severity.upper(), str(hours),
        )

    async def highest_score_since(self, hours: int) -> dict[str, Any] | None:
        row = await self.pool.fetchrow(
            """
            SELECT * FROM cves
            WHERE created_at >= NOW() - ($1::text || ' hours')::interval
            ORDER BY cvss_score DESC NULLS LAST
            LIMIT 1;
            """,
            str(hours),
        )
        return dict(row) if row else None

    async def total(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM cves;")
