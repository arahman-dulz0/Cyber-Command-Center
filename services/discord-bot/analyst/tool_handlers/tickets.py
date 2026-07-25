"""Ticket tool handlers — reuse the ticket repository."""

from __future__ import annotations

from typing import Any

from database import db


async def open_tickets(limit: int = 15) -> list[dict[str, Any]]:
    return await db.tickets.open_tickets(limit=limit)


async def count() -> int:
    return await db.tickets.open_count()
