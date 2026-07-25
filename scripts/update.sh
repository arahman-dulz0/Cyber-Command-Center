#!/usr/bin/env bash
#
# update.sh — safe auto-update for the locally-built app containers.
# Pulls the latest code, validates the environment, rebuilds and redeploys the
# bot and dashboard. Backs up the database first. Cron-friendly.
#
#   ./scripts/update.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

echo "==> Backing up before update…"
"${ROOT}/scripts/backup.sh" || { echo "backup failed — aborting update"; exit 1; }

if [[ -d "${ROOT}/.git" ]]; then
  echo "==> Pulling latest code…"
  git pull --ff-only || { echo "git pull failed — aborting"; exit 1; }
fi

echo "==> Validating environment…"
"${ROOT}/scripts/validate-env.sh" || { echo "validation failed — aborting update"; exit 1; }

echo "==> Rebuilding and redeploying…"
docker compose -f docker/bot.yml up -d --build
docker compose -f docker/dashboard.yml up -d --build

echo "==> Update complete. Recent bot log:"
docker logs --tail 5 cyber-discord-bot 2>&1 | tail -5
