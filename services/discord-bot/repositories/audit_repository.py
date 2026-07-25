"""Repository for the security ``audit_log`` table."""

from __future__ import annotations

from typing import Any

from repositories.base import BaseRepository


class AuditRepository(BaseRepository):
    async def record(
        self,
        *,
        actor: str | None,
        action: str,
        target: str | None = None,
        detail: str | None = None,
        source: str = "discord",
        ip: str | None = None,
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO audit_log (actor, action, target, detail, source, ip)
            VALUES ($1,$2,$3,$4,$5,$6);
            """,
            actor, action, target, detail, source, ip,
        )

    async def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT $1;", limit
        )
        return [dict(r) for r in rows]
