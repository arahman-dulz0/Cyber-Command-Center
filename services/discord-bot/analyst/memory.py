"""
Conversational memory for the AI Analyst.

Keeps a short per-user history plus the last entities discussed (CVE id, product,
topic) so follow-ups like "does it affect my lab?" resolve without the user
repeating context. In-memory, per-process, TTL-expiring.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class Turn:
    query: str
    intent: str


@dataclass
class UserMemory:
    turns: deque[Turn] = field(default_factory=lambda: deque(maxlen=8))
    last_cve: str | None = None
    last_product: str | None = None
    last_topic: str | None = None
    updated: float = 0.0


class Memory:
    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._store: dict[int, UserMemory] = {}
        self._ttl = ttl_seconds

    def get(self, user_id: int) -> UserMemory:
        m = self._store.get(user_id)
        now = time.monotonic()
        if m is not None and (now - m.updated) > self._ttl:
            m = None  # expired
        if m is None:
            m = UserMemory(updated=now)
            self._store[user_id] = m
        return m

    def remember(
        self,
        user_id: int,
        *,
        cve: str | None = None,
        product: str | None = None,
        topic: str | None = None,
    ) -> None:
        m = self.get(user_id)
        if cve:
            m.last_cve = cve
        if product:
            m.last_product = product
        if topic:
            m.last_topic = topic
        m.updated = time.monotonic()

    def add_turn(self, user_id: int, query: str, intent: str) -> None:
        m = self.get(user_id)
        m.turns.append(Turn(query=query, intent=intent))
        m.updated = time.monotonic()

    def recent(self, user_id: int, n: int = 3) -> list[Turn]:
        return list(self.get(user_id).turns)[-n:]


# Shared instance.
memory = Memory()
