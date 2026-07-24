"""
HTB catalog import monitor (Phase 4).

A data-sync monitor (it posts nothing to Discord): periodically pulls the HTB
machine catalogue + own-status into ``htb_machines`` and lazily backfills
AI-derived skill areas for a bounded number of machines per run. Reuses the
BaseMonitor framework so it's tracked in ``monitor_runs`` and runnable via
/monitor.
"""

from __future__ import annotations

from discord.ext import commands

from config import config
from database import db
from learning.htb_client import htb
from learning.recommender import recommender
from tasks.base import BaseMonitor
from utils.logger import get_logger

log = get_logger("learning.htb")

_SKILL_BACKFILL_PER_RUN = 8  # bound AI work per cycle on a slow host


class HTBMonitor(BaseMonitor):
    name = "htb"
    channel_name = ""  # data sync only; nothing posted
    interval = config.htb_refresh_hours * 3600
    initial_delay = 120

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)

    async def fetch(self) -> list[dict]:
        if not htb.enabled:
            log.info("[htb] no HTB_APP_TOKEN set — skipping catalog import")
            return []
        return await htb.fetch_catalog()

    async def process(self, raw: list[dict]) -> list[dict]:
        # Upsert catalog + own status.
        for m in raw:
            await db.machines.upsert(
                machine_id=m["machine_id"], name=m["name"], os=m.get("os"),
                difficulty=m.get("difficulty"), points=m.get("points"),
                retired=m.get("retired", False), active=m.get("active", False),
                release_date=None,
            )
            await db.machines.set_owns(
                m["machine_id"],
                user_owned=m.get("user_owned", False),
                root_owned=m.get("root_owned", False),
            )

        # Lazily AI-tag a few machines that still lack skill areas.
        pending = await db.machines.needs_skill_areas(limit=_SKILL_BACKFILL_PER_RUN)
        for row in pending:
            tags = await recommender.infer_skill_areas(row["name"], row.get("os"), row.get("difficulty"))
            if tags:
                await db.machines.set_skill_areas(row["machine_id"], tags)
        return raw

    async def post(self, items: list[dict]) -> int:
        # Data-sync task: nothing is posted to Discord.
        return 0
