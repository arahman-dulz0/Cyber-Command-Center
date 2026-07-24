"""
HackTheBox v4 API client.

Fetches the machine catalogue (active + retired) with the authenticated user's
own-status. Auth is a Bearer App Token (JWT) from HTB profile settings.

The HTB API is undocumented/semi-private, so parsing is defensive: field names
vary between endpoints and releases, and every method degrades to empty rather
than raising. Own-status is read from the per-machine flags the list returns for
an authenticated user (no separate owns endpoint needed).
"""

from __future__ import annotations

import aiohttp

from config import config
from utils.logger import get_logger

log = get_logger("learning.htb")


def _first(d: dict, *keys, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


class HTBClient:
    def __init__(self, token: str | None = None, base: str | None = None) -> None:
        self.token = token if token is not None else config.htb_app_token
        self.base = (base or config.htb_api_base).rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self.token)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            # HTB rejects non-browser user agents.
            "User-Agent": "Mozilla/5.0 (CyberCommandCenter)",
        }

    async def _get(self, session: aiohttp.ClientSession, path: str, params: dict | None = None) -> dict | None:
        url = f"{self.base}/{path.lstrip('/')}"
        try:
            async with session.get(url, params=params, headers=self._headers()) as resp:
                if resp.status == 401:
                    log.warning("HTB API unauthorized (check HTB_APP_TOKEN)")
                    return None
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except Exception as exc:  # noqa: BLE001
            log.warning("HTB API GET %s failed: %s", path, exc)
            return None

    @staticmethod
    def _normalize(m: dict, *, retired: bool) -> dict | None:
        mid = _first(m, "id")
        name = _first(m, "name")
        if mid is None or not name:
            return None
        return {
            "machine_id": int(mid),
            "name": str(name),
            "os": _first(m, "os"),
            "difficulty": _first(m, "difficultyText", "difficulty"),
            "points": _first(m, "static_points", "points", default=0),
            "retired": bool(retired or _first(m, "retired", default=False)),
            "active": bool(_first(m, "active", default=not retired)),
            "user_owned": bool(_first(m, "authUserInUserOwns", "isUserOwn", "owned", default=False)),
            "root_owned": bool(_first(m, "authUserInRootOwns", "isRootOwn", default=False)),
        }

    async def fetch_catalog(self, *, max_retired_pages: int = 8) -> list[dict]:
        """
        Return normalized machine dicts (active + retired) with own-status.
        Empty list on any failure — the caller decides how to degrade.
        """
        if not self.enabled:
            return []
        out: list[dict] = []
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Active machines.
            data = await self._get(session, "machine/list")
            for m in (data or {}).get("info", []) if data else []:
                norm = self._normalize(m, retired=False)
                if norm:
                    out.append(norm)

            # Retired machines (Laravel pagination).
            page = 1
            while page <= max_retired_pages:
                data = await self._get(
                    session, "machine/list/retired/paginated",
                    params={"per_page": "100", "page": str(page)},
                )
                if not data:
                    break
                rows = data.get("data") or data.get("info") or []
                if not rows:
                    break
                for m in rows:
                    norm = self._normalize(m, retired=True)
                    if norm:
                        out.append(norm)
                # Stop if there's no next page.
                meta = data.get("meta") or {}
                last_page = meta.get("last_page")
                if last_page is not None and page >= last_page:
                    break
                page += 1

        # De-duplicate by id (active list may overlap).
        by_id = {m["machine_id"]: m for m in out}
        log.info("HTB catalog fetched: %d machines", len(by_id))
        return list(by_id.values())


# Shared instance.
htb = HTBClient()
