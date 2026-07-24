"""
EPSS client (FIRST.org).

EPSS (Exploit Prediction Scoring System) gives the probability a CVE will be
exploited in the next 30 days. Free, no auth. The API accepts a comma-separated
batch of CVE IDs.
"""

from __future__ import annotations

import aiohttp

from config import config
from utils.logger import get_logger

log = get_logger("enrichment.epss")


class EPSSClient:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or config.epss_url

    async def scores(self, cve_ids: list[str]) -> dict[str, tuple[float, float]]:
        """
        Return {cve_id: (epss, percentile)} for the given IDs (batched).

        Missing IDs simply won't appear in the result. Never raises — returns an
        empty dict on failure so enrichment degrades gracefully.
        """
        if not cve_ids:
            return {}
        out: dict[str, tuple[float, float]] = {}
        # Batch in chunks to keep the query string reasonable.
        for i in range(0, len(cve_ids), 100):
            chunk = cve_ids[i : i + 100]
            params = {"cve": ",".join(chunk)}
            try:
                timeout = aiohttp.ClientTimeout(total=20)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(self.url, params=params) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
            except Exception as exc:  # noqa: BLE001
                log.warning("EPSS fetch failed: %s", exc)
                continue
            for row in data.get("data", []):
                cid = (row.get("cve") or "").upper()
                try:
                    out[cid] = (float(row.get("epss", 0)), float(row.get("percentile", 0)))
                except (TypeError, ValueError):
                    continue
        return out
