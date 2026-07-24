"""
Monitor scheduler.

Runs every registered :class:`BaseMonitor` on its own ``discord.ext.tasks`` loop
(no cron, no external scheduler, no new containers). Monitors are registered from
a list, so future monitors (GitHub, YouTube, HTB, TryHackMe, ExploitDB, KEV,
vendor advisories) drop in with zero scheduler changes — just add the class to
``build_default_scheduler``.
"""

from __future__ import annotations

import asyncio

from discord.ext import commands, tasks

from config import config
from tasks.base import BaseMonitor, MonitorResult
from tasks.cve_monitor import CVEMonitor
from tasks.news_monitor import NewsMonitor
from utils.logger import scheduler_log as log


class Scheduler:
    """Owns and drives the background monitors."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.monitors: dict[str, BaseMonitor] = {}
        self._loops: list[tasks.Loop] = []

    def register(self, monitor: BaseMonitor) -> None:
        self.monitors[monitor.name] = monitor

    def get(self, name: str) -> BaseMonitor | None:
        return self.monitors.get(name)

    @property
    def names(self) -> list[str]:
        return list(self.monitors.keys())

    def start(self) -> None:
        """Start a loop per registered monitor (respects MONITORS_ENABLED)."""
        if not config.monitors_enabled:
            log.warning("Monitors are disabled (MONITORS_ENABLED=false); none started.")
            return
        for monitor in self.monitors.values():
            loop = self._build_loop(monitor)
            loop.start()
            self._loops.append(loop)
            log.info(
                "Scheduled monitor '%s' every %ds (initial delay %ds).",
                monitor.name, monitor.interval, monitor.initial_delay,
            )

    def stop(self) -> None:
        for loop in self._loops:
            loop.cancel()
        self._loops.clear()

    async def run_now(self, name: str) -> MonitorResult | None:
        """Run one monitor immediately (used by /monitor). Returns its result."""
        monitor = self.get(name)
        if monitor is None:
            return None
        return await monitor.run()

    def _build_loop(self, monitor: BaseMonitor) -> tasks.Loop:
        """Create a discord.py Loop bound to this monitor's interval."""

        @tasks.loop(seconds=monitor.interval)
        async def runner() -> None:
            # run() records its own monitor_runs row and never raises, but guard
            # anyway so a bug can never kill the loop.
            try:
                await monitor.run()
            except Exception as exc:  # noqa: BLE001
                log.error("Monitor '%s' crashed unexpectedly: %s", monitor.name, exc)

        @runner.before_loop
        async def before() -> None:
            await self.bot.wait_until_ready()
            if monitor.initial_delay:
                await asyncio.sleep(monitor.initial_delay)

        return runner


def build_default_scheduler(bot: commands.Bot) -> Scheduler:
    """Construct the scheduler with the built-in Phase 2 monitors registered."""
    scheduler = Scheduler(bot)
    scheduler.register(CVEMonitor(bot))
    scheduler.register(NewsMonitor(bot))
    return scheduler
