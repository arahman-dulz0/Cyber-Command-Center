# Phase 8 — Automation & Actioning

The platform stops just *notifying* and starts *acting*: when a high-priority CVE
hits **your** stack, it auto-raises a ticket, generates a remediation checklist,
and escalates — the last mile of a real SOC.

```
fused CVE (Phase 3)
   │  priority ≥ ACTION_MIN_PRIORITY?
   ▼
match against your lab inventory  ──no──▶ (just the normal #cve-alert post)
   │ yes
   ▼
open ticket → AI remediation checklist → escalate to #announcements → (optional email)
```

## Commands

| Command | What it does |
|---------|--------------|
| `/lab add <tech> [note]` | Add a technology to your inventory (e.g. `vmware`, `apache`, `wordpress`). |
| `/lab list` | Show your inventory. |
| `/lab remove <tech>` | Remove an entry. |
| `/tickets` | Open action tickets (auto-raised). |
| `/ticket-close <id>` | Close a ticket. |

## How actioning works

Hooked into the CVE monitor: after a fused CVE is posted to `#cve-alert`, the
**action engine** checks it. If its **CCC priority ≥ `ACTION_MIN_PRIORITY`** (default
80) **and** a lab-inventory keyword appears as a whole word in the CVE's products
or description, it:

1. **Raises a ticket** in `tickets` (one open ticket per CVE — deduped).
2. **Generates a remediation checklist** with the local AI (4–6 concrete steps;
   deterministic fallback if the model is offline).
3. **Escalates** a red "🚨 ACTION REQUIRED" embed to `#announcements`.
4. **Emails** you — *only if* SMTP is configured (opt-in).

Verified live: lab asset `apache` matched Log4Shell (priority 100) → ticket +
checklist ("Update Log4j2… Disable JNDI features…").

## Architecture

```
actioning/engine.py      ← match → ticket → AI checklist → escalate (+email)
utils/notify.py          ← optional SMTP notifier (disabled unless configured)
cogs/lab.py              ← /lab, /tickets, /ticket-close
tasks/cve_monitor.py     ← calls action_engine.evaluate() per posted CVE
services/dashboard/      ← "Open tickets" stat tile
```

## Database

`lab_assets` + `tickets` (migration `docs/migrations/007_phase8.sql`,
auto-applied). One open ticket per CVE is enforced by a partial unique index.

## Configuration (`.env`)

```
ACTION_ENABLED=true
ACTION_MIN_PRIORITY=80     # lab-matching CVEs at/above this raise a ticket
# Optional email (leave SMTP_HOST empty to disable):
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_TO=
```

## Getting started

```
/lab add vmware
/lab add apache
/lab add wordpress
```
From then on, any critical CVE touching those auto-becomes a ticket + escalation.
Check `/tickets` or the dashboard's "Open tickets" tile.

## Testing checklist

- [ ] `/lab add apache` then `/lab list` shows it.
- [ ] A priority-≥80 CVE mentioning a lab asset raises a ticket + posts to `#announcements`.
- [ ] `/tickets` lists it; `/ticket-close <id>` closes it.
- [ ] Re-detecting the same CVE does NOT open a second ticket (dedup).
- [ ] With SMTP set, an email is sent; without, it's silently skipped.

## Rollback

`ACTION_ENABLED=false` disables the engine (alerts still post normally). Email is
off unless SMTP is set. Tables are harmless to leave.
