"""
Read-only data access for the dashboard.

A small asyncpg pool over the SAME PostgreSQL the bot fills. All queries are
read-only; the dashboard never writes. Reached by service name over
docker_cyber-net (POSTGRES_HOST=postgres), same as the bot.
"""

from __future__ import annotations

import os
from typing import Any

import asyncpg


def _dsn() -> str:
    user = os.getenv("POSTGRES_USER", "cyber")
    password = os.getenv("POSTGRES_PASSWORD", "")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "cyberdb")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# HTB-owned target used for the learning progress ring (honest, modest goal).
_HTB_GOAL = int(os.getenv("HTB_PROGRESS_GOAL", "50"))


class Dashboard:
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(dsn=_dsn(), min_size=1, max_size=5, command_timeout=15)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    @property
    def pool(self) -> asyncpg.Pool:
        assert self._pool is not None, "pool not connected"
        return self._pool

    async def _val(self, sql: str, *args) -> Any:
        try:
            return await self.pool.fetchval(sql, *args)
        except Exception:
            return None

    # --- Summary tiles ---------------------------------------------------
    async def summary(self) -> dict[str, Any]:
        cves_24h = await self._val(
            "SELECT COUNT(*) FROM cves WHERE created_at >= NOW() - INTERVAL '24 hours'"
        ) or 0
        news_24h = await self._val(
            "SELECT COUNT(*) FROM news_articles WHERE created_at >= NOW() - INTERVAL '24 hours'"
        ) or 0
        kev_24h = await self._val(
            "SELECT COUNT(*) FROM cve_enrichment WHERE kev AND enriched_at >= NOW() - INTERVAL '24 hours'"
        ) or 0
        exploited_24h = await self._val(
            """SELECT COUNT(*) FROM cve_enrichment
               WHERE (exploitdb_count > 0 OR github_poc_count > 0)
                 AND enriched_at >= NOW() - INTERVAL '24 hours'"""
        ) or 0
        top_priority = await self._val(
            "SELECT COALESCE(MAX(priority_score),0) FROM cve_enrichment WHERE enriched_at >= NOW() - INTERVAL '24 hours'"
        ) or 0

        sessions = await self._val("SELECT COUNT(*) FROM practice_log") or 0
        distinct_skills = await self._val(
            "SELECT COUNT(DISTINCT s) FROM practice_log, unnest(skills) s"
        ) or 0
        htb_owned = await self._val(
            "SELECT COUNT(*) FROM htb_machines WHERE user_owned OR root_owned"
        ) or 0
        docs = await self._val("SELECT COUNT(*) FROM kb_documents") or 0
        chunks = await self._val("SELECT COUNT(*) FROM kb_chunks") or 0
        commands_24h = await self._val(
            "SELECT COUNT(*) FROM command_logs WHERE created_at >= NOW() - INTERVAL '24 hours'"
        ) or 0

        level, color = self._threat_level(kev_24h, top_priority, exploited_24h, cves_24h)
        progress = min(100, round(htb_owned / _HTB_GOAL * 100)) if _HTB_GOAL else 0

        return {
            "threat_level": level, "threat_color": color,
            "cves_24h": cves_24h, "news_24h": news_24h, "kev_24h": kev_24h,
            "exploited_24h": exploited_24h, "top_priority": top_priority,
            "commands_24h": commands_24h,
            "practice_sessions": sessions, "distinct_skills": distinct_skills,
            "htb_owned": htb_owned, "htb_goal": _HTB_GOAL, "learning_progress": progress,
            "kb_docs": docs, "kb_chunks": chunks,
        }

    @staticmethod
    def _threat_level(kev: int, top: int, exploited: int, cves: int) -> tuple[str, str]:
        if kev > 0 or top >= 90:
            return "HIGH", "#FF3B30"
        if top >= 70 or exploited > 0:
            return "ELEVATED", "#FF9500"
        if cves > 0:
            return "GUARDED", "#FFCC00"
        return "LOW", "#34C759"

    # --- Charts ----------------------------------------------------------
    async def cve_timeline(self, days: int = 7) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            """
            SELECT to_char(d::date, 'Mon DD') AS day,
                   COALESCE(c.n, 0) AS count
            FROM generate_series(NOW() - ($1::text || ' days')::interval, NOW(), INTERVAL '1 day') d
            LEFT JOIN (
                SELECT date_trunc('day', created_at) AS day, COUNT(*) n
                FROM cves GROUP BY 1
            ) c ON c.day = date_trunc('day', d)
            ORDER BY d;
            """,
            str(days),
        )
        return [{"day": r["day"], "count": r["count"]} for r in rows]

    async def priority_distribution(self) -> dict[str, int]:
        rows = await self.pool.fetch(
            "SELECT priority_label, COUNT(*) n FROM cve_enrichment GROUP BY priority_label"
        )
        out = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for r in rows:
            if r["priority_label"] in out:
                out[r["priority_label"]] = r["n"]
        return out

    # --- Lists -----------------------------------------------------------
    async def latest_alerts(self, limit: int = 8) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            """
            SELECT c.cve_id, c.cvss_score, c.severity,
                   e.priority_score, e.priority_label, e.kev, e.epss,
                   e.github_poc_count, e.exploitdb_count
            FROM cve_enrichment e JOIN cves c ON c.cve_id = e.cve_id
            ORDER BY e.enriched_at DESC
            LIMIT $1;
            """,
            limit,
        )
        return [dict(r) for r in rows]

    async def latest_news(self, limit: int = 8) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            """
            SELECT title, url, source, COALESCE(published_date, created_at) AS ts
            FROM news_articles ORDER BY COALESCE(published_date, created_at) DESC LIMIT $1;
            """,
            limit,
        )
        return [dict(r) for r in rows]

    async def top_skills(self, limit: int = 8) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            """
            SELECT s AS skill, COUNT(*) n FROM practice_log, unnest(skills) s
            GROUP BY s ORDER BY n DESC LIMIT $1;
            """,
            limit,
        )
        return [{"skill": r["skill"], "count": r["n"]} for r in rows]


dashboard = Dashboard()
