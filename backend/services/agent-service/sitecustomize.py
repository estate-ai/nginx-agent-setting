# backend/services/agent-service/sitecustomize.py
from __future__ import annotations

import copy
import os
import sys
from typing import Any

PATCH_ENABLED = os.getenv("PATCH_LANGGRAPH_STREAM_MODES", "true").lower() not in {
    "0",
    "false",
    "no",
}

# langgraph-api 0.9.0의 bundled OpenAPI validator가 "tools", "lifecycle"을 누락한다.
# SDK/useStream 계약상 "tools"는 정상 stream_mode라 요청 body는 그대로 둔다.
# 이 패치는 langgraph_api.validation import 전에 validator schema만 보정한다.
# 제거 기준: upstream fix 포함 stable langgraph-api로 업그레이드할 때.
# https://github.com/langchain-ai/langgraph/issues/7986
# https://docs.langchain.com/oss/javascript/langgraph/streaming#tool-progress
EXTRA_STREAM_MODES = ("tools", "lifecycle")

STREAM_MODE_ENUM_FINGERPRINT = {
    "values",
    "messages",
    "messages-tuple",
    "tasks",
    "checkpoints",
    "updates",
    "events",
    "debug",
    "custom",
}


def _patch_stream_mode_enum(value: Any) -> int:
    patched = 0

    if isinstance(value, dict):
        enum = value.get("enum")

        if isinstance(enum, list):
            enum_set = set(enum)

            if STREAM_MODE_ENUM_FINGERPRINT.issubset(enum_set):
                for mode in EXTRA_STREAM_MODES:
                    if mode not in enum_set:
                        enum.append(mode)
                        enum_set.add(mode)
                        patched += 1

        for child in value.values():
            patched += _patch_stream_mode_enum(child)

    elif isinstance(value, list):
        for child in value:
            patched += _patch_stream_mode_enum(child)

    return patched


def _install_patch() -> None:
    if not PATCH_ENABLED:
        return

    try:
        import jsonschema_rs
    except Exception as exc:
        print(f"[langgraph-patch] jsonschema_rs import 실패: {exc}", file=sys.stderr)
        return

    original_validator_for = jsonschema_rs.validator_for

    def patched_validator_for(schema: Any, *args: Any, **kwargs: Any) -> Any:
        patched_schema = copy.deepcopy(schema)
        patched_count = _patch_stream_mode_enum(patched_schema)

        if patched_count:
            print(
                f"[langgraph-patch] stream_mode enum 보정: {patched_count}",
                file=sys.stderr,
            )

        return original_validator_for(patched_schema, *args, **kwargs)

    jsonschema_rs.validator_for = patched_validator_for

    print("[langgraph-patch] jsonschema_rs.validator_for 패치 설치 완료", file=sys.stderr)


_install_patch()
