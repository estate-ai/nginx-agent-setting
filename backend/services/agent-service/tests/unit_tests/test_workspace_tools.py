import pytest

from agent.services.chat.toolkits.chat_toolkit import CHAT_TOOL_SPECS_BY_NAME
from agent.services.chat.approvals.nodes import (
    _handle_chat_tool_error,
    _system_context_refresh_update_for_tool_calls,
)
from agent.services.chat.tools import ChatToolError


def test_workspace_read_tools_are_allowed_by_default() -> None:
    """사용자 데이터를 바꾸지 않는 조회 도구는 승인 없이 실행할 수 있다."""

    for tool_name in (
        "before_research",
        "memory_search",
        "artifact_get",
        "document_search",
        "document_read",
        "web_search",
        "web_fetch",
        "market_search_areas",
        "market_list_industries",
        "market_get_dong_report",
        "franchise_search_brands",
        "onboarding_get_default_profile",
        "onboarding_get_survey_result",
        "onboarding_get_area_recommendations",
        "onboarding_preview_profile_update",
    ):
        assert CHAT_TOOL_SPECS_BY_NAME[tool_name].default_allowed is True


def test_workspace_mutation_tools_are_default_deny() -> None:
    """메모리·문서·아티팩트·성향을 바꾸는 도구는 모두 HITL 기본 거부다."""

    for tool_name in (
        "memory_create",
        "memory_update",
        "memory_delete",
        "artifact_create",
        "artifact_update",
        "artifact_save_as_document",
        "document_create",
        "document_update",
        "document_delete",
        "onboarding_commit_profile_update",
    ):
        spec = CHAT_TOOL_SPECS_BY_NAME[tool_name]
        assert spec.default_allowed is False
        assert spec.allowed_decisions == ["approve", "edit", "reject", "respond"]


def test_before_research_tool_returns_internal_research_guide() -> None:
    """검색 전 도구는 파라미터 없이 긴 리서치 가이드를 반환해야 한다."""

    spec = CHAT_TOOL_SPECS_BY_NAME["before_research"]
    tool = spec.tool

    assert spec.default_allowed is True
    assert tool.args == {}
    assert "상권 분석 리포트" in tool.description
    assert "파라미터 없이 호출" in tool.description
    assert "few-shot" in tool.description

    result = tool.invoke({})

    assert len(result) > 10000
    assert "내부 리서치 가이드" in result
    assert "창업 희망 지역" in result
    assert "총 창업 예산" in result
    assert "직원 수" in result
    assert "목표 월 순수익" in result
    assert "web_search 사용 원칙" in result
    assert "검색 결과가 부족하거나 부정확할 때" in result
    assert "차트 작성 규칙" in result
    assert "few-shot 예시" in result
    assert "성동구 카페 창업 커머셜 리포트" in result
    assert "```chart" in result


def test_system_context_refresh_flags_follow_memory_and_onboarding_mutations() -> None:
    """메모리·온보딩 변경 도구 실행은 해당 summary dirty flag를 올린다."""

    result = _system_context_refresh_update_for_tool_calls(
        {
            "messages": [],
            "system_context_refresh": {
                "memory_summary_dirty": False,
                "onboarding_summary_dirty": False,
            },
        },
        [
            {"id": "tool-1", "name": "memory_create", "args": {}},
            {"id": "tool-2", "name": "onboarding_commit_profile_update", "args": {}},
        ],
    )

    assert result == {
        "memory_summary_dirty": True,
        "onboarding_summary_dirty": True,
    }


def test_chat_tool_error_handler_returns_model_visible_message() -> None:
    """도구가 예외를 내도 graph를 터뜨리지 않고 ToolMessage 본문으로 돌려준다."""

    assert _handle_chat_tool_error(ChatToolError("본문은 비어 있을 수 없습니다.")) == (
        "도구 실행 실패: 본문은 비어 있을 수 없습니다."
    )
    assert "RuntimeError" in _handle_chat_tool_error(RuntimeError("boom"))


def test_workspace_tool_descriptions_explain_chart_block_usage() -> None:
    """생성 도구 설명에는 타입 목록과 chart block 사용법이 포함되어야 한다."""

    artifact_create = CHAT_TOOL_SPECS_BY_NAME["artifact_create"].tool
    document_create = CHAT_TOOL_SPECS_BY_NAME["document_create"].tool

    assert "artifact_type" in artifact_create.description
    assert "commercial_report" in artifact_create.description
    assert "```chart" in artifact_create.description
    assert "document_type" in document_create.description
    assert "research_report" in document_create.description
    assert "```chart" in document_create.description


def test_workspace_create_tool_args_keep_existing_contract_keys() -> None:
    """차트 설명 보강과 무관하게 생성 도구 입력 계약은 기존 키 이름을 유지해야 한다."""

    artifact_args = CHAT_TOOL_SPECS_BY_NAME["artifact_create"].tool.args
    document_args = CHAT_TOOL_SPECS_BY_NAME["document_create"].tool.args

    assert "artifact_type" in artifact_args
    assert "type" not in artifact_args
    assert "document_type" in document_args
    assert "type" not in document_args


def test_web_tool_descriptions_explain_visibility_and_result_shape() -> None:
    """웹 도구 설명에는 공개 웹 제한과 반환 결과 윤곽이 드러나야 한다."""

    web_search = CHAT_TOOL_SPECS_BY_NAME["web_search"].tool
    web_fetch = CHAT_TOOL_SPECS_BY_NAME["web_fetch"].tool

    assert "제목" in web_search.description
    assert "limit" in web_search.description
    assert "기본 format은 text" in web_fetch.description
    assert "localhost" in web_fetch.description


@pytest.mark.asyncio
async def test_market_search_tool_returns_map_area_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """지도 검색 도구는 market-service 응답을 지도 캐시용 결과로 정규화한다."""

    from agent.services.chat.tools.market_tool import market_tool as module

    class FakeMarketClient:
        async def search_areas(
            self,
            *,
            keyword: str | None,
            industry_code: str | None,
        ) -> dict[str, object]:
            assert keyword == "성수"
            assert industry_code is None
            return {
                "keyword": keyword,
                "industryCode": None,
                "industryName": None,
                "areas": [
                    {
                        "centerLat": 37.544,
                        "centerLng": 127.055,
                        "dongCode": "11200690",
                        "dongName": "성수2가3동",
                        "sigunguCode": "11200",
                        "sigunguName": "성동구",
                        "industryCode": None,
                        "industryName": None,
                        "rank": 1,
                        "estimatedSalesAmount": 123456,
                    }
                ],
            }

    monkeypatch.setattr(module, "market_service_client", FakeMarketClient())

    result = await module.market_search_areas.ainvoke(
        {
            "keyword": "성수",
            "limit": 1,
        }
    )

    assert result["type"] == "map_area_search_results"
    assert result["success"] is True
    assert result["keyword"] == "성수"
    assert result["industryCode"] is None
    assert result["areas"][0]["dongCode"] == "11200690"


@pytest.mark.asyncio
async def test_market_search_tool_with_empty_keyword_returns_silent_error() -> None:
    """키워드가 빈 문자열이면 예외 대신 실패 결과를 반환한다."""

    from agent.services.chat.tools.market_tool import market_tool as module

    result = await module.market_search_areas.ainvoke({"keyword": "   "})

    assert result["type"] == "map_area_search_results"
    assert result["success"] is False
    assert result["areas"] == []


@pytest.mark.asyncio
async def test_market_list_industries_filters_by_korean_alias() -> None:
    """업종 코드북 도구는 자연어 업종명을 industryCode 후보로 바꿔준다."""

    from agent.services.chat.tools.market_tool import market_tool as module

    result = await module.market_list_industries.ainvoke({"query": "카페"})

    assert result["type"] == "market_industry_codebook"
    assert result["success"] is True
    assert result["matchedCount"] >= 1
    first_category = result["categories"][0]
    assert first_category["categoryName"] == "외식"
    assert first_category["industries"][0]["industryCode"] == "CS100010"
    assert "franchise_search_brands" in result["usage"][1]


@pytest.mark.asyncio
async def test_market_get_dong_report_returns_korean_meaning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """상권 상세 도구는 원본 리포트를 한국어 의미가 붙은 구조로 정리한다."""

    from agent.services.chat.tools.market_tool import market_tool as module

    class FakeMarketClient:
        async def get_dong_report(self, *, dong_code: str, period: str) -> dict[str, object]:
            assert dong_code == "11200650"
            assert period == "latest"
            return {
                "dong": {
                    "dongCode": "11200650",
                    "dongName": "성수1가1동",
                    "sigunguName": "성동구",
                },
                "period": {"periodKey": "20261", "year": 2026, "quarter": 1},
                "floatingPopulation": {
                    "total": 1000,
                    "peakTimeSlot": "17-21",
                    "youngAdultRatio": 42.5,
                },
                "residentPopulation": {"total": 500},
                "sales": {
                    "totalSalesAmount": 1000000,
                    "industryRankings": [
                        {
                            "rank": 1,
                            "industryCode": "CS100010",
                            "industryName": "커피-음료",
                            "estimatedSalesAmount": 900000,
                        }
                    ],
                },
                "stores": {"totalStores": 12, "franchiseStores": 3},
                "tradeAreaChange": {
                    "changeIndex": "LL",
                    "changeIndexName": "다이나믹",
                    "displayDescription": "변화 가능성이 큰 상권입니다.",
                },
                "dataQuality": {
                    "availableSections": ["sales"],
                    "missingSections": [],
                    "note": "테스트",
                },
                "franchiseRecommendations": [
                    {
                        "brandCode": "brand-1",
                        "brandName": "예시카페",
                        "estimatedSalesAmount": 12340,
                        "startupCostTotal": 5600,
                    }
                ],
            }

    monkeypatch.setattr(module, "market_service_client", FakeMarketClient())

    result = await module.market_get_dong_report.ainvoke({"dongCode": "11200650"})

    assert result["type"] == "market_dong_report"
    assert result["success"] is True
    assert result["dong"]["dongName"] == "성수1가1동"
    assert result["period"]["text"] == "2026년 1분기"
    assert result["sales"]["topIndustryCodeForFranchiseSearch"] == "CS100010"
    assert "프랜차이즈" in result["nextActions"][0]


@pytest.mark.asyncio
async def test_franchise_search_brands_returns_normalized_units(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """프랜차이즈 도구는 천원 단위 원천값을 만원 의미 구조로 변환한다."""

    from agent.services.chat.tools.market_tool import market_tool as module

    class FakeFranchiseClient:
        async def get_franchises(
            self,
            *,
            industry_code: str | None,
            size: int,
        ) -> dict[str, object]:
            assert industry_code == "CS100010"
            assert size == 2
            return {
                "items": [
                    {
                        "brandCode": "brand-1",
                        "brandName": "예시카페",
                        "companyName": "예시컴퍼니",
                        "industryName": "커피-음료",
                        "ftcIndustryName": "커피",
                        "baseYear": 2025,
                        "startupCost": {
                            "totalAmount": 10000,
                            "franchiseFee": 1000,
                            "educationFee": 500,
                            "etcAmount": 8000,
                            "deposit": 500,
                        },
                        "sales": {
                            "averageSalesAmount": 20000,
                            "areaUnitAverageSalesAmount": 300,
                            "franchiseCount": 7,
                        },
                    }
                ]
            }

    monkeypatch.setattr(module, "franchise_service_client", FakeFranchiseClient())

    result = await module.franchise_search_brands.ainvoke({"industryCode": "CS100010", "size": 2})

    assert result["type"] == "franchise_brand_search_results"
    assert result["success"] is True
    assert result["items"][0]["startupCost"]["totalAmount"]["text"] == "1,000만원"
    assert result["items"][0]["sales"]["averageSalesAmount"]["text"] == "2,000만원"


@pytest.mark.asyncio
async def test_franchise_search_brands_guides_invalid_industry_code() -> None:
    """잘못된 업종 코드는 예외 대신 코드북 확인 안내를 반환한다."""

    from agent.services.chat.tools.market_tool import market_tool as module

    result = await module.franchise_search_brands.ainvoke({"industryCode": "WRONG", "size": 2})

    assert result["type"] == "franchise_brand_search_results"
    assert result["success"] is False
    assert "market_list_industries" in result["nextActions"][0]
