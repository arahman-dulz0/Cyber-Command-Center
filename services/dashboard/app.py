"""
Cyber Command Center — web dashboard (Phase 6).

A lightweight FastAPI app that renders a dark, SOC-style dashboard and serves
JSON endpoints the frontend polls. Read-only over the shared PostgreSQL.
"""

from __future__ import annotations

import datetime as _dt
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from db import dashboard
from security import (
    AUTH_ENABLED,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    require_auth,
    require_ui_auth,
)

_TEMPLATE = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging

    logging.getLogger("uvicorn.error").info(
        "Dashboard auth %s", "ENABLED" if AUTH_ENABLED else "DISABLED (open / LAN mode)"
    )
    await dashboard.connect()
    yield
    await dashboard.close()


app = FastAPI(title="Cyber Command Center", lifespan=lifespan)
# Order matters: rate-limit first, then attach security headers to every response.
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# Every /api endpoint requires Basic Auth or a valid X-API-Key.
API_DEPS = [Depends(require_auth)]


def _clean(obj):
    """Make DB rows JSON-serialisable (datetimes → ISO)."""
    if isinstance(obj, list):
        return [_clean(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, _dt.datetime):
        return obj.isoformat()
    return obj


@app.get("/", response_class=HTMLResponse, dependencies=[Depends(require_ui_auth)])
async def index() -> str:
    return _TEMPLATE


@app.get("/healthz")
async def healthz() -> dict:
    # Intentionally unauthenticated + rate-limit exempt (container healthcheck).
    return {"ok": True}


@app.get("/api/summary", dependencies=API_DEPS)
async def api_summary() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.summary()))


@app.get("/api/cve-timeline", dependencies=API_DEPS)
async def api_cve_timeline() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.cve_timeline()))


@app.get("/api/priority-distribution", dependencies=API_DEPS)
async def api_priority_distribution() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.priority_distribution()))


@app.get("/api/latest-alerts", dependencies=API_DEPS)
async def api_latest_alerts() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.latest_alerts()))


@app.get("/api/latest-news", dependencies=API_DEPS)
async def api_latest_news() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.latest_news()))


@app.get("/api/top-skills", dependencies=API_DEPS)
async def api_top_skills() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.top_skills()))


@app.get("/api/latest-reports", dependencies=API_DEPS)
async def api_latest_reports() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.latest_reports()))


@app.get("/api/security-score", dependencies=API_DEPS)
async def api_security_score() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.security_score()))


@app.get("/api/assets-summary", dependencies=API_DEPS)
async def api_assets_summary() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.assets_summary()))


@app.get("/api/activity-trend", dependencies=API_DEPS)
async def api_activity_trend() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.activity_trend()))
