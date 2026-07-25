"""Repository for the ``analyst_log`` table (AI Analyst interaction log)."""

from __future__ import annotations

from typing import Any

from repositories.base import BaseRepository


class AnalystRepository(BaseRepository):
    async def log(
        self,
        *,
        user_id: int | None,
        username: str | None,
        query: str,
        intent: str | None,
        tools: list[str],
        sources: list[str],
        used_llm: bool,
        elapsed_ms: int,
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO analyst_log
                (user_id, username, query, intent, tools, sources, used_llm, elapsed_ms)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8);
            """,
            user_id, username, query[:2000], intent, tools, sources, used_llm, elapsed_ms,
        )

    async def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            "SELECT * FROM analyst_log ORDER BY created_at DESC LIMIT $1;", limit
        )
        return [dict(r) for r in rows]

    async def count_since(self, hours: int) -> int:
        return await self.pool.fetchval(
            "SELECT COUNT(*) FROM analyst_log WHERE created_at >= NOW() - ($1::text || ' hours')::interval;",
            str(hours),
        )
