"""
Security layer for the dashboard.

- Security headers (CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy;
  HSTS only when served over HTTPS).
- Sliding-window rate limiting per client IP.
- Authentication: HTTP Basic Auth for the UI, plus an X-API-Key alternative for
  programmatic access to /api. Both are constant-time compared.
- Auth events are written to the shared audit_log.

All of it is env-gated: if no credentials are configured, the dashboard runs
open (LAN mode) but logs a warning.
"""

from __future__ import annotations

import base64
import hmac
import os
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from db import dashboard

DASH_USER = os.getenv("DASHBOARD_USER", "")
DASH_PASS = os.getenv("DASHBOARD_PASS", "")
API_KEY = os.getenv("DASHBOARD_API_KEY", "")
HTTPS = os.getenv("DASHBOARD_HTTPS", "false").lower() in {"1", "true", "yes", "on"}
RATE_LIMIT = int(os.getenv("DASHBOARD_RATE_LIMIT", "120"))
RATE_WINDOW = int(os.getenv("DASHBOARD_RATE_WINDOW", "60"))

AUTH_ENABLED = bool(DASH_USER and DASH_PASS)

_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data:; font-src 'self' data:; connect-src 'self'; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        resp: Response = await call_next(request)
        resp.headers["Content-Security-Policy"] = _CSP
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        if HTTPS:
            resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        resp.headers["Server"] = "ccc"
        return resp


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = RATE_LIMIT, window: int = RATE_WINDOW):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/healthz":
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        dq = self._hits[ip]
        while dq and dq[0] <= now - self.window:
            dq.popleft()
        if len(dq) >= self.limit:
            return JSONResponse(
                {"error": "rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": str(self.window)},
            )
        dq.append(now)
        return await call_next(request)


def _valid_basic(header: str) -> str | None:
    """Return the username on a valid Basic credential, else None."""
    try:
        scheme, cred = header.split(" ", 1)
        if scheme.lower() != "basic":
            return None
        user, _, pw = base64.b64decode(cred).decode("utf-8").partition(":")
    except Exception:
        return None
    ok = hmac.compare_digest(user, DASH_USER) and hmac.compare_digest(pw, DASH_PASS)
    return user if ok else None


def _valid_api_key(request: Request) -> bool:
    key = request.headers.get("x-api-key", "")
    return bool(API_KEY) and hmac.compare_digest(key, API_KEY)


async def _audit(request: Request, action: str, actor: str | None) -> None:
    ip = request.client.host if request.client else None
    try:
        await dashboard.audit(actor=actor, action=action, source="dashboard", ip=ip)
    except Exception:
        pass


async def _authenticate(request: Request, allow_api_key: bool) -> str | None:
    """Return the authenticated principal, None in open mode, or raise 401."""
    if not AUTH_ENABLED and not API_KEY:
        return None  # open / LAN mode

    if allow_api_key and _valid_api_key(request):
        return "api-key"

    if AUTH_ENABLED:
        user = _valid_basic(request.headers.get("authorization", ""))
        if user:
            return user

    await _audit(request, "auth.fail", actor=None)
    raise HTTPException(
        status_code=401,
        detail="Unauthorized",
        headers={"WWW-Authenticate": 'Basic realm="Cyber Command Center"'},
    )


async def require_auth(request: Request) -> None:
    """FastAPI dependency for /api — Basic Auth OR X-API-Key."""
    await _authenticate(request, allow_api_key=True)


async def require_ui_auth(request: Request) -> None:
    """FastAPI dependency for the HTML page — Basic only, logs the page view."""
    user = await _authenticate(request, allow_api_key=False)
    if AUTH_ENABLED and user:
        await _audit(request, "auth.login", actor=user)
