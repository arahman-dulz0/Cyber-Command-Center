"""
Repository for AI summary caching (``ai_summaries``) and AI metrics
(``ai_metrics``).

The summary cache guarantees we never summarise the same content twice; the
metrics table powers the AI figures shown by /stats.
"""

from __future__ import annotations

import hashlib

from repositories.base import BaseRepository


def content_hash(model: str, text: str) -> str:
    """Stable cache key for a (model, prompt) pair."""
    return hashlib.sha256(f"{model}\x00{text}".encode("utf-8")).hexdigest()


class AIRepository(BaseRepository):
    # --- Summary cache ---------------------------------------------------
    async def get_cached_summary(self, key: str) -> str | None:
        return await self.pool.fetchval(
            "SELECT summary FROM ai_summaries WHERE content_hash = $1;", key
        )

    async def save_summary(self, key: str, model: str, summary: str) -> None:
        await self.pool.execute(
            """
            INSERT INTO ai_summaries (content_hash, model, summary)
            VALUES ($1, $2, $3)
            ON CONFLICT (content_hash) DO UPDATE SET summary = EXCLUDED.summary;
            """,
            key, model, summary,
        )

    # --- Metrics ---------------------------------------------------------
    async def record_metric(
        self, *, kind: str, model: str, elapsed_ms: int, cache_hit: bool
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO ai_metrics (kind, model, elapsed_ms, cache_hit)
            VALUES ($1, $2, $3, $4);
            """,
            kind, model, elapsed_ms, cache_hit,
        )

    async def summaries_generated_since(self, hours: int) -> int:
        """Count of real (non-cached) AI generations in the window."""
        return await self.pool.fetchval(
            """
            SELECT COUNT(*) FROM ai_metrics
            WHERE cache_hit = FALSE
              AND created_at >= NOW() - ($1::text || ' hours')::interval;
            """,
            str(hours),
        )

    async def avg_response_ms_since(self, hours: int) -> float | None:
        """Average latency of real generations (cache hits excluded)."""
        return await self.pool.fetchval(
            """
            SELECT AVG(elapsed_ms) FROM ai_metrics
            WHERE cache_hit = FALSE
              AND created_at >= NOW() - ($1::text || ' hours')::interval;
            """,
            str(hours),
        )
