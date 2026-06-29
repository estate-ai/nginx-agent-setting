#!/usr/bin/env bash
# frontend 배포 전에 Orval 산출물을 다시 생성한다.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT_DIR/.." && pwd)"
FRONTEND_DIR="$REPO_ROOT/frontend"
COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-$ROOT_DIR/.env}"

if [[ -f "$COMPOSE_ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$COMPOSE_ENV_FILE"
  set +a
fi

# root docker-compose.yml이 기대하는 이름과 deploy/.env 이름을 맞춘다.
export MARKET_DB_USERNAME="${MARKET_DB_USERNAME:-${MARKET_DB_USER:-}}"
export FRANCHISE_DB_USERNAME="${FRANCHISE_DB_USERNAME:-${FRANCHISE_DB_USER:-}}"
export NEXT_PUBLIC_API_ORIGIN="${NEXT_PUBLIC_API_ORIGIN:-${API_PUBLIC_ORIGIN:-}}"

: "${AUTHENTIK_SERVICE_ROLE_KEY:?set AUTHENTIK_SERVICE_ROLE_KEY}"
: "${MARKET_DB_PASSWORD:?set MARKET_DB_PASSWORD}"
: "${FRANCHISE_DB_PASSWORD:?set FRANCHISE_DB_PASSWORD}"
: "${MARKET_DB_USERNAME:?set MARKET_DB_USER}"
: "${FRANCHISE_DB_USERNAME:?set FRANCHISE_DB_USER}"
: "${NEXT_PUBLIC_API_ORIGIN:?set API_PUBLIC_ORIGIN}"

echo ">> frontend 의존성 설치"
(
  cd "$FRONTEND_DIR"
  npm ci
)

echo ">> frontend api:gen 실행"
(
  cd "$FRONTEND_DIR"
  npm run api:gen
)

echo ">> done"
