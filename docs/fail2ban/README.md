# fail2ban for the dashboard (optional — only if publicly exposed)

Not required on a private LAN. If you expose the dashboard to the internet, use
these to ban IPs that repeatedly hit `401` (auth failures) or `429` (rate limit).

## Setup (host-level, needs sudo)

1. Stream the dashboard logs to a file fail2ban can read:
   ```bash
   # e.g. a systemd unit or cron that appends container logs
   docker logs -f cyber-dashboard >> /var/log/ccc-dashboard.log 2>&1 &
   ```
   (Better: run the dashboard behind a reverse proxy — Caddy/Nginx — and point
   fail2ban at the proxy's access log, which includes real client IPs.)

2. Install the filter and jail:
   ```bash
   sudo cp ccc-dashboard.conf /etc/fail2ban/filter.d/
   sudo cp jail.local /etc/fail2ban/jail.local     # or merge into your existing one
   sudo systemctl reload fail2ban
   sudo fail2ban-client status ccc-dashboard
   ```

Behind Cloudflare Tunnel, prefer Cloudflare's own rate-limiting / WAF and
Cloudflare Access over host fail2ban, since the origin only sees Cloudflare IPs.
