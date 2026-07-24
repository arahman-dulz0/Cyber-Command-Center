"""Repository for the ``news_articles`` table."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from repositories.base import BaseRepository


class NewsRepository(BaseRepository):
    """All persistence operations for news articles."""

    async def exists(self, url: str) -> bool:
        val = await self.pool.fetchval(
            "SELECT 1 FROM news_articles WHERE url = $1;", url
        )
        return val is not None

    async def is_posted(self, url: str) -> bool:
        """True only if this article was already posted to Discord (dedup key)."""
        val = await self.pool.fetchval(
            "SELECT posted_to_discord FROM news_articles WHERE url = $1;", url
        )
        return bool(val)

    async def upsert(
        self,
        *,
        title: str,
        url: str,
        source: str | None,
        description: str | None,
        ai_summary: str | None,
        published_date: datetime | None,
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO news_articles (title, url, source, description,
                                       ai_summary, published_date)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (url) DO UPDATE SET
                ai_summary = COALESCE(EXCLUDED.ai_summary, news_articles.ai_summary);
            """,
            title, url, source, description, ai_summary, published_date,
        )

    async def mark_posted(self, url: str) -> None:
        await self.pool.execute(
            "UPDATE news_articles SET posted_to_discord = TRUE WHERE url = $1;",
            url,
        )

    async def recent(self, limit: int = 3) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            """
            SELECT * FROM news_articles
            ORDER BY COALESCE(published_date, created_at) DESC
            LIMIT $1;
            """,
            limit,
        )
        return [dict(r) for r in rows]

    async def count_since(self, hours: int) -> int:
        return await self.pool.fetchval(
            "SELECT COUNT(*) FROM news_articles WHERE created_at >= NOW() - ($1::text || ' hours')::interval;",
            str(hours),
        )

    async def total(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM news_articles;")
