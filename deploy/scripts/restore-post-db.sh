#!/usr/bin/env bash
# post-db service에 post-service 덤프를 복원한다.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STACK_FILE="${STACK_FILE:-$ROOT_DIR/compose/backend-public-stack.yml}"
COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-$ROOT_DIR/.env}"
DB_SERVICE="${DB_SERVICE:-post-db}"
DUMP_DIR="${DUMP_DIR:-$ROOT_DIR/.local/post-db}"
DUMP_FILE="${DUMP_FILE:-$DUMP_DIR/post.dump}"
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

# 기본 공개 배포 스택에서는 restore 시점에만 post dump 마운트 오버라이드를 덧붙인다.
if [[ "$STACK_FILE_PATH" == "$ROOT_DIR/compose/backend-public-stack.yml" ]]; then
  append_stack_extra_file_if_missing "$ROOT_DIR/compose/post-db.dump.yml"
fi

POST_DB_NAME="${POST_DB_NAME:-post}"
POST_DB_USER="${POST_DB_USER:-post}"
POST_DB_PASSWORD="${POST_DB_PASSWORD:?set POST_DB_PASSWORD}"

if [[ ! -f "$DUMP_FILE" ]]; then
  echo "post.dump 파일이 없습니다: $DUMP_FILE" >&2
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
  echo ">> post 0) post-db를 restore 구성으로 시작"
  "${COMPOSE[@]}" up -d "$DB_SERVICE"
}

wait_for_db() {
  local max_attempts="${DB_READY_MAX_ATTEMPTS:-30}"
  local sleep_seconds="${DB_READY_SLEEP_SECONDS:-2}"
  local attempt=1

  echo ">> post 1) post-db 준비 대기"
  while (( attempt <= max_attempts )); do
    if "${COMPOSE[@]}" exec -T -e PGPASSWORD="$POST_DB_PASSWORD" "$DB_SERVICE" \
      pg_isready -U "$POST_DB_USER" -d "$POST_DB_NAME" >/dev/null 2>&1; then
      echo "post-db가 준비되었습니다."
      return 0
    fi

    echo "post-db 준비 중... (${attempt}/${max_attempts})"
    sleep "$sleep_seconds"
    ((attempt++))
  done

  echo "post-db가 준비되지 않았습니다. docker compose logs $DB_SERVICE 로 상태를 확인해 주세요." >&2
  return 1
}

run_psql() {
  "${COMPOSE[@]}" exec -T -e PGPASSWORD="$POST_DB_PASSWORD" "$DB_SERVICE" \
    psql -U "$POST_DB_USER" -v ON_ERROR_STOP=1 "$@"
}

run_restore() {
  "${COMPOSE[@]}" exec -T -e PGPASSWORD="$POST_DB_PASSWORD" "$DB_SERVICE" \
    pg_restore -U "$POST_DB_USER" --clean --if-exists --no-owner --no-privileges "$@"
}

ensure_db_service
wait_for_db

echo ">> post 2) post DB 생성 확인"
run_psql -d postgres <<SQL
SELECT 'CREATE DATABASE $POST_DB_NAME OWNER $POST_DB_USER'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '$POST_DB_NAME')\gexec
SQL

echo ">> post 3) 복원"
run_restore -d "$POST_DB_NAME" /dump/post.dump

echo ">> post 4) 검증"
run_psql -d "$POST_DB_NAME" -tAc "SELECT 'post rows: posts='||count(*) FROM posts;"
echo ">> post done"
