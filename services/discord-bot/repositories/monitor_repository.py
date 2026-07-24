"""Repository for the ``monitor_runs`` table (background-task run history/state)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from repositories.base import BaseRepository


class MonitorRepository(BaseRepository):
    """
    Stores one row per monitor execution and exposes the "last successful run"
    state that monitors use to look back only over new data.
    """

    async def start_run(self, task: str) -> int:
        """Insert a run row in the 'running' state; return its id."""
        return await self.pool.fetchval(
            """
            INSERT INTO monitor_runs (task, started, status)
            VALUES ($1, NOW(), 'running')
            RETURNING id;
            """,
            task,
        )

    async def finish_run(
        self,
        run_id: int,
        *,
        status: str,
        items_found: int,
        items_posted: int,
        errors: str | None,
    ) -> None:
        # last_success is stamped only on a successful run.
        await self.pool.execute(
            """
            UPDATE monitor_runs SET
                finished     = NOW(),
                status       = $2,
                items_found  = $3,
                items_posted = $4,
                errors       = $5,
                last_success = CASE WHEN $2 = 'success' THEN NOW() ELSE last_success END
            WHERE id = $1;
            """,
            run_id, status, items_found, items_posted, errors,
        )

    async def last_success(self, task: str) -> datetime | None:
        """Timestamp the given task last completed successfully, or None."""
        return await self.pool.fetchval(
            """
            SELECT MAX(last_success) FROM monitor_runs
            WHERE task = $1 AND status = 'success';
            """,
            task,
        )

    async def last_run(self, task: str) -> dict[str, Any] | None:
        row = await self.pool.fetchrow(
            """
            SELECT * FROM monitor_runs
            WHERE task = $1
            ORDER BY started DESC
            LIMIT 1;
            """,
            task,
        )
        return dict(row) if row else None
