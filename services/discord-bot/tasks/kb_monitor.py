"""
Knowledge-base folder-ingest monitor (Phase 5).

Scans the mounted knowledge directory for supported files and ingests any new
ones (dedup is by content hash inside the ingest pipeline). Bounded per run so a
large drop doesn't monopolise the embedder. Posts nothing to Discord.
"""

from __future__ import annotations

import os

from discord.ext import commands

from config import config
from knowledge.ingest import ingest_file_bytes, is_supported
from tasks.base import BaseMonitor
from utils.logger import get_logger

log = get_logger("knowledge.folder")

_MAX_FILES_PER_RUN = 10


class KBMonitor(BaseMonitor):
    name = "kb"
    channel_name = ""  # data ingest only
    interval = 3600
    initial_delay = 240

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)

    async def fetch(self) -> list[str]:
        d = config.knowledge_dir
        if not os.path.isdir(d):
            return []
        paths = []
        for entry in sorted(os.listdir(d)):
            full = os.path.join(d, entry)
            if os.path.isfile(full) and is_supported(entry):
                paths.append(full)
        return paths

    async def process(self, raw: list[str]) -> list[str]:
        ingested = 0
        for path in raw:
            if ingested >= _MAX_FILES_PER_RUN:
                log.info("[kb] hit per-run cap (%d); remaining files next cycle", _MAX_FILES_PER_RUN)
                break
            try:
                with open(path, "rb") as f:
                    data = f.read()
            except OSError as exc:
                log.warning("[kb] cannot read %s: %s", path, exc)
                continue
            result = await ingest_file_bytes(os.path.basename(path), data, added_by="folder")
            if result.ok:
                ingested += 1
                log.info("[kb] ingested %s (%d chunks)", os.path.basename(path), result.chunks)
        return [str(ingested)]

    async def post(self, items: list[str]) -> int:
        return 0
