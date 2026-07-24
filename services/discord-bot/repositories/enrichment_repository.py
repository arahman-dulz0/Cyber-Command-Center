"""Repository for the ``cve_enrichment`` table (threat-intel fusion results)."""

from __future__ import annotations

from typing import Any

from repositories.base import BaseRepository


class EnrichmentRepository(BaseRepository):
    async def upsert(
        self,
        *,
        cve_id: str,
        epss: float | None,
        epss_percentile: float | None,
        kev: bool,
        kev_ransomware: bool,
        exploitdb_ids: list[str],
        github_poc_urls: list[str],
        patch_available: bool,
        priority_score: int,
        priority_label: str,
        ai_risk: str | None,
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO cve_enrichment (
                cve_id, epss, epss_percentile, kev, kev_ransomware,
                exploitdb_count, exploitdb_ids, github_poc_count, github_poc_urls,
                patch_available, priority_score, priority_label, ai_risk, enriched_at
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13, NOW())
            ON CONFLICT (cve_id) DO UPDATE SET
                epss=EXCLUDED.epss, epss_percentile=EXCLUDED.epss_percentile,
                kev=EXCLUDED.kev, kev_ransomware=EXCLUDED.kev_ransomware,
                exploitdb_count=EXCLUDED.exploitdb_count, exploitdb_ids=EXCLUDED.exploitdb_ids,
                github_poc_count=EXCLUDED.github_poc_count, github_poc_urls=EXCLUDED.github_poc_urls,
                patch_available=EXCLUDED.patch_available,
                priority_score=EXCLUDED.priority_score, priority_label=EXCLUDED.priority_label,
                ai_risk=COALESCE(EXCLUDED.ai_risk, cve_enrichment.ai_risk),
                enriched_at=NOW();
            """,
            cve_id.upper(), epss, epss_percentile, kev, kev_ransomware,
            len(exploitdb_ids), exploitdb_ids, len(github_poc_urls), github_poc_urls,
            patch_available, priority_score, priority_label, ai_risk,
        )

    async def get(self, cve_id: str) -> dict[str, Any] | None:
        row = await self.pool.fetchrow(
            "SELECT * FROM cve_enrichment WHERE cve_id = $1;", cve_id.upper()
        )
        return dict(row) if row else None

    async def count_kev_since(self, hours: int) -> int:
        return await self.pool.fetchval(
            """
            SELECT COUNT(*) FROM cve_enrichment
            WHERE kev = TRUE AND enriched_at >= NOW() - ($1::text || ' hours')::interval;
            """,
            str(hours),
        )

    async def count_exploited_since(self, hours: int) -> int:
        """CVEs enriched recently that have any public exploit or PoC."""
        return await self.pool.fetchval(
            """
            SELECT COUNT(*) FROM cve_enrichment
            WHERE (exploitdb_count > 0 OR github_poc_count > 0)
              AND enriched_at >= NOW() - ($1::text || ' hours')::interval;
            """,
            str(hours),
        )

    async def max_priority_since(self, hours: int) -> int:
        val = await self.pool.fetchval(
            """
            SELECT MAX(priority_score) FROM cve_enrichment
            WHERE enriched_at >= NOW() - ($1::text || ' hours')::interval;
            """,
            str(hours),
        )
        return val or 0
