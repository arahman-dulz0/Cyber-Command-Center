"""Base repository — holds the shared asyncpg pool for all repositories."""

from __future__ import annotations

import asyncpg


class BaseRepository:
    """
    Base class for the repository pattern.

    Every repository receives the shared connection pool and exposes typed,
    intention-revealing query methods so cogs/tasks never write raw SQL.
    """

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    @property
    def pool(self) -> asyncpg.Pool:
        return self._pool
