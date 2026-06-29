#!/usr/bin/env bash
# backend-db service에 market/franchise 덤프를 복원한다.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STACK_FILE="${STACK_FILE:-$ROOT_DIR/compose/backend-public-stack.yml}"
COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-$ROOT_DIR/.env}"
DB_SERVICE="${DB_SERVICE:-backend-db}"
DUMP_DIR="${DUMP_DIR:-$ROOT_DIR/.local/backend-db-market-franchise}"

if [[ -f "$COMPOSE_ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$COMPOSE_ENV_FILE"
  set +a
fi

POSTGRES_SUPERUSER_PASSWORD="${BACKEND_DB_POSTGRES_PASSWORD:-${POSTGRES_PASSWORD:-}}"

: "${POSTGRES_SUPERUSER_PASSWORD:?set BACKEND_DB_POSTGRES_PASSWORD}"
: "${MARKET_DB_PASSWORD:?set MARKET_DB_PASSWORD}"
: "${FRANCHISE_DB_PASSWORD:?set FRANCHISE_DB_PASSWORD}"

if [[ ! -f "$DUMP_DIR/market.dump" ]]; then
  echo "market.dump 파일이 없습니다: $DUMP_DIR/market.dump" >&2
  exit 1
fi

if [[ ! -f "$DUMP_DIR/franchise.dump" ]]; then
  echo "franchise.dump 파일이 없습니다: $DUMP_DIR/franchise.dump" >&2
  exit 1
fi

COMPOSE=(docker compose --env-file "$COMPOSE_ENV_FILE" -f "$STACK_FILE")

wait_for_db() {
  local max_attempts="${DB_READY_MAX_ATTEMPTS:-30}"
  local sleep_seconds="${DB_READY_SLEEP_SECONDS:-2}"
  local attempt=1

  echo ">> 0) backend-db 준비 대기"
  while (( attempt <= max_attempts )); do
    if "${COMPOSE[@]}" exec -T -e PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" "$DB_SERVICE" \
      pg_isready -U postgres -d postgres >/dev/null 2>&1; then
      echo "backend-db가 준비되었습니다."
      return 0
    fi

    echo "backend-db 준비 중... (${attempt}/${max_attempts})"
    sleep "$sleep_seconds"
    ((attempt++))
  done

  echo "backend-db가 준비되지 않았습니다. docker compose logs $DB_SERVICE 로 상태를 확인해 주세요." >&2
  return 1
}

run_psql() {
  "${COMPOSE[@]}" exec -T -e PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" "$DB_SERVICE" \
    psql -U postgres -v ON_ERROR_STOP=1 "$@"
}

run_restore() {
  "${COMPOSE[@]}" exec -T -e PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" "$DB_SERVICE" \
    pg_restore -U postgres --no-privileges "$@"
}

wait_for_db

echo ">> 1) 롤 생성"
run_psql <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'market') THEN
    CREATE ROLE market LOGIN PASSWORD '${MARKET_DB_PASSWORD}';
  ELSE
    ALTER ROLE market WITH LOGIN PASSWORD '${MARKET_DB_PASSWORD}';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'franchise') THEN
    CREATE ROLE franchise LOGIN PASSWORD '${FRANCHISE_DB_PASSWORD}';
  ELSE
    ALTER ROLE franchise WITH LOGIN PASSWORD '${FRANCHISE_DB_PASSWORD}';
  END IF;
END
\$\$;
SQL

echo ">> 2) 빈 DB 생성"
run_psql <<'SQL'
SELECT 'CREATE DATABASE market OWNER market'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'market')\gexec
SQL

run_psql <<'SQL'
SELECT 'CREATE DATABASE franchise OWNER franchise'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'franchise')\gexec
SQL

echo ">> 3) 복원"
run_restore -d market    /dump/market.dump
run_restore -d franchise /dump/franchise.dump

echo ">> 4) 검증"
run_psql -d market    -tAc "SELECT 'market rows: market_admin_dong_boundaries='||count(*) FROM market_admin_dong_boundaries;"
run_psql -d franchise -tAc "SELECT 'franchise rows: franchise_brands='||count(*) FROM franchise_brands;"
echo ">> done"
