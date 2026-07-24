#!/usr/bin/env bash
#
# deploy.sh — build & (re)start the Cyber Command Center Discord bot on the server.
#
# Run this from the project root on the Ubuntu server:
#   ./scripts/deploy.sh
#
set -euo pipefail

# Resolve project root (parent of this script's directory).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

COMPOSE_FILE="docker/bot.yml"

echo "==> Cyber Command Center — bot deployment"
echo "    project root: ${PROJECT_ROOT}"

# 1) Sanity checks -----------------------------------------------------------
if [[ ! -f ".env" ]]; then
  echo "ERROR: .env not found in ${PROJECT_ROOT}."
  echo "       Copy services/discord-bot/.env.example to .env and fill it in."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker is not installed or not on PATH."
  exit 1
fi

# Pick the right compose invocation (plugin vs legacy).
if docker compose version >/dev/null 2>&1; then
  DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  DC="docker-compose"
else
  echo "ERROR: neither 'docker compose' nor 'docker-compose' is available."
  exit 1
fi

# 2) Build & restart ---------------------------------------------------------
echo "==> Building image and starting the bot…"
${DC} -f "${COMPOSE_FILE}" up -d --build

# 3) Show status -------------------------------------------------------------
echo "==> Running containers:"
${DC} -f "${COMPOSE_FILE}" ps

echo ""
echo "==> Tail logs with:"
echo "    ${DC} -f ${COMPOSE_FILE} logs -f"
echo "==> Done."
