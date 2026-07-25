#!/usr/bin/env bash
#
# autoheal.sh — recreate app containers that have vanished entirely.
#
# The `restart: unless-stopped` policy and the autoheal container handle crashes
# and unhealthy states, but neither can recover a container that was *removed*
# (e.g. a compose run interrupted mid-deploy). This cron-friendly script detects
# a missing bot/dashboard and recreates it with `compose up -d`.
#
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
mkdir -p "${ROOT}/backups"

check() {
  local file="$1" name="$2"
  if ! docker ps --format '{{.Names}}' | grep -qx "${name}"; then
    echo "$(date -Is) [autoheal] ${name} not running — recreating"
    docker compose -f "${file}" up -d >/dev/null 2>&1 \
      || echo "$(date -Is) [autoheal] FAILED to start ${name}"
  fi
}

check "docker/bot.yml" "cyber-discord-bot"
check "docker/dashboard.yml" "cyber-dashboard"
