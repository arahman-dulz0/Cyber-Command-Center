"""Repositories for Phase 4 — practice journal and HTB machine catalog."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from repositories.base import BaseRepository


class PracticeRepository(BaseRepository):
    """The user's study journal (``practice_log``)."""

    async def add(
        self,
        *,
        user_id: int | None,
        username: str | None,
        machine: str,
        platform: str,
        skills: list[str],
        difficulty: str | None,
        notes: str | None,
        source: str = "manual",
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO practice_log
                (user_id, username, machine, platform, skills, difficulty, notes, source)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8);
            """,
            user_id, username, machine, platform,
            [s.lower() for s in skills], difficulty, notes, source,
        )

    async def recent(self, limit: int = 10) -> list[dict[str, Any]]:
        rows = await self.pool.fetch(
            "SELECT * FROM practice_log ORDER BY practiced_at DESC LIMIT $1;", limit
        )
        return [dict(r) for r in rows]

    async def skill_counts(self, days: int = 90) -> list[tuple[str, int]]:
        """How often each skill was practiced in the window (most first)."""
        rows = await self.pool.fetch(
            """
            SELECT skill, COUNT(*) AS n
            FROM practice_log, unnest(skills) AS skill
            WHERE practiced_at >= NOW() - ($1::text || ' days')::interval
            GROUP BY skill
            ORDER BY n DESC;
            """,
            str(days),
        )
        return [(r["skill"], r["n"]) for r in rows]

    async def last_practiced_at(self) -> datetime | None:
        return await self.pool.fetchval("SELECT MAX(practiced_at) FROM practice_log;")

    async def total(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM practice_log;")


class MachineRepository(BaseRepository):
    """HTB machine catalog + own status (``htb_machines``)."""

    async def upsert(
        self,
        *,
        machine_id: int,
        name: str,
        os: str | None,
        difficulty: str | None,
        points: int | None,
        retired: bool,
        active: bool,
        release_date: datetime | None,
    ) -> None:
        await self.pool.execute(
            """
            INSERT INTO htb_machines
                (machine_id, name, os, difficulty, points, retired, active, release_date, updated_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8, NOW())
            ON CONFLICT (machine_id) DO UPDATE SET
                name=EXCLUDED.name, os=EXCLUDED.os, difficulty=EXCLUDED.difficulty,
                points=EXCLUDED.points, retired=EXCLUDED.retired, active=EXCLUDED.active,
                release_date=EXCLUDED.release_date, updated_at=NOW();
            """,
            machine_id, name, os, difficulty, points, retired, active, release_date,
        )

    async def set_owns(self, machine_id: int, *, user_owned: bool, root_owned: bool) -> None:
        await self.pool.execute(
            """
            UPDATE htb_machines
            SET user_owned = $2, root_owned = $3, updated_at = NOW()
            WHERE machine_id = $1;
            """,
            machine_id, user_owned, root_owned,
        )

    async def set_skill_areas(self, machine_id: int, skills: list[str]) -> None:
        await self.pool.execute(
            "UPDATE htb_machines SET skill_areas = $2 WHERE machine_id = $1;",
            machine_id, [s.lower() for s in skills],
        )

    async def needs_skill_areas(self, limit: int = 25) -> list[dict[str, Any]]:
        """Machines missing AI-derived skill areas (for lazy backfill)."""
        rows = await self.pool.fetch(
            """
            SELECT * FROM htb_machines
            WHERE cardinality(skill_areas) = 0
            ORDER BY active DESC, release_date DESC NULLS LAST
            LIMIT $1;
            """,
            limit,
        )
        return [dict(r) for r in rows]

    async def candidates(self, *, exclude_owned: bool = True, limit: int = 200) -> list[dict[str, Any]]:
        """Machines eligible to recommend (default: not yet root-owned)."""
        clause = "WHERE root_owned = FALSE" if exclude_owned else ""
        rows = await self.pool.fetch(
            f"""
            SELECT * FROM htb_machines
            {clause}
            ORDER BY active DESC, release_date DESC NULLS LAST
            LIMIT $1;
            """,
            limit,
        )
        return [dict(r) for r in rows]

    async def os_balance(self) -> dict[str, int]:
        """Count of owned machines per OS (informs recommendations)."""
        rows = await self.pool.fetch(
            """
            SELECT COALESCE(os,'Unknown') AS os, COUNT(*) AS n
            FROM htb_machines WHERE user_owned = TRUE OR root_owned = TRUE
            GROUP BY os;
            """
        )
        return {r["os"]: r["n"] for r in rows}

    async def total(self) -> int:
        return await self.pool.fetchval("SELECT COUNT(*) FROM htb_machines;")

    async def owned_count(self) -> int:
        return await self.pool.fetchval(
            "SELECT COUNT(*) FROM htb_machines WHERE user_owned OR root_owned;"
        )
