#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BLUEPRINT_FILE="${BLUEPRINT_FILE:-$ROOT_DIR/authentik/pickle-web.yaml}"
COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-$ROOT_DIR/.env}"
VALIDATE_DEPLOY_ENV_SCRIPT="${VALIDATE_DEPLOY_ENV_SCRIPT:-$ROOT_DIR/scripts/validate-deploy-env.sh}"

test -f "$BLUEPRINT_FILE"

bash "$VALIDATE_DEPLOY_ENV_SCRIPT" "$COMPOSE_ENV_FILE"

# authentik-worker의 blueprint watcher가 env 변경 후에도 재평가하도록
# 동일 내용을 다시 기록해 파일 변경 이벤트를 발생시킨다.
tmp_file="$(mktemp)"
cp "$BLUEPRINT_FILE" "$tmp_file"
cat "$tmp_file" > "$BLUEPRINT_FILE"
rm -f "$tmp_file"

echo ">> authentik blueprint refresh triggered"
