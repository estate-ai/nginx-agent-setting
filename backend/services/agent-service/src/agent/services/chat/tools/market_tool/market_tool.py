from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx
from langchain_core.tools import tool

from agent.clients.market_service import market_service_client
from agent.services.chat.approvals.schemas import ApprovalDecisionType
from agent.services.chat.tools.tool_spec import ToolSpec

DECISIONS: list[ApprovalDecisionType] = ["approve", "edit", "reject", "respond"]
_MAX_AREAS = 10


def _trim_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _clamp_limit(limit: int) -> int:
    return max(1, min(limit, _MAX_AREAS))


def _string_or_none(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _number_or_none(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return value
    if isinstance(value, Decimal):
        return float(value)
    return None


def _normalize_area(raw_area: Any) -> dict[str, Any] | None:
    if not isinstance(raw_area, dict):
        return None

    dong_code = _string_or_none(raw_area.get("dongCode"))
    center_lat = _number_or_none(raw_area.get("centerLat"))
    center_lng = _number_or_none(raw_area.get("centerLng"))
    if dong_code is None or center_lat is None or center_lng is None:
        return None

    return {
        "centerLat": center_lat,
        "centerLng": center_lng,
        "dongCode": dong_code,
        "dongName": _string_or_none(raw_area.get("dongName")) or dong_code,
        "estimatedSalesAmount": _number_or_none(raw_area.get("estimatedSalesAmount")),
        "industryCode": _string_or_none(raw_area.get("industryCode")),
        "industryName": _string_or_none(raw_area.get("industryName")),
        "rank": _number_or_none(raw_area.get("rank")),
        "sigunguCode": _string_or_none(raw_area.get("sigunguCode")) or "",
        "sigunguName": _string_or_none(raw_area.get("sigunguName")) or "",
    }


def _error_result(message: str) -> dict[str, Any]:
    return {
        "type": "map_area_search_results",
        "success": False,
        "error": message,
        "areas": [],
    }


@tool
async def market_search_areas(
    keyword: str | None = None,
    industry_code: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """지도에 표시할 서울 행정동 상권 검색 결과를 조회합니다."""

    normalized_keyword = _trim_to_none(keyword)
    normalized_industry_code = _trim_to_none(industry_code)
    if normalized_keyword is None and normalized_industry_code is None:
        return _error_result("keyword 또는 industry_code 중 하나 이상이 필요합니다.")

    try:
        payload = await market_service_client.search_areas(
            keyword=normalized_keyword,
            industry_code=normalized_industry_code,
        )
    except httpx.HTTPStatusError as exc:
        return _error_result(
            f"market-service 검색 호출이 실패했습니다. status={exc.response.status_code}"
        )
    except (httpx.HTTPError, RuntimeError, ValueError):
        return _error_result("market-service 검색 호출에 실패했습니다.")

    raw_areas = payload.get("areas")
    raw_area_items = raw_areas if isinstance(raw_areas, list) else []
    areas = [
        area
        for area in (_normalize_area(raw_area) for raw_area in raw_area_items)
        if area is not None
    ][:_clamp_limit(limit)]

    return {
        "type": "map_area_search_results",
        "success": True,
        "keyword": _string_or_none(payload.get("keyword")),
        "industryCode": _string_or_none(payload.get("industryCode")),
        "industryName": _string_or_none(payload.get("industryName")),
        "periodKey": _string_or_none(payload.get("periodKey")),
        "stdrYyquCd": _string_or_none(payload.get("stdrYyquCd")),
        "areas": areas,
    }


MARKET_TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        tool=market_search_areas,
        name="market_search_areas",
        description=(
            "지도 화면에서 지역을 찾거나 지도에 표시할 상권 후보가 필요할 때 호출합니다. "
            "keyword는 구/행정동/상권명 검색어이고, industry_code는 상권 업종 코드입니다. "
            "결과는 지도 UI가 사용할 행정동 코드, 이름, 중심좌표, 업종 매출 정보를 반환합니다."
        ),
        category="rag",
        args_schema=market_search_areas.args_schema,
        default_allowed=True,
        allowed_decisions=DECISIONS,
    ),
)
