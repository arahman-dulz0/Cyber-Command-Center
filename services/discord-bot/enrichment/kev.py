"""
CISA KEV (Known Exploited Vulnerabilities) client.

Downloads the CISA KEV catalog (one JSON file), caches it in memory, and
refreshes on an interval. KEV membership is our authoritative "actively
exploited in the wild" signal.
"""

from __future__ import annotations

import asyncio
import time

import aiohttp

from config import config
from utils.logger import get_logger

log = get_logger("enrichment.kev")


class KEVClient:
    def __init__(self, url: str | None = None, refresh_hours: int | None = None) -> None:
        self.url = url or config.kev_url
        self.refresh_seconds = (refresh_hours or config.kev_refresh_hours) * 3600
        self._entries: dict[str, dict] = {}
        self._loaded_at: float | None = None
        self._lock = asyncio.Lock()

    async def ensure(self) -> None:
        """Download the catalog if not loaded or stale (thread-safe)."""
        fresh = (
            self._loaded_at is not None
            and (time.monotonic() - self._loaded_at) < self.refresh_seconds
        )
        if fresh:
            return
        async with self._lock:
            # Re-check after acquiring the lock.
            if (
                self._loaded_at is not None
                and (time.monotonic() - self._loaded_at) < self.refresh_seconds
            ):
                return
            try:
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(self.url) as resp:
                        resp.raise_for_status()
                        data = await resp.json(content_type=None)
                entries = {
                    v["cveID"].upper(): v
                    for v in data.get("vulnerabilities", [])
                    if v.get("cveID")
                }
                self._entries = entries
                self._loaded_at = time.monotonic()
                log.info("KEV catalog loaded: %d entries", len(entries))
            except Exception as exc:  # noqa: BLE001
                log.warning("KEV fetch failed: %s", exc)
                if self._loaded_at is None:
                    self._entries = {}  # keep empty; enrichment degrades gracefully

    def is_kev(self, cve_id: str) -> bool:
        return cve_id.upper() in self._entries

    def ransomware(self, cve_id: str) -> bool:
        entry = self._entries.get(cve_id.upper())
        return bool(entry) and entry.get("knownRansomwareCampaignUse", "Unknown") == "Known"
