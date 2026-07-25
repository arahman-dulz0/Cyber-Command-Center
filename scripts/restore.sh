#!/usr/bin/env bash
#
# restore.sh — restore the database from a backup produced by backup.sh.
# Destructive: overwrites the current cyberdb. Requires explicit confirmation.
#
#   ./scripts/restore.sh backups/cyberdb-YYYYMMDD-HHMMSS.sql.gz
#
set -euo pipefail

FILE="${1:-}"
PG_CONTAINER="${PG_CONTAINER:-postgres}"

if [[ -z "${FILE}" ]]; then
  echo "usage: restore.sh <cyberdb-YYYYMMDD-HHMMSS.sql.gz>"
  echo "available backups:"
  ls -1t "$(dirname "${BASH_SOURCE[0]}")/../backups/"cyberdb-*.sql.gz 2>/dev/null || echo "  (none)"
  exit 1
fi
[[ -f "${FILE}" ]] || { echo "not found: ${FILE}"; exit 1; }

echo "!! This will DROP and REPLACE the 'cyberdb' database from:"
echo "   ${FILE}"
read -r -p "Type 'restore' to proceed: " ans
[[ "${ans}" == "restore" ]] || { echo "aborted."; exit 1; }

echo "==> Restoring…"
gunzip -c "${FILE}" | docker exec -i "${PG_CONTAINER}" psql -U cyber -d cyberdb -q

echo "==> Restored. Recreate the bot so it reconnects cleanly:"
echo "    docker compose -f docker/bot.yml up -d"
