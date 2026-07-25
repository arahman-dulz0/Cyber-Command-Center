#!/usr/bin/env bash
#
# validate-env.sh — preflight check before deploying.
# Verifies required .env keys are set and backing services are reachable.
# Exit 0 = all good, 1 = something is wrong.
#
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT}/.env"
PG_CONTAINER="${PG_CONTAINER:-postgres}"
REDIS_CONTAINER="${REDIS_CONTAINER:-redis}"
fail=0

echo "== .env keys =="
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "  ✗ .env missing at ${ENV_FILE}"
  exit 1
fi
REQUIRED=(DISCORD_TOKEN DISCORD_GUILD_ID POSTGRES_HOST POSTGRES_USER
  POSTGRES_PASSWORD POSTGRES_DB REDIS_HOST OLLAMA_HOST OLLAMA_MODEL)
for k in "${REQUIRED[@]}"; do
  v="$(grep -E "^${k}=" "${ENV_FILE}" | head -1 | cut -d= -f2-)"
  if [[ -z "${v}" ]]; then
    echo "  ✗ ${k} is empty"
    fail=1
  else
    echo "  ✓ ${k}"
  fi
done

echo "== services =="
if docker exec "${PG_CONTAINER}" pg_isready -U cyber >/dev/null 2>&1; then
  echo "  ✓ postgres accepting connections"
else
  echo "  ✗ postgres not ready"
  fail=1
fi
if docker exec "${REDIS_CONTAINER}" redis-cli ping >/dev/null 2>&1; then
  echo "  ✓ redis responding"
else
  echo "  ✗ redis not responding"
  fail=1
fi
MODEL="$(grep -E "^OLLAMA_MODEL=" "${ENV_FILE}" | cut -d= -f2-)"
if command -v ollama >/dev/null 2>&1 && ollama list 2>/dev/null | grep -q "${MODEL%%:*}"; then
  echo "  ✓ ollama model '${MODEL}' present"
else
  echo "  ✗ ollama model '${MODEL}' not pulled (run: ollama pull ${MODEL})"
  fail=1
fi

echo "======================================"
if [[ "${fail}" -eq 0 ]]; then
  echo "VALIDATION PASSED ✓"
else
  echo "VALIDATION FAILED ✗ — fix the items above before deploying."
fi
exit "${fail}"
