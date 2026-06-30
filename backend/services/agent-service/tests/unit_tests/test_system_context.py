import pytest
from langchain_core.messages import AIMessage, HumanMessage

from agent.services.chat.system_context import (
    append_system_context_to_latest_human_message,
    build_system_context,
)
from agent.services.chat.system_context_state import (
    parse_selected_dong_codes,
    parse_selected_ids,
)


def test_parse_selected_ids_rejects_invalid_values() -> None:
    """선택 ID가 제공되면 잘못된 UUID를 조용히 건너뛰지 않는다."""

    valid_id = "0a40bf78-783a-4a53-a94e-b6f2134df5e1"

    with pytest.raises(ValueError, match="not a UUID"):
        parse_selected_ids([valid_id, "not-a-uuid"])


def test_parse_selected_ids_accepts_valid_uuid_list() -> None:
    """유효한 UUID 문자열 목록은 UUID list로 변환한다."""

    valid_id = "0a40bf78-783a-4a53-a94e-b6f2134df5e1"

    result = parse_selected_ids([valid_id])

    assert [str(item) for item in result] == [valid_id]


def test_parse_selected_dong_codes_rejects_invalid_values() -> None:
    """선택 상권 동 코드는 문자열 목록만 허용한다."""

    with pytest.raises(ValueError, match="must not be empty"):
        parse_selected_dong_codes(["11230820", ""])


def test_parse_selected_dong_codes_deduplicates_values() -> None:
    """선택 상권 동 코드는 입력 순서를 유지하며 중복을 제거한다."""

    result = parse_selected_dong_codes(["11230820", "11230820", "11230830"])

    assert result == ["11230820", "11230830"]


def test_build_system_context_renders_document_metadata_only() -> None:
    result = build_system_context(
        {
            "selected_documents": [
                {
                    "id": "doc-1",
                    "type": "commercial_report",
                    "title": "강남 상권 분석",
                    "summary": "핵심 지표 요약",
                }
            ],
            "selected_artifacts": [],
            "memory_summary": None,
            "onboarding_summary": None,
        }
    )

    assert result is not None
    assert "<system_context>" in result
    assert "<selected_documents>" in result
    assert "doc-1" in result
    assert "강남 상권 분석" in result
    assert "핵심 지표 요약" in result
    assert "document_read" in result
    assert "raw_text" not in result


def test_build_system_context_always_renders_current_datetime() -> None:
    """선택 컨텍스트가 없어도 현재 날짜와 몇시인지 system_context에 포함된다."""

    result = build_system_context(None)

    assert result is not None
    assert "<current_datetime" in result
    assert 'hour="' in result
    assert 'timezone="Asia/Seoul"' in result
    assert 'utc_iso="' not in result


def test_build_system_context_renders_map_surface_instruction() -> None:
    """지도 화면에서 들어온 run에는 지도 도구 호출 지시를 포함한다."""

    result = build_system_context(
        {
            "selected_documents": [],
            "selected_artifacts": [],
            "memory_summary": None,
            "onboarding_summary": None,
            "client_surface": "map",
        }
    )

    assert result is not None
    assert '<client_surface name="map">' in result
    assert "market_search_areas" in result
    assert "before_research 호출을 지양" in result


def test_build_system_context_renders_artifact_metadata_only() -> None:
    result = build_system_context(
        {
            "selected_documents": [],
            "selected_artifacts": [
                {
                    "id": "artifact-1",
                    "type": "research_report",
                    "title": "조사 초안",
                    "summary": "초안 요약",
                    "version": 3,
                }
            ],
            "memory_summary": None,
            "onboarding_summary": None,
        }
    )

    assert result is not None
    assert "<selected_artifacts>" in result
    assert "artifact-1" in result
    assert 'version="3"' in result
    assert "artifact_get" in result
    assert "raw_text" not in result


def test_build_system_context_renders_memory_and_onboarding_summaries() -> None:
    result = build_system_context(
        {
            "selected_documents": [],
            "selected_artifacts": [],
            "memory_summary": {"has_memories": True, "memory_count": 3},
            "onboarding_summary": {
                "has_default_profile": False,
                "has_thread_context": True,
                "result_code": "result-1",
                "selected_category_code": "cafe",
                "source": "manual_attach",
            },
        }
    )

    assert result is not None
    assert "<memory_summary" in result
    assert 'memory_count="3"' in result
    assert "<onboarding_summary" in result
    assert 'has_thread_context="true"' in result
    assert 'result_code="result-1"' in result
    assert 'selected_category_code="cafe"' in result
    assert "onboarding_get_survey_result" in result
    assert "onboarding_get_area_recommendations" in result


def test_build_system_context_renders_market_areas_and_user_memories() -> None:
    """선택 상권과 사용자 메모리는 system_context에 함께 렌더링된다."""

    result = build_system_context(
        {
            "selected_documents": [],
            "selected_artifacts": [],
            "selected_market_areas": [
                {
                    "dong_code": "11230820",
                    "dong_name": "역삼1동",
                }
            ],
            "user_memories": [
                {
                    "id": "memory-1",
                    "content": "주말 유동인구가 많은 상권을 선호한다.",
                    "source": "manual",
                }
            ],
            "memory_summary": {"has_memories": True, "memory_count": 1},
            "onboarding_summary": None,
        }
    )

    assert result is not None
    assert "<selected_market_areas>" in result
    assert 'dong_code="11230820"' in result
    assert 'dong_name="역삼1동"' in result
    assert "market_get_dong_report" in result
    assert "<user_memories>" in result
    assert "주말 유동인구가 많은 상권을 선호한다." in result


def test_append_system_context_to_latest_human_message_only_updates_human_message() -> None:
    messages = [
        HumanMessage(content="첫 질문"),
        AIMessage(content="중간 응답"),
        HumanMessage(content="최신 질문"),
    ]

    updated = append_system_context_to_latest_human_message(
        messages,
        "<system_context>\nselected\n</system_context>",
    )

    assert updated[0].content == "첫 질문"
    assert updated[1].content == "중간 응답"
    assert isinstance(updated[2].content, str)
    assert "<system_context>" in updated[2].content
