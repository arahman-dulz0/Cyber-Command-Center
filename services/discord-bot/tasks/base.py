"""
Base class for background monitors.

Every monitor implements the same four-step contract:

    fetch()   -> pull raw items from an external source
    process() -> deduplicate, summarise, and persist; return items to post
    post()    -> render and send to Discord; return how many were posted
    run()     -> orchestrate the above, record a monitor_runs row, never raise

The template ``run()`` lives here (DRY), so adding a new monitor (GitHub,
YouTube, HTB, ExploitDB, KEV, vendor advisories, …) means subclassing this and
implementing fetch/process/post — the scheduler needs no changes.
"""

from __future__ import annotations

import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from database import db
from utils.logger import scheduler_log as log

if TYPE_CHECKING:  # avoid a runtime import cycle with bot.py
    import discord
    from discord.ext import commands


@dataclass
class MonitorResult:
    """Outcome of a single monitor run (returned to /monitor)."""

    task: str
    status: str            # "success" | "error"
    items_found: int
    items_posted: int
    errors: str | None
    elapsed_seconds: float


class BaseMonitor(ABC):
    """Abstract base for all background monitors."""

    #: Unique task name (used as the monitor_runs.task key and /monitor choice).
    name: str = "base"
    #: Discord channel name to post into.
    channel_name: str = ""
    #: How often the scheduler runs this monitor, in seconds.
    interval: int = 3600
    #: Delay (seconds) before the first run after startup, to stagger monitors.
    initial_delay: int = 10

    def __init__(self, bot: "commands.Bot") -> None:
        self.bot = bot

    # --- Steps implemented by subclasses ---------------------------------
    @abstractmethod
    async def fetch(self) -> list[Any]:
        """Pull raw items from the external source."""

    @abstractmethod
    async def process(self, raw: list[Any]) -> list[Any]:
        """Deduplicate, summarise, persist; return the items that should post."""

    @abstractmethod
    async def post(self, items: list[Any]) -> int:
        """Send items to Discord; return the number actually posted."""

    # --- Orchestration (shared) ------------------------------------------
    async def run(self) -> MonitorResult:
        """Execute fetch → process → post, recording a monitor_runs row."""
        import time

        started = time.monotonic()
        run_id = await db.monitors.start_run(self.name)
        found = posted = 0
        status = "success"
        errors: str | None = None

        try:
            raw = await self.fetch()
            found = len(raw)
            to_post = await self.process(raw)
            posted = await self.post(to_post)
            log.info("[%s] run complete: found=%d posted=%d", self.name, found, posted)
        except Exception as exc:  # noqa: BLE001 - a monitor must never crash the loop
            status = "error"
            errors = f"{type(exc).__name__}: {exc}"
            log.error("[%s] run failed: %s\n%s", self.name, exc, traceback.format_exc())

        await db.monitors.finish_run(
            run_id, status=status, items_found=found, items_posted=posted, errors=errors
        )
        return MonitorResult(
            task=self.name,
            status=status,
            items_found=found,
            items_posted=posted,
            errors=errors,
            elapsed_seconds=time.monotonic() - started,
        )

    # --- Helpers ---------------------------------------------------------
    def channel(self) -> "discord.TextChannel | None":
        """Resolve the target channel by name across the bot's guilds."""
        return self.bot.find_channel(self.channel_name)
