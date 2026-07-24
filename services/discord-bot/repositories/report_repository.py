"""Repository for agent-crew intelligence reports (``reports``)."""

from __future__ import annotations

from typing import Any

from repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    async def add(self, *, title: str, summary: str, content: str) -> int:
        return await self.pool.fetchval(
            "INSERT INTO reports (title, summary, content) VALUES ($1,$2,$3) RETURNING id;",
            title, summary, content,
        )

    async def recent(self, limit: int = 5) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            "SELECT id, title, summary, created_at FROM reports ORDER BY created_at DESC LIMIT $1;",
            limit,
        )
        return [dict(r) for r in rows]

    async def total(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM reports;")
