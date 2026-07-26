# Security & hardening guide (Stage 3)

How Cyber Command Center is secured, and how to harden a deployment further.
Threat model: a self-hosted platform on a home LAN, single operator, holding API
tokens and threat-intel data. Goals: least privilege, no secret leakage, an
audit trail, and safe exposure *if* it ever goes public.

## Authentication & access control

- **Dashboard** is protected by **HTTP Basic Auth** (`DASHBOARD_USER` /
  `DASHBOARD_PASS`). Credentials are compared in constant time. Set them in
  `.env` to enable; if unset the dashboard runs open and logs a warning.
- **`/api/*`** also accepts an **API key** (`X-API-Key: <DASHBOARD_API_KEY>`) for
  programmatic access, so scripts don't need the UI password.
- **`/healthz`** is intentionally unauthenticated (container healthcheck only;
  discloses nothing).
- **Discord bot RBAC** — administrative commands (`/monitor`, `/reload`, `/sync`)
  require the Discord **Administrator** permission (`app_commands.checks`).

## Rate limiting

A per-IP sliding-window limiter guards the dashboard (`DASHBOARD_RATE_LIMIT`
requests per `DASHBOARD_RATE_WINDOW` seconds, default 120/60). `429` with
`Retry-After` on exceed. `/healthz` is exempt.

## Security headers

The dashboard and the marketing site both send:

- `Content-Security-Policy` (locks script/style/img/font sources)
- `X-Frame-Options` (clickjacking) · `X-Content-Type-Options: nosniff`
- `Referrer-Policy` · `Permissions-Policy` (disables geolocation/camera/mic/…)
- `Strict-Transport-Security` — **only when served over HTTPS**
  (`DASHBOARD_HTTPS=true`). Never sent over plain HTTP, which would lock browsers
  out of the LAN site.
- The dashboard hides its server software (`--no-server-header`).

## Audit logging

The `audit_log` table records security-relevant actions from both surfaces:

| Source | Actions |
|--------|---------|
| Discord | `monitor.run`, `cog.reload`, `commands.sync`, `lab.add`, `lab.remove`, `ticket.close` |
| Dashboard | `auth.login`, `auth.fail` (with client IP) |

```sql
SELECT created_at, source, actor, action, target, ip
FROM audit_log ORDER BY created_at DESC LIMIT 50;
```

## Input validation & sanitisation

Free-text inputs (lab keywords, skill tags, machine names, notes) are normalised
to a safe character set and length-bounded (`utils/validation.py`) before storage
or echo. Slash-command types already constrain ints/choices; CVE ids are regex-
validated; uploaded KB files are type- and size-checked. Dashboard rendering
HTML-escapes all untrusted strings and restricts links to `http(s)`.

## Container hardening

Both app containers run:

- **Non-root** (bot as uid 1000; dashboard as the `cyber` user)
- `security_opt: no-new-privileges:true` — no setuid escalation
- `cap_drop: [ALL]` — zero Linux capabilities
- `read_only: true` root filesystem, with a small `tmpfs` for `/tmp` and only the
  logs directory bind-mounted writable (`PYTHONDONTWRITEBYTECODE` avoids pycache)
- Bounded json-file logging; healthchecks + autoheal (see `operations.md`)

The ops containers mount the Docker socket (autoheal read-write, Dozzle
read-only) — keep their ports on the LAN.

## Secret management

- All secrets live in a single **`.env`, git-ignored** (verified: no token has
  ever been committed). Tighten permissions: `chmod 600 .env`.
- Rotate anytime: Discord token (Developer Portal → Reset Token), HTB App Token,
  `DASHBOARD_PASS` / `DASHBOARD_API_KEY` (regenerate + restart).
- **Encryption at rest** — for off-box backups, encrypt the secrets:
  ```bash
  openssl enc -aes-256-cbc -pbkdf2 -salt -in .env -out .env.enc   # encrypt
  openssl enc -d -aes-256-cbc -pbkdf2 -in .env.enc -out .env      # decrypt
  ```
  Store `.env.enc` (never `.env`) in any remote backup. For stronger separation,
  use Docker secrets or SOPS/age; the compose `env_file` reference stays the same.

## fail2ban (only if exposed publicly)

Not needed on a private LAN. If you expose the dashboard, ban IPs that hammer the
`401`/`429` responses. A sample jail + filter is in `docs/fail2ban/` — point the
filter at the dashboard's log stream (e.g. `docker logs` piped to a file) and
enable the jail in `/etc/fail2ban/jail.local`.

## Going public (HTTPS)

Recommended: a **Cloudflare Tunnel** — free TLS, no open router ports, home IP
hidden, and Cloudflare Access can add an auth wall. Then set
`DASHBOARD_HTTPS=true` (enables HSTS) and bundle the dashboard's CDN assets
locally with Subresource Integrity for a strict CSP.

## Deployment hardening checklist

- [ ] `chmod 600 .env`
- [ ] `DASHBOARD_USER` / `DASHBOARD_PASS` set to strong values
- [ ] `DASHBOARD_API_KEY` set (and rotated) for programmatic access
- [ ] `./scripts/validate-env.sh` passes
- [ ] Containers show `read_only`, `cap_drop: ALL`, non-root (verify with
      `docker inspect`)
- [ ] Ops ports (3001/8888/8080) reachable on LAN only
- [ ] Backups running and **restore tested** (`restore.sh`)
- [ ] `DASHBOARD_HTTPS=true` only behind TLS
- [ ] Audit log reviewed periodically
