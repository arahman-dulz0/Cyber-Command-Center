"""
Cyber Command Center — web dashboard (Phase 6).

A lightweight FastAPI app that renders a dark, SOC-style dashboard and serves
JSON endpoints the frontend polls. Read-only over the shared PostgreSQL.
"""

from __future__ import annotations

import datetime as _dt
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from db import dashboard

_TEMPLATE = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await dashboard.connect()
    yield
    await dashboard.close()


app = FastAPI(title="Cyber Command Center", lifespan=lifespan)


def _clean(obj):
    """Make DB rows JSON-serialisable (datetimes → ISO)."""
    if isinstance(obj, list):
        return [_clean(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, _dt.datetime):
        return obj.isoformat()
    return obj


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return _TEMPLATE


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}


@app.get("/api/summary")
async def api_summary() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.summary()))


@app.get("/api/cve-timeline")
async def api_cve_timeline() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.cve_timeline()))


@app.get("/api/priority-distribution")
async def api_priority_distribution() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.priority_distribution()))


@app.get("/api/latest-alerts")
async def api_latest_alerts() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.latest_alerts()))


@app.get("/api/latest-news")
async def api_latest_news() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.latest_news()))


@app.get("/api/top-skills")
async def api_top_skills() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.top_skills()))


@app.get("/api/latest-reports")
async def api_latest_reports() -> JSONResponse:
    return JSONResponse(_clean(await dashboard.latest_reports()))
