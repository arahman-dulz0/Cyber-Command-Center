"""Repository for the ``command_logs`` table."""

from __future__ import annotations

from typing import Any

from repositories.base import BaseRepository


class CommandRepository(BaseRepository):
    """Records slash-command usage and answers usage-stat queries."""

    async def log(
        self,
        *,
        user_id: int,
        username: str,
        command: str,
        guild_id: int | None,
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO command_logs (user_id, username, command, guild_id)
            VALUES ($1, $2, $3, $4);
            """,
            user_id, username, command, guild_id,
        )

    async def count_since(self, hours: int) -> int:
        return await self.pool.fetchval(
            "SELECT COUNT(*) FROM command_logs WHERE created_at >= NOW() - ($1::text || ' hours')::interval;",
            str(hours),
        )

    async def total(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM command_logs;")

    async def top_command(self, hours: int | None = None) -> dict[str, Any] | None:
        """Return the most-used command (optionally within the last N hours)."""
        # command_logs stores the raw invocation (e.g. "/cve CVE-2021-44228");
        # collapse to the base command word for a meaningful ranking.
        if hours is None:
            row = await self.pool.fetchrow(
                """
                SELECT split_part(command, ' ', 1) AS cmd, COUNT(*) AS n
                FROM command_logs
                GROUP BY cmd
                ORDER BY n DESC
                LIMIT 1;
                """
            )
        else:
            row = await self.pool.fetchrow(
                """
                SELECT split_part(command, ' ', 1) AS cmd, COUNT(*) AS n
                FROM command_logs
                WHERE created_at >= NOW() - ($1::text || ' hours')::interval
                GROUP BY cmd
                ORDER BY n DESC
                LIMIT 1;
                """,
                str(hours),
            )
        return dict(row) if row else None
