#!/usr/bin/env bash
#
# install-crons.sh — install the platform's scheduled jobs into the user crontab.
# No sudo required. Idempotent (removes prior entries tagged 'cyber-command-center'
# before re-adding). Times are deliberately off the :00 mark.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "${ROOT}/backups"
tmp="$(mktemp)"

# Keep existing crontab minus our previous entries.
crontab -l 2>/dev/null | grep -v "cyber-command-center" > "${tmp}" || true

{
  echo "*/5 * * * * ${ROOT}/scripts/autoheal.sh >> ${ROOT}/backups/autoheal.log 2>&1 # cyber-command-center"
  echo "17 3 * * * ${ROOT}/scripts/backup.sh >> ${ROOT}/backups/backup.log 2>&1 # cyber-command-center"
} >> "${tmp}"

crontab "${tmp}"
rm -f "${tmp}"

echo "Installed cron jobs:"
echo "  • autoheal — every 5 minutes"
echo "  • backup   — daily at 03:17"
echo "View with:   crontab -l"
echo "Remove with: crontab -l | grep -v cyber-command-center | crontab -"
