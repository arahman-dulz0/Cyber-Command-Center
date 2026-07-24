"""Repositories for Phase 8 — lab inventory and auto-raised tickets."""

from __future__ import annotations

from typing import Any

from repositories.base import BaseRepository


class LabRepository(BaseRepository):
    """The user's lab/stack inventory (matched against CVEs)."""

    async def add(self, *, name: str, note: str | None, added_by: str | None) -> bool:
        """Add an asset keyword. Returns False if it already existed."""
        val = await self.pool.fetchval(
            """
            INSERT INTO lab_assets (name, note, added_by) VALUES ($1,$2,$3)
            ON CONFLICT (name) DO NOTHING RETURNING id;
            """,
            name.strip().lower(), note, added_by,
        )
        return val is not None

    async def remove(self, name: str) -> bool:
        val = await self.pool.fetchval(
            "DELETE FROM lab_assets WHERE name = $1 RETURNING id;", name.strip().lower()
        )
        return val is not None

    async def all(self) -> list[dict[str, Any]]:
        rows = await self.pool.fetch("SELECT * FROM lab_assets ORDER BY name;")
        return [dict(r) for r in rows]

    async def names(self) -> list[str]:
        rows = await self.pool.fetch("SELECT name FROM lab_assets;")
        return [r["name"] for r in rows]

    async def total(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM lab_assets;")


class TicketRepository(BaseRepository):
    """Auto-raised remediation tickets."""

    async def create(
        self, *, cve_id: str, assets: list[str], priority: int, checklist: str | None
    ) -> int | None:
        """Create an open ticket; returns id, or None if one is already open for this CVE."""
        return await self.pool.fetchval(
            """
            INSERT INTO tickets (cve_id, assets, priority, checklist)
            VALUES ($1,$2,$3,$4)
            ON CONFLICT (cve_id) WHERE status = 'open' DO NOTHING
            RETURNING id;
            """,
            cve_id.upper(), assets, priority, checklist,
        )

    async def open_tickets(self, limit: int = 25) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            "SELECT * FROM tickets WHERE status='open' ORDER BY priority DESC, created_at DESC LIMIT $1;",
            limit,
        )
        return [dict(r) for r in rows]

    async def close(self, ticket_id: int) -> bool:
        val = await self.pool.fetchval(
            "UPDATE tickets SET status='closed', closed_at=NOW() WHERE id=$1 AND status='open' RETURNING id;",
            ticket_id,
        )
        return val is not None

    async def open_count(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM tickets WHERE status='open';")
