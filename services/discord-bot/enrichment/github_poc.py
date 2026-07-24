"""
GitHub PoC client (curated dataset).

Uses the public 'PoC-in-GitHub' index (nomi-sec), which stores one JSON file per
CVE listing known public proof-of-concept repositories. No auth, no rate limits.
Per-CVE results are cached in memory for the process lifetime.

Layout: {base}/{year}/{CVE-ID}.json  ->  [ { "html_url": ..., ... }, ... ]
A 404 simply means "no known PoCs".
"""

from __future__ import annotations

import re

import aiohttp

from config import config
from utils.logger import get_logger

log = get_logger("enrichment.github_poc")

_YEAR_RE = re.compile(r"CVE-(\d{4})-", re.IGNORECASE)


class GitHubPoCClient:
    def __init__(self, base: str | None = None) -> None:
        self.base = (base or config.github_poc_base).rstrip("/")
        self._cache: dict[str, list[str]] = {}

    async def pocs(self, cve_id: str) -> list[str]:
        """Return known PoC repo URLs for a CVE (empty list if none/unknown)."""
        cve_id = cve_id.upper()
        if cve_id in self._cache:
            return self._cache[cve_id]

        match = _YEAR_RE.match(cve_id)
        if not match:
            return []
        url = f"{self.base}/{match.group(1)}/{cve_id}.json"

        repos: list[str] = []
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status == 404:
                        self._cache[cve_id] = []
                        return []
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)
            repos = [r["html_url"] for r in data if r.get("html_url")]
        except Exception as exc:  # noqa: BLE001
            log.debug("GitHub PoC lookup failed for %s: %s", cve_id, exc)
            return []  # don't cache transient failures

        self._cache[cve_id] = repos
        return repos
