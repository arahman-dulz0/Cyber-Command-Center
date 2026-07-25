#!/usr/bin/env bash
#
# backup.sh — logical backup of the platform database + knowledge base.
# Safe to run on a schedule (see install-crons.sh). Keeps the newest N backups.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${ROOT}/backups"
RETAIN="${BACKUP_RETAIN:-14}"
STAMP="$(date +%Y%m%d-%H%M%S)"
PG_CONTAINER="${PG_CONTAINER:-postgres}"

mkdir -p "${BACKUP_DIR}"

echo "==> [${STAMP}] Dumping database 'cyberdb' from container '${PG_CONTAINER}'…"
docker exec "${PG_CONTAINER}" pg_dump -U cyber -d cyberdb --clean --if-exists \
  | gzip > "${BACKUP_DIR}/cyberdb-${STAMP}.sql.gz"

if [[ -d "${ROOT}/knowledge" ]]; then
  echo "==> Archiving knowledge base…"
  tar -czf "${BACKUP_DIR}/knowledge-${STAMP}.tar.gz" -C "${ROOT}" knowledge 2>/dev/null || true
fi

# Retention: keep only the newest RETAIN of each kind.
echo "==> Pruning to newest ${RETAIN} backups…"
for prefix in cyberdb knowledge; do
  ls -1t "${BACKUP_DIR}/${prefix}-"*.gz 2>/dev/null | tail -n +"$((RETAIN + 1))" | xargs -r rm -f
done

size="$(du -h "${BACKUP_DIR}/cyberdb-${STAMP}.sql.gz" | cut -f1)"
echo "==> Done: ${BACKUP_DIR}/cyberdb-${STAMP}.sql.gz (${size})"
