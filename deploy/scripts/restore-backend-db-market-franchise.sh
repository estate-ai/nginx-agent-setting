#!/usr/bin/env bash
# backend-db service에 market/franchise 덤프를 복원한다.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STACK_FILE="${STACK_FILE:-$ROOT_DIR/compose/backend-public-stack.yml}"
COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-$ROOT_DIR/.env}"
DB_SERVICE="${DB_SERVICE:-backend-db}"
DUMP_DIR="${DUMP_DIR:-$ROOT_DIR/.local/backend-db-market-franchise}"
STACK_EXTRA_FILES="${STACK_EXTRA_FILES:-}"

if [[ -f "$COMPOSE_ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$COMPOSE_ENV_FILE"
  set +a
fi

STACK_FILE_PATH="$STACK_FILE"
if [[ -f "$STACK_FILE_PATH" ]]; then
  STACK_FILE_PATH="$(cd "$(dirname "$STACK_FILE_PATH")" && pwd)/$(basename "$STACK_FILE_PATH")"
fi

append_stack_extra_file_if_missing() {
  local extra_file="$1"
  if [[ -z "$STACK_EXTRA_FILES" ]]; then
    STACK_EXTRA_FILES="$extra_file"
    return 0
  fi

  case " $STACK_EXTRA_FILES " in
    *" $extra_file "*) ;;
    *) STACK_EXTRA_FILES="$STACK_EXTRA_FILES $extra_file" ;;
  esac
}

# 기본 공개 배포 스택에서는 restore 시점에만 dump 마운트 오버라이드를 덧붙인다.
if [[ "$STACK_FILE_PATH" == "$ROOT_DIR/compose/backend-public-stack.yml" ]]; then
  append_stack_extra_file_if_missing "$ROOT_DIR/compose/backend-db-market-franchise.dump.yml"
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

if [[ -n "$STACK_EXTRA_FILES" ]]; then
  # 공백 구분 추가 compose 파일을 순서대로 이어 붙인다.
  # shellcheck disable=SC2206
  EXTRA_STACK_FILES=( $STACK_EXTRA_FILES )
  for extra_stack_file in "${EXTRA_STACK_FILES[@]}"; do
    COMPOSE+=(-f "$extra_stack_file")
  done
fi

ensure_db_service() {
  echo ">> 0) backend-db를 restore 구성으로 시작"
  "${COMPOSE[@]}" up -d --build "$DB_SERVICE"
}

wait_for_db() {
  local max_attempts="${DB_READY_MAX_ATTEMPTS:-30}"
  local sleep_seconds="${DB_READY_SLEEP_SECONDS:-2}"
  local attempt=1

  echo ">> 1) backend-db 준비 대기"
  while (( attempt <= max_attempts )); do
    if "${COMPOSE[@]}" exec -T -e PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" "$DB_SERVICE" \
      psql -U postgres -d postgres -v ON_ERROR_STOP=1 -tAc "SELECT 1" >/dev/null 2>&1; then
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
  local max_attempts="${DB_READY_MAX_ATTEMPTS:-30}"
  local sleep_seconds="${DB_READY_SLEEP_SECONDS:-2}"
  local attempt=1
  local sql
  sql="$(cat)"

  while (( attempt <= max_attempts )); do
    if printf '%s\n' "$sql" | "${COMPOSE[@]}" exec -T -e PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" "$DB_SERVICE" \
      psql -U postgres -v ON_ERROR_STOP=1 "$@"; then
      return 0
    fi

    echo "psql 재시도 중... (${attempt}/${max_attempts})"
    sleep "$sleep_seconds"
    ((attempt++))
  done

  echo "psql 실행에 실패했습니다. docker compose logs $DB_SERVICE 로 상태를 확인해 주세요." >&2
  return 1
}

run_restore() {
  local max_attempts="${DB_READY_MAX_ATTEMPTS:-30}"
  local sleep_seconds="${DB_READY_SLEEP_SECONDS:-2}"
  local attempt=1

  while (( attempt <= max_attempts )); do
    if "${COMPOSE[@]}" exec -T -e PGPASSWORD="$POSTGRES_SUPERUSER_PASSWORD" "$DB_SERVICE" \
      pg_restore -U postgres --clean --if-exists --no-privileges "$@"; then
      return 0
    fi

    echo "pg_restore 재시도 중... (${attempt}/${max_attempts})"
    sleep "$sleep_seconds"
    ((attempt++))
  done

  echo "pg_restore 실행에 실패했습니다. docker compose logs $DB_SERVICE 로 상태를 확인해 주세요." >&2
  return 1
}

ensure_db_service
wait_for_db

echo ">> 2) 롤 생성"
run_psql -v market_password="$MARKET_DB_PASSWORD" -v franchise_password="$FRANCHISE_DB_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', 'market', :'market_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'market')\gexec
SELECT format('ALTER ROLE %I WITH LOGIN PASSWORD %L', 'market', :'market_password')
WHERE EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'market')\gexec
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', 'franchise', :'franchise_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'franchise')\gexec
SELECT format('ALTER ROLE %I WITH LOGIN PASSWORD %L', 'franchise', :'franchise_password')
WHERE EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'franchise')\gexec
SQL

echo ">> 3) 빈 DB 생성"
run_psql <<'SQL'
SELECT 'CREATE DATABASE market OWNER market'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'market')\gexec
SQL

run_psql <<'SQL'
SELECT 'CREATE DATABASE franchise OWNER franchise'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'franchise')\gexec
SQL

echo ">> 4) 복원"
run_restore -d market    /dump/market.dump
run_restore -d franchise /dump/franchise.dump

echo ">> 5) 검증"
run_psql -d market    -tAc "SELECT 'market rows: market_admin_dong_boundaries='||count(*) FROM market_admin_dong_boundaries;"
run_psql -d franchise -tAc "SELECT 'franchise rows: franchise_brands='||count(*) FROM franchise_brands;"
echo ">> done"
