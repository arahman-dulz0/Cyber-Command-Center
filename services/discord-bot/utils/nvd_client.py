"""
Async client for the NVD (National Vulnerability Database) REST API v2.0.

Docs: https://nvd.nist.gov/developers/vulnerabilities

Handles the different CVSS metric versions (v3.1 → v3.0 → v2) and respects the
NVD rate limits (5 req/30s without a key, 50 req/30s with a key) by retrying on
HTTP 403/429 with a short backoff.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone

import aiohttp

from config import config
from utils.logger import get_logger

log = get_logger()

_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
_MAX_RETRIES = 3


class NVDError(Exception):
    """Generic NVD failure."""


class CVENotFound(NVDError):
    """Raised when the CVE id does not exist in NVD."""


@dataclass
class CVEData:
    cve_id: str
    description: str
    cvss_score: float | None
    cvss_vector: str | None
    severity: str | None
    published: datetime | None
    products: list[str] = field(default_factory=list)
    references: list[dict] = field(default_factory=list)  # [{"url":..., "tags":[...]}]

    @property
    def nvd_url(self) -> str:
        return f"https://nvd.nist.gov/vuln/detail/{self.cve_id}"

    @property
    def patch_available(self) -> bool:
        """Best-effort: NVD tags a reference 'Patch' when a fix is published."""
        return any("Patch" in (ref.get("tags") or []) for ref in self.references)


def _parse_metrics(metrics: dict) -> tuple[float | None, str | None, str | None]:
    """Return (score, vector, severity) preferring the newest CVSS version."""
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        entries = metrics.get(key)
        if not entries:
            continue
        primary = entries[0]
        data = primary.get("cvssData", {})
        score = data.get("baseScore")
        vector = data.get("vectorString")
        # v2 stores severity on the metric wrapper, v3 inside cvssData.
        severity = data.get("baseSeverity") or primary.get("baseSeverity")
        return score, vector, (severity.upper() if severity else None)
    return None, None, None


# CVSS v3 severity bands (label -> max score). A band is queried when its upper
# bound is at or above the requested minimum score.
_SEVERITY_BANDS: list[tuple[str, float]] = [
    ("CRITICAL", 10.0),
    ("HIGH", 8.9),
    ("MEDIUM", 6.9),
    ("LOW", 3.9),
]


def _severities_for(min_score: float) -> list[str]:
    """Severity labels whose score range overlaps [min_score, 10]."""
    return [label for label, band_max in _SEVERITY_BANDS if band_max >= min_score]


def _parse_published(cve: dict) -> datetime | None:
    raw = cve.get("published")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _build_cve(cve: dict) -> CVEData:
    """Build a CVEData from a single NVD 'cve' object (shared by all fetches)."""
    descriptions = cve.get("descriptions", [])
    description = next(
        (d["value"] for d in descriptions if d.get("lang") == "en"),
        "No description available.",
    )
    score, vector, severity = _parse_metrics(cve.get("metrics", {}))
    references = [
        {"url": r.get("url", ""), "tags": r.get("tags", [])}
        for r in cve.get("references", [])
    ]
    return CVEData(
        cve_id=cve.get("id", "UNKNOWN"),
        description=description,
        cvss_score=score,
        cvss_vector=vector,
        severity=severity,
        published=_parse_published(cve),
        products=_parse_products(cve.get("configurations", [])),
        references=references,
    )


def _parse_products(configurations: list) -> list[str]:
    products: list[str] = []
    for cfg in configurations or []:
        for node in cfg.get("nodes", []):
            for match in node.get("cpeMatch", []):
                criteria = match.get("criteria", "")
                # CPE 2.3: cpe:2.3:a:vendor:product:version:...
                parts = criteria.split(":")
                if len(parts) >= 5:
                    vendor, product = parts[3], parts[4]
                    label = f"{vendor} {product}".replace("_", " ").strip()
                    if label and label not in products:
                        products.append(label)
    return products[:5]


class NVDClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else config.nvd_api_key

    async def fetch_cve(self, cve_id: str) -> CVEData:
        cve_id = cve_id.strip().upper()
        headers = {"User-Agent": "CyberCommandCenter/1.0"}
        if self.api_key:
            headers["apiKey"] = self.api_key

        params = {"cveId": cve_id}
        last_err: Exception | None = None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(_BASE_URL, params=params, headers=headers) as resp:
                        if resp.status in (403, 429):
                            # Rate limited — back off and retry.
                            log.warning("NVD rate limit (HTTP %d), backing off", resp.status)
                            last_err = NVDError("NVD rate limit exceeded.")
                            await asyncio.sleep(6 * attempt)
                            continue
                        resp.raise_for_status()
                        data = await resp.json()
            except asyncio.TimeoutError:
                last_err = NVDError("NVD request timed out.")
                await asyncio.sleep(2 * attempt)
                continue
            except aiohttp.ClientError as exc:
                last_err = NVDError(f"NVD request failed: {exc}")
                await asyncio.sleep(2 * attempt)
                continue

            vulns = data.get("vulnerabilities", [])
            if not vulns:
                raise CVENotFound(f"{cve_id} not found in NVD database.")

            return _build_cve(vulns[0].get("cve", {}))

        assert last_err is not None
        raise last_err

    async def fetch_recent(
        self,
        start: datetime,
        end: datetime,
        *,
        min_score: float,
        max_results: int = 200,
    ) -> list[CVEData]:
        """
        Fetch CVEs *published* in [start, end] with CVSS >= ``min_score``.

        Uses NVD's server-side ``cvssV3Severity`` filter (one request per relevant
        severity band) so responses stay small and fast — a broad, unfiltered
        window returns thousands of results and times out. Results are
        client-filtered to the exact score, de-duplicated, sorted newest-first,
        and capped at ``max_results``. Dates are sent as UTC ISO-8601.
        """
        headers = {"User-Agent": "CyberCommandCenter/1.0"}
        if self.api_key:
            headers["apiKey"] = self.api_key

        def _fmt(dt: datetime) -> str:
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000")

        by_id: dict[str, CVEData] = {}
        per_page = 2000

        for severity in _severities_for(min_score):
            start_index = 0
            while True:
                params = {
                    "pubStartDate": _fmt(start),
                    "pubEndDate": _fmt(end),
                    "cvssV3Severity": severity,
                    "resultsPerPage": str(per_page),
                    "startIndex": str(start_index),
                    "noRejected": "",
                }
                data = await self._get_page(params, headers)
                vulns = data.get("vulnerabilities", [])
                for entry in vulns:
                    cve = _build_cve(entry.get("cve", {}))
                    if cve.cvss_score is not None and cve.cvss_score >= min_score:
                        by_id[cve.cve_id] = cve

                total = data.get("totalResults", 0)
                start_index += per_page
                if start_index >= total or not vulns:
                    break

        collected = list(by_id.values())
        collected.sort(key=lambda c: c.published or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return collected[:max_results]

    async def _get_page(self, params: dict, headers: dict) -> dict:
        """One NVD request with retry/backoff on timeouts and rate limits."""
        last_err: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=60)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(_BASE_URL, params=params, headers=headers) as resp:
                        if resp.status in (403, 429):
                            log.warning("NVD rate limit (HTTP %d), backing off", resp.status)
                            last_err = NVDError("NVD rate limit exceeded.")
                            await asyncio.sleep(6 * attempt)
                            continue
                        resp.raise_for_status()
                        return await resp.json()
            except asyncio.TimeoutError:
                last_err = NVDError("NVD request timed out.")
                await asyncio.sleep(2 * attempt)
            except aiohttp.ClientError as exc:
                last_err = NVDError(f"NVD request failed: {exc}")
                await asyncio.sleep(2 * attempt)
        assert last_err is not None
        raise last_err


# Shared instance.
nvd = NVDClient()
