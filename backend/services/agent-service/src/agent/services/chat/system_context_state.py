from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import BaseUser

from agent.clients.onboarding_service import onboarding_service_client
from agent.db.session import get_session_factory
from agent.repositories.workspace import (
    artifact_repository,
    content_repository,
    document_repository,
    market_favorite_repository,
    memory_repository,
    onboarding_context_repository,
)
from agent.services.chat.context import ChatRuntimeContext
from agent.services.chat.state import (
    MemorySummary,
    OnboardingSummary,
    SelectedArtifactContextState,
    SelectedDocumentContextState,
    SelectedMarketAreaContextState,
    SystemContextRefreshState,
    SystemContextState,
    UserMemoryContextState,
)
from agent.services.chat.tools.runtime_user import (
    extract_runtime_value,
)


def empty_system_context_state() -> SystemContextState:
    return {
        "selected_documents": [],
        "selected_artifacts": [],
        "selected_market_areas": [],
        "user_memories": [],
        "memory_summary": None,
        "onboarding_summary": None,
    }


def clean_system_context_refresh_state() -> SystemContextRefreshState:
    return {
        "memory_summary_dirty": False,
        "onboarding_summary_dirty": False,
    }


def parse_selected_ids(raw_ids: object) -> list[UUID]:
    """실행 컨텍스트의 선택 ID 목록을 UUID list로 검증한다."""

    if not isinstance(raw_ids, list):
        raise ValueError("selected ids must be a list")
    resolved_ids: list[UUID] = []
    for raw_id in raw_ids:
        if not isinstance(raw_id, str):
            raise ValueError("selected id must be a string")
        try:
            resolved_ids.append(UUID(raw_id))
        except ValueError:
            raise ValueError(f"selected id is not a UUID: {raw_id}") from None
    return resolved_ids


def parse_selected_dong_codes(raw_codes: object) -> list[str]:
    """실행 컨텍스트의 선택 행정동 코드 목록을 검증한다."""

    if not isinstance(raw_codes, list):
        raise ValueError("selected market dong codes must be a list")
    resolved_codes: list[str] = []
    for raw_code in raw_codes:
        if not isinstance(raw_code, str):
            raise ValueError("selected market dong code must be a string")
        code = raw_code.strip()
        if not code:
            raise ValueError("selected market dong code must not be empty")
        if code not in resolved_codes:
            resolved_codes.append(code)
    return resolved_codes


def _runtime_context_mapping(
    context: ChatRuntimeContext | None,
) -> Mapping[str, Any] | None:
    return context if isinstance(context, Mapping) else None


def _runtime_context_value(
    config: RunnableConfig,
    context: ChatRuntimeContext | None,
    key: str,
) -> Any:
    return extract_runtime_value(config, _runtime_context_mapping(context), key)


def extract_authenticated_user_identity(server_user: BaseUser | None) -> str | None:
    """LangGraph Server가 Runtime.server_info.user에 주입한 사용자 식별자를 읽는다.

    config.configurable.langgraph_auth_user는 서버 내부 worker 전달 구현 세부사항이므로
    애플리케이션 노드에서는 Runtime.server_info.user만 인증 사용자 경로로 사용한다.
    https://docs.langchain.com/oss/python/langchain/tools#server-info
    """

    if server_user is None:
        return None
    identity = server_user.identity
    return identity if isinstance(identity, str) and identity else None


def extract_authenticated_user_access_token(server_user: BaseUser | None) -> str | None:
    """LangGraph Server 인증 사용자에 실어 보낸 액세스 토큰을 읽는다.

    onboarding-service 같은 사용자 위임 호출은 authenticate 반환값에 포함된
    access_token을 그대로 사용한다.
    """

    if server_user is None or "access_token" not in server_user:
        return None
    access_token = server_user["access_token"]
    return access_token if isinstance(access_token, str) and access_token else None


def extract_app_thread_id(
    context: ChatRuntimeContext | None, config: RunnableConfig | None = None
) -> UUID | None:
    raw_thread_id = (
        _runtime_context_value(config, context, "app_thread_id")
        if config is not None
        else (context or {}).get("app_thread_id")
    )
    if not isinstance(raw_thread_id, str):
        return None
    try:
        return UUID(raw_thread_id)
    except ValueError:
        return None


def _runtime_configurable_mapping(config: RunnableConfig) -> Mapping[str, Any] | None:
    configurable = config.get("configurable", {})
    return configurable if isinstance(configurable, Mapping) else None


def _has_runtime_value(
    config: RunnableConfig,
    context: ChatRuntimeContext | None,
    key: str,
) -> bool:
    context_mapping = _runtime_context_mapping(context)
    if context_mapping is not None and key in context_mapping:
        return True

    configurable = _runtime_configurable_mapping(config)
    return configurable is not None and key in configurable


def _normalize_client_surface(raw_surface: object) -> str | None:
    if not isinstance(raw_surface, str):
        return None
    normalized = raw_surface.strip().lower()
    return normalized if normalized == "map" else None


def _normalize_optional_context_string(raw_value: object) -> str | None:
    if raw_value is None:
        return None
    if not isinstance(raw_value, str):
        raise ValueError("selected onboarding context value must be a string or null")
    normalized = raw_value.strip()
    return normalized or None


async def _build_selected_document_states(
    owner: str | None,
    *,
    raw_ids: object,
) -> list[SelectedDocumentContextState]:
    if owner is None:
        raise ValueError("authenticated user is required for selected documents")
    selected_document_ids = parse_selected_ids(raw_ids)
    if not selected_document_ids:
        return []

    async with get_session_factory()() as session:
        document_records = await document_repository.list_by_ids(
            session, owner, selected_document_ids
        )
        contents = {
            content.id: content
            for content in await content_repository.list_by_ids(
                session, [record.content_id for record in document_records]
            )
        }

    found_ids = {record.id for record in document_records}
    missing_ids = set(selected_document_ids) - found_ids
    if missing_ids:
        raise ValueError("selected documents must belong to the authenticated user")

    return [
        {
            "id": str(record.id),
            "type": content.type,
            "title": content.title,
            "summary": content.summary,
        }
        for record in document_records
        if (content := contents.get(record.content_id)) is not None
    ]


async def _build_selected_artifact_states(
    owner: str | None,
    *,
    raw_ids: object,
) -> list[SelectedArtifactContextState]:
    if owner is None:
        raise ValueError("authenticated user is required for selected artifacts")
    selected_artifact_ids = parse_selected_ids(raw_ids)
    if not selected_artifact_ids:
        return []

    async with get_session_factory()() as session:
        artifact_records = await artifact_repository.list_by_ids(
            session, owner, selected_artifact_ids
        )
        contents = {
            content.id: content
            for content in await content_repository.list_by_ids(
                session, [record.content_id for record in artifact_records]
            )
        }

    found_ids = {record.id for record in artifact_records}
    missing_ids = set(selected_artifact_ids) - found_ids
    if missing_ids:
        raise ValueError("selected artifacts must belong to the authenticated user")

    return [
        {
            "id": str(record.id),
            "type": content.type,
            "title": content.title,
            "summary": content.summary,
            "version": record.version,
        }
        for record in artifact_records
        if (content := contents.get(record.content_id)) is not None
    ]


async def _build_selected_market_area_states(
    owner: str | None,
    *,
    raw_codes: object,
) -> list[SelectedMarketAreaContextState]:
    if owner is None:
        raise ValueError("authenticated user is required for selected market areas")
    selected_dong_codes = parse_selected_dong_codes(raw_codes)
    if not selected_dong_codes:
        return []

    async with get_session_factory()() as session:
        records = await market_favorite_repository.list_by_dong_codes(
            session, owner, selected_dong_codes
        )

    found_codes = {record.dong_code for record in records}
    missing_codes = set(selected_dong_codes) - found_codes
    if missing_codes:
        raise ValueError("selected market areas must belong to the authenticated user")

    return [
        {
            "dong_code": record.dong_code,
            "dong_name": record.dong_name,
        }
        for record in records
    ]


async def _build_memory_summary(owner: str | None) -> MemorySummary | None:
    if owner is None:
        return None
    async with get_session_factory()() as session:
        memory_count = await memory_repository.count_enabled(session, owner)
    return {
        "has_memories": memory_count > 0,
        "memory_count": memory_count,
    }


async def _build_user_memories(
    owner: str | None,
    *,
    limit: int = 10,
) -> list[UserMemoryContextState]:
    if owner is None:
        return []
    async with get_session_factory()() as session:
        records = await memory_repository.list(session, owner, enabled_only=True, limit=limit)
    return [
        {
            "id": str(record.id),
            "content": record.content,
            "source": record.source,
        }
        for record in records
    ]


async def _build_thread_onboarding_summary(
    owner: str,
    *,
    app_thread_id: UUID | None,
) -> OnboardingSummary:
    if app_thread_id is None:
        return {
            "has_default_profile": False,
            "has_thread_context": False,
            "result_code": None,
            "selected_category_code": None,
            "source": None,
        }

    async with get_session_factory()() as session:
        record = await onboarding_context_repository.get(session, owner, app_thread_id)

    if record is None:
        return {
            "has_default_profile": False,
            "has_thread_context": False,
            "result_code": None,
            "selected_category_code": None,
            "source": None,
        }

    return {
        "has_default_profile": False,
        "has_thread_context": True,
        "result_code": record.result_code,
        "selected_category_code": record.selected_category_code,
        "source": record.source,
    }


async def _build_onboarding_summary(
    owner: str | None,
    *,
    access_token: str | None,
    app_thread_id: UUID | None,
    previous_summary: OnboardingSummary | None,
    refresh_default_profile: bool,
) -> OnboardingSummary | None:
    if owner is None:
        return None

    summary = await _build_thread_onboarding_summary(owner, app_thread_id=app_thread_id)
    summary["has_default_profile"] = (
        previous_summary["has_default_profile"] if previous_summary is not None else False
    )

    if access_token is not None and refresh_default_profile:
        try:
            default_profile = await onboarding_service_client.get_default_profile(access_token)
        except Exception:
            if previous_summary is None and not summary["has_thread_context"]:
                return None
        else:
            summary["has_default_profile"] = default_profile is not None
    elif previous_summary is None and not summary["has_thread_context"]:
        return None

    return summary


def _build_selected_onboarding_summary(
    *,
    raw_result_code: object,
    raw_category_code: object,
) -> OnboardingSummary | None:
    result_code = _normalize_optional_context_string(raw_result_code)
    selected_category_code = _normalize_optional_context_string(raw_category_code)
    if result_code is None:
        return None
    return {
        "has_default_profile": False,
        "has_thread_context": True,
        "result_code": result_code,
        "selected_category_code": selected_category_code,
        "source": "manual_attach",
    }


async def prepare_system_context_state_update(
    current_system_context: SystemContextState | None,
    current_refresh: SystemContextRefreshState | None,
    *,
    config: RunnableConfig,
    context: ChatRuntimeContext | None,
    server_user: BaseUser | None = None,
) -> dict[str, Any]:
    owner = extract_authenticated_user_identity(server_user)
    access_token = extract_authenticated_user_access_token(server_user)
    app_thread_id = extract_app_thread_id(context, config)

    system_context = (
        {
            "selected_documents": list(current_system_context["selected_documents"]),
            "selected_artifacts": list(current_system_context["selected_artifacts"]),
            "selected_market_areas": list(current_system_context.get("selected_market_areas", [])),
            "user_memories": list(current_system_context.get("user_memories", [])),
            "memory_summary": current_system_context["memory_summary"],
            "onboarding_summary": current_system_context["onboarding_summary"],
        }
        if current_system_context is not None
        else empty_system_context_state()
    )
    if current_system_context is not None and "client_surface" in current_system_context:
        system_context["client_surface"] = current_system_context["client_surface"]
    refresh_state = (
        {
            "memory_summary_dirty": current_refresh["memory_summary_dirty"],
            "onboarding_summary_dirty": current_refresh["onboarding_summary_dirty"],
        }
        if current_refresh is not None
        else clean_system_context_refresh_state()
    )

    if _has_runtime_value(config, context, "selected_document_ids"):
        system_context["selected_documents"] = await _build_selected_document_states(
            owner,
            raw_ids=_runtime_context_value(config, context, "selected_document_ids"),
        )
    if _has_runtime_value(config, context, "selected_artifact_ids"):
        system_context["selected_artifacts"] = await _build_selected_artifact_states(
            owner,
            raw_ids=_runtime_context_value(config, context, "selected_artifact_ids"),
        )
    if _has_runtime_value(config, context, "selected_market_dong_codes"):
        system_context["selected_market_areas"] = await _build_selected_market_area_states(
            owner,
            raw_codes=_runtime_context_value(config, context, "selected_market_dong_codes"),
        )

    if _has_runtime_value(config, context, "surface"):
        client_surface = _normalize_client_surface(
            _runtime_context_value(config, context, "surface")
        )
        if client_surface is None:
            system_context.pop("client_surface", None)
        else:
            system_context["client_surface"] = client_surface
    else:
        system_context.pop("client_surface", None)

    if current_system_context is None or refresh_state["memory_summary_dirty"]:
        system_context["memory_summary"] = await _build_memory_summary(owner)
        system_context["user_memories"] = await _build_user_memories(owner)
        refresh_state["memory_summary_dirty"] = False

    # 프론트가 thread onboarding context를 API로 직접 바꿀 수 있으므로,
    # 성향 컨텍스트 포인터는 매 turn 다시 읽고 기본 프로필 여부만 dirty flag로 캐시한다.
    system_context["onboarding_summary"] = await _build_onboarding_summary(
        owner,
        access_token=access_token,
        app_thread_id=app_thread_id,
        previous_summary=current_system_context["onboarding_summary"]
        if current_system_context is not None
        else None,
        refresh_default_profile=(
            current_system_context is None or refresh_state["onboarding_summary_dirty"]
        ),
    )
    refresh_state["onboarding_summary_dirty"] = False

    if _has_runtime_value(config, context, "selected_onboarding_result_code"):
        system_context["onboarding_summary"] = _build_selected_onboarding_summary(
            raw_result_code=_runtime_context_value(
                config, context, "selected_onboarding_result_code"
            ),
            raw_category_code=_runtime_context_value(
                config, context, "selected_onboarding_category_code"
            )
            if _has_runtime_value(config, context, "selected_onboarding_category_code")
            else None,
        )

    return {
        "system_context": system_context,
        "system_context_refresh": refresh_state,
    }
