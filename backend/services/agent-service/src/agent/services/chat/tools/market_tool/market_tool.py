from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx
from langchain_core.tools import tool

from agent.clients.franchise_service import franchise_service_client
from agent.clients.market_service import market_service_client
from agent.services.chat.approvals.schemas import ApprovalDecisionType
from agent.services.chat.tools.tool_spec import ToolSpec

DECISIONS: list[ApprovalDecisionType] = ["approve", "edit", "reject", "respond"]
_MAX_AREAS = 10
_MAX_FRANCHISES = 20

_INDUSTRY_CATEGORIES: tuple[dict[str, Any], ...] = (
    {
        "categoryCode": "CS1",
        "categoryName": "외식",
        "industries": (
            {
                "industryCode": "CS100001",
                "industryName": "한식음식점",
                "aliases": ("한식", "백반", "국밥", "고기집", "식당"),
            },
            {
                "industryCode": "CS100002",
                "industryName": "중식음식점",
                "aliases": ("중식", "중국집", "짜장면", "짬뽕"),
            },
            {
                "industryCode": "CS100003",
                "industryName": "일식음식점",
                "aliases": ("일식", "초밥", "스시", "라멘", "돈카츠"),
            },
            {
                "industryCode": "CS100004",
                "industryName": "양식음식점",
                "aliases": ("양식", "파스타", "스테이크", "레스토랑"),
            },
            {
                "industryCode": "CS100005",
                "industryName": "제과점",
                "aliases": ("베이커리", "빵집", "제빵", "디저트"),
            },
            {
                "industryCode": "CS100006",
                "industryName": "패스트푸드점",
                "aliases": ("패스트푸드", "버거", "햄버거"),
            },
            {
                "industryCode": "CS100007",
                "industryName": "치킨전문점",
                "aliases": ("치킨", "닭강정"),
            },
            {
                "industryCode": "CS100008",
                "industryName": "분식전문점",
                "aliases": ("분식", "김밥", "떡볶이", "라면"),
            },
            {
                "industryCode": "CS100009",
                "industryName": "호프-간이주점",
                "aliases": ("호프", "술집", "주점", "맥주"),
            },
            {
                "industryCode": "CS100010",
                "industryName": "커피-음료",
                "aliases": ("커피", "카페", "음료", "디저트카페", "테이크아웃커피"),
            },
        ),
    },
    {
        "categoryCode": "CS2",
        "categoryName": "서비스",
        "industries": (
            {
                "industryCode": "CS200001",
                "industryName": "일반교습학원",
                "aliases": ("학원", "보습학원", "교습소"),
            },
            {
                "industryCode": "CS200002",
                "industryName": "외국어학원",
                "aliases": ("영어학원", "어학원", "외국어"),
            },
            {
                "industryCode": "CS200003",
                "industryName": "예술학원",
                "aliases": ("미술학원", "음악학원", "예체능학원"),
            },
            {
                "industryCode": "CS200004",
                "industryName": "컴퓨터학원",
                "aliases": ("코딩학원", "컴퓨터교육"),
            },
            {
                "industryCode": "CS200005",
                "industryName": "스포츠 강습",
                "aliases": ("스포츠학원", "운동강습"),
            },
            {
                "industryCode": "CS200006",
                "industryName": "일반의원",
                "aliases": ("의원", "병원", "내과"),
            },
            {"industryCode": "CS200007", "industryName": "치과의원", "aliases": ("치과",)},
            {"industryCode": "CS200008", "industryName": "한의원", "aliases": ("한방",)},
            {
                "industryCode": "CS200009",
                "industryName": "동물병원",
                "aliases": ("반려동물병원", "수의원"),
            },
            {
                "industryCode": "CS200010",
                "industryName": "변호사사무소",
                "aliases": ("변호사", "법률사무소"),
            },
            {"industryCode": "CS200011", "industryName": "변리사사무소", "aliases": ("변리사",)},
            {"industryCode": "CS200012", "industryName": "법무사사무소", "aliases": ("법무사",)},
            {
                "industryCode": "CS200013",
                "industryName": "기타법무서비스",
                "aliases": ("법무서비스",),
            },
            {"industryCode": "CS200014", "industryName": "회계사사무소", "aliases": ("회계사",)},
            {"industryCode": "CS200015", "industryName": "세무사사무소", "aliases": ("세무사",)},
            {"industryCode": "CS200016", "industryName": "당구장", "aliases": ("당구",)},
            {
                "industryCode": "CS200017",
                "industryName": "골프연습장",
                "aliases": ("골프", "스크린골프"),
            },
            {"industryCode": "CS200018", "industryName": "볼링장", "aliases": ("볼링",)},
            {"industryCode": "CS200019", "industryName": "PC방", "aliases": ("피시방", "게임방")},
            {
                "industryCode": "CS200020",
                "industryName": "전자게임장",
                "aliases": ("오락실", "게임장"),
            },
            {"industryCode": "CS200021", "industryName": "기타오락장", "aliases": ("오락장",)},
            {"industryCode": "CS200022", "industryName": "복권방", "aliases": ("로또", "복권")},
            {
                "industryCode": "CS200023",
                "industryName": "통신기기수리",
                "aliases": ("휴대폰수리", "핸드폰수리"),
            },
            {
                "industryCode": "CS200024",
                "industryName": "스포츠클럽",
                "aliases": ("헬스장", "피트니스", "PT"),
            },
            {
                "industryCode": "CS200025",
                "industryName": "자동차수리",
                "aliases": ("카센터", "정비소"),
            },
            {
                "industryCode": "CS200026",
                "industryName": "자동차미용",
                "aliases": ("세차", "디테일링"),
            },
            {
                "industryCode": "CS200027",
                "industryName": "모터사이클수리",
                "aliases": ("오토바이수리",),
            },
            {
                "industryCode": "CS200028",
                "industryName": "미용실",
                "aliases": ("헤어샵", "헤어", "미용"),
            },
            {"industryCode": "CS200029", "industryName": "네일숍", "aliases": ("네일", "네일샵")},
            {
                "industryCode": "CS200030",
                "industryName": "피부관리실",
                "aliases": ("피부관리", "에스테틱"),
            },
            {"industryCode": "CS200031", "industryName": "세탁소", "aliases": ("세탁", "빨래방")},
            {"industryCode": "CS200032", "industryName": "가전제품수리", "aliases": ("가전수리",)},
            {
                "industryCode": "CS200033",
                "industryName": "부동산중개업",
                "aliases": ("부동산", "공인중개사"),
            },
            {"industryCode": "CS200034", "industryName": "여관", "aliases": ("모텔", "숙박")},
            {"industryCode": "CS200035", "industryName": "게스트하우스", "aliases": ("게하",)},
            {"industryCode": "CS200036", "industryName": "고시원", "aliases": ("고시텔",)},
            {
                "industryCode": "CS200037",
                "industryName": "노래방",
                "aliases": ("코인노래방", "노래연습장"),
            },
            {
                "industryCode": "CS200038",
                "industryName": "독서실",
                "aliases": ("스터디카페", "공부방"),
            },
            {"industryCode": "CS200039", "industryName": "DVD방", "aliases": ("디브이디방",)},
            {"industryCode": "CS200040", "industryName": "녹음실", "aliases": ("레코딩",)},
            {
                "industryCode": "CS200041",
                "industryName": "사진관",
                "aliases": ("스튜디오", "증명사진"),
            },
            {
                "industryCode": "CS200042",
                "industryName": "통번역서비스",
                "aliases": ("번역", "통역"),
            },
            {
                "industryCode": "CS200043",
                "industryName": "건축물청소",
                "aliases": ("청소", "청소업체"),
            },
            {"industryCode": "CS200044", "industryName": "여행사", "aliases": ("여행",)},
            {
                "industryCode": "CS200045",
                "industryName": "비디오/서적임대",
                "aliases": ("대여", "서적임대"),
            },
            {
                "industryCode": "CS200046",
                "industryName": "의류임대",
                "aliases": ("옷대여", "드레스대여"),
            },
            {
                "industryCode": "CS200047",
                "industryName": "가정용품임대",
                "aliases": ("렌탈", "생활용품임대"),
            },
        ),
    },
    {
        "categoryCode": "CS3",
        "categoryName": "도소매",
        "industries": (
            {"industryCode": "CS300001", "industryName": "슈퍼마켓", "aliases": ("마트", "슈퍼")},
            {"industryCode": "CS300002", "industryName": "편의점", "aliases": ("편의점", "24시")},
            {
                "industryCode": "CS300003",
                "industryName": "컴퓨터및주변장치판매",
                "aliases": ("컴퓨터판매", "PC판매"),
            },
            {
                "industryCode": "CS300004",
                "industryName": "핸드폰",
                "aliases": ("휴대폰", "휴대폰판매", "핸드폰판매"),
            },
            {"industryCode": "CS300005", "industryName": "주류도매", "aliases": ("주류", "술도매")},
            {
                "industryCode": "CS300006",
                "industryName": "미곡판매",
                "aliases": ("쌀가게", "쌀판매"),
            },
            {
                "industryCode": "CS300007",
                "industryName": "육류판매",
                "aliases": ("정육점", "고기판매"),
            },
            {
                "industryCode": "CS300008",
                "industryName": "수산물판매",
                "aliases": ("생선가게", "수산물"),
            },
            {
                "industryCode": "CS300009",
                "industryName": "청과상",
                "aliases": ("과일가게", "야채가게"),
            },
            {"industryCode": "CS300010", "industryName": "반찬가게", "aliases": ("반찬",)},
            {
                "industryCode": "CS300011",
                "industryName": "일반의류",
                "aliases": ("옷가게", "의류", "패션"),
            },
            {"industryCode": "CS300012", "industryName": "한복점", "aliases": ("한복",)},
            {
                "industryCode": "CS300013",
                "industryName": "유아의류",
                "aliases": ("아동복", "유아복"),
            },
            {"industryCode": "CS300014", "industryName": "신발", "aliases": ("신발가게", "운동화")},
            {"industryCode": "CS300015", "industryName": "가방", "aliases": ("가방가게",)},
            {"industryCode": "CS300016", "industryName": "안경", "aliases": ("안경점", "렌즈")},
            {
                "industryCode": "CS300017",
                "industryName": "시계및귀금속",
                "aliases": ("시계", "귀금속", "주얼리"),
            },
            {"industryCode": "CS300018", "industryName": "의약품", "aliases": ("약국", "약")},
            {"industryCode": "CS300019", "industryName": "의료기기", "aliases": ("의료기구",)},
            {"industryCode": "CS300020", "industryName": "서적", "aliases": ("서점", "책방")},
            {"industryCode": "CS300021", "industryName": "문구", "aliases": ("문구점", "문방구")},
            {"industryCode": "CS300022", "industryName": "화장품", "aliases": ("코스메틱", "뷰티")},
            {"industryCode": "CS300023", "industryName": "미용재료", "aliases": ("미용용품",)},
            {
                "industryCode": "CS300024",
                "industryName": "운동/경기용품",
                "aliases": ("스포츠용품", "운동용품"),
            },
            {
                "industryCode": "CS300025",
                "industryName": "자전거 및 기타운송장비",
                "aliases": ("자전거", "킥보드"),
            },
            {"industryCode": "CS300026", "industryName": "완구", "aliases": ("장난감", "토이")},
            {"industryCode": "CS300027", "industryName": "섬유제품", "aliases": ("원단", "패브릭")},
            {
                "industryCode": "CS300028",
                "industryName": "화초",
                "aliases": ("꽃집", "화원", "플라워"),
            },
            {
                "industryCode": "CS300029",
                "industryName": "애완동물",
                "aliases": ("펫샵", "반려동물"),
            },
            {"industryCode": "CS300030", "industryName": "중고가구", "aliases": ("중고가구점",)},
            {"industryCode": "CS300031", "industryName": "가구", "aliases": ("가구점",)},
            {
                "industryCode": "CS300032",
                "industryName": "가전제품",
                "aliases": ("가전", "전자제품"),
            },
            {"industryCode": "CS300033", "industryName": "철물점", "aliases": ("철물", "공구")},
            {"industryCode": "CS300034", "industryName": "악기", "aliases": ("악기점",)},
            {
                "industryCode": "CS300035",
                "industryName": "인테리어",
                "aliases": ("인테리어소품", "리빙"),
            },
            {"industryCode": "CS300036", "industryName": "조명용품", "aliases": ("조명",)},
            {"industryCode": "CS300037", "industryName": "중고차판매", "aliases": ("중고차",)},
            {"industryCode": "CS300038", "industryName": "자동차부품", "aliases": ("차부품",)},
            {
                "industryCode": "CS300039",
                "industryName": "모터사이클및부품",
                "aliases": ("오토바이부품",),
            },
            {
                "industryCode": "CS300040",
                "industryName": "재생용품 판매점",
                "aliases": ("재활용", "재생용품"),
            },
            {"industryCode": "CS300041", "industryName": "예술품", "aliases": ("갤러리", "아트")},
            {"industryCode": "CS300042", "industryName": "주유소", "aliases": ("주유",)},
            {
                "industryCode": "CS300043",
                "industryName": "전자상거래업",
                "aliases": ("온라인몰", "쇼핑몰", "이커머스"),
            },
        ),
    },
)


def _trim_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _clamp_limit(limit: int) -> int:
    return max(1, min(limit, _MAX_AREAS))


def _clamp_franchise_size(size: int) -> int:
    return max(1, min(size, _MAX_FRANCHISES))


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


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, Decimal):
        return int(value)
    return None


def _trimmed_query(value: str | None) -> str | None:
    normalized = _trim_to_none(value)
    return normalized.lower() if normalized is not None else None


def _matches_industry(industry: dict[str, Any], query: str | None) -> bool:
    if query is None:
        return True
    values = [
        _string_or_none(industry.get("industryCode")),
        _string_or_none(industry.get("industryName")),
        *[alias for alias in industry.get("aliases", ()) if isinstance(alias, str)],
    ]
    return any(query in value.lower() for value in values if value is not None)


def _industry_code_exists(industry_code: str) -> bool:
    return any(
        industry["industryCode"] == industry_code
        for category in _INDUSTRY_CATEGORIES
        for industry in category["industries"]
    )


def _normalize_industry(industry: dict[str, Any]) -> dict[str, Any]:
    return {
        "industryCode": industry["industryCode"],
        "industryName": industry["industryName"],
        "aliases": list(industry.get("aliases", ())),
        "meaning": (
            f"{industry['industryName']} 업종 코드입니다. "
            "market_search_areas의 industryCode 필터, franchise_search_brands의 industryCode로 사용할 수 있습니다."
        ),
    }


def _format_manwon_from_thousand(value: Any) -> dict[str, Any] | None:
    number = _number_or_none(value)
    if number is None:
        return None
    manwon = round(float(number) / 10)
    return {
        "value": manwon,
        "unit": "만원",
        "sourceValue": number,
        "sourceUnit": "천원",
        "text": f"{manwon:,}만원",
    }


def _format_won(value: Any) -> dict[str, Any] | None:
    number = _number_or_none(value)
    if number is None:
        return None
    return {
        "value": number,
        "unit": "원",
        "text": f"{number:,.0f}원",
    }


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
        "nextActions": [
            "지역명은 행정동 이름 일부로 다시 검색합니다. 예: 성수, 을지로, 신당동",
            "사용자가 업종도 함께 말한 경우 market_list_industries로 정확한 industryCode를 확인한 뒤 다시 시도합니다.",
        ],
        "areas": [],
    }


def _tool_error_result(
    *,
    result_type: str,
    message: str,
    next_actions: list[str],
) -> dict[str, Any]:
    return {
        "type": result_type,
        "success": False,
        "error": message,
        "nextActions": next_actions,
    }


def _normalize_period(raw_period: Any) -> dict[str, Any]:
    year = _int_or_none(raw_period.get("year")) if isinstance(raw_period, dict) else None
    quarter = _int_or_none(raw_period.get("quarter")) if isinstance(raw_period, dict) else None
    period_key = (
        _string_or_none(raw_period.get("periodKey")) if isinstance(raw_period, dict) else None
    )
    stdr_yyqu_cd = (
        _string_or_none(raw_period.get("stdrYyquCd")) if isinstance(raw_period, dict) else None
    )
    return {
        "periodKey": period_key,
        "stdrYyquCd": stdr_yyqu_cd,
        "year": year,
        "quarter": quarter,
        "meaning": "상권 데이터 기준 기간입니다.",
        "text": f"{year}년 {quarter}분기"
        if year is not None and quarter is not None
        else (period_key or "latest"),
    }


def _normalize_ranking(raw_item: Any) -> dict[str, Any] | None:
    if not isinstance(raw_item, dict):
        return None
    industry_code = _string_or_none(raw_item.get("industryCode"))
    industry_name = _string_or_none(raw_item.get("industryName"))
    if industry_code is None and industry_name is None:
        return None
    return {
        "rank": _int_or_none(raw_item.get("rank")),
        "industryCode": industry_code,
        "industryName": industry_name,
        "estimatedSalesAmount": _format_won(raw_item.get("estimatedSalesAmount")),
        "salesCount": _number_or_none(raw_item.get("salesCount")),
        "previousPeriodChangeRate": _number_or_none(raw_item.get("previousPeriodChangeRate")),
        "storeCount": _number_or_none(raw_item.get("storeCount")),
        "estimatedSalesPerStore": _format_won(raw_item.get("estimatedSalesPerStore")),
        "meaning": "행정동 안에서 추정매출 기준으로 정렬된 업종입니다.",
    }


def _normalize_store_ranking(raw_item: Any) -> dict[str, Any] | None:
    if not isinstance(raw_item, dict):
        return None
    return {
        "rank": _int_or_none(raw_item.get("rank")),
        "industryCode": _string_or_none(raw_item.get("industryCode")),
        "industryName": _string_or_none(raw_item.get("industryName")),
        "totalStores": _number_or_none(raw_item.get("totalStores")),
        "franchiseStores": _number_or_none(raw_item.get("franchiseStores")),
        "openRate": _number_or_none(raw_item.get("openRate")),
        "openedStores": _number_or_none(raw_item.get("openedStores")),
        "closeRate": _number_or_none(raw_item.get("closeRate")),
        "closedStores": _number_or_none(raw_item.get("closedStores")),
    }


def _normalize_recommended_franchise(raw_item: Any) -> dict[str, Any] | None:
    if not isinstance(raw_item, dict):
        return None
    brand_name = _string_or_none(raw_item.get("brandName"))
    if brand_name is None:
        return None
    return {
        "brandCode": _string_or_none(raw_item.get("brandCode")),
        "brandName": brand_name,
        "companyName": _string_or_none(raw_item.get("companyName")),
        "averageSalesAmount": _format_manwon_from_thousand(raw_item.get("estimatedSalesAmount")),
        "startupCostTotal": _format_manwon_from_thousand(raw_item.get("startupCostTotal")),
        "franchiseCount": _int_or_none(raw_item.get("franchiseCount")),
        "meaning": "상권 매출 1위 업종과 연결된 프랜차이즈 추천 후보입니다.",
    }


def _normalize_franchise_brand(raw_item: Any) -> dict[str, Any] | None:
    if not isinstance(raw_item, dict):
        return None
    brand_name = _string_or_none(raw_item.get("brandName"))
    if brand_name is None:
        return None
    startup_cost = (
        raw_item.get("startupCost") if isinstance(raw_item.get("startupCost"), dict) else {}
    )
    sales = raw_item.get("sales") if isinstance(raw_item.get("sales"), dict) else {}
    return {
        "brandCode": _string_or_none(raw_item.get("brandCode")),
        "brandName": brand_name,
        "companyName": _string_or_none(raw_item.get("companyName")),
        "industryName": _string_or_none(raw_item.get("industryName")),
        "ftcIndustryName": _string_or_none(raw_item.get("ftcIndustryName")),
        "baseYear": _int_or_none(raw_item.get("baseYear")),
        "startupCost": {
            "totalAmount": _format_manwon_from_thousand(startup_cost.get("totalAmount")),
            "franchiseFee": _format_manwon_from_thousand(startup_cost.get("franchiseFee")),
            "educationFee": _format_manwon_from_thousand(startup_cost.get("educationFee")),
            "etcAmount": _format_manwon_from_thousand(startup_cost.get("etcAmount")),
            "deposit": _format_manwon_from_thousand(startup_cost.get("deposit")),
            "meaning": "창업예상비용입니다. 원천 응답은 천원 단위이며, 도구 결과는 만원 단위로 환산합니다.",
        },
        "sales": {
            "averageSalesAmount": _format_manwon_from_thousand(sales.get("averageSalesAmount")),
            "areaUnitAverageSalesAmount": _format_manwon_from_thousand(
                sales.get("areaUnitAverageSalesAmount")
            ),
            "franchiseCount": _int_or_none(sales.get("franchiseCount")),
            "meaning": "가맹점 평균 매출 통계입니다. 원천 응답은 천원 단위이며, 도구 결과는 만원 단위로 환산합니다.",
        },
    }


@tool
async def market_search_areas(
    keyword: str,
    limit: int = 5,
) -> dict[str, Any]:
    """지도에 표시할 서울 행정동 상권 검색 결과를 조회합니다."""

    normalized_keyword = _trim_to_none(keyword)
    if normalized_keyword is None:
        return _error_result("keyword는 필수입니다. 예: 을지로동, 신당동, 왕십리도선동, 성수1가1동")

    try:
        payload = await market_service_client.search_areas(
            keyword=normalized_keyword,
            industry_code=None,
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
    ][: _clamp_limit(limit)]

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


@tool
async def market_list_industries(query: str | None = None) -> dict[str, Any]:
    """상권 업종명과 industryCode 매핑을 내부 코드북에서 조회합니다."""

    normalized_query = _trimmed_query(query)
    categories: list[dict[str, Any]] = []
    for category in _INDUSTRY_CATEGORIES:
        industries = [
            _normalize_industry(industry)
            for industry in category["industries"]
            if _matches_industry(industry, normalized_query)
        ]
        if industries:
            categories.append(
                {
                    "categoryCode": category["categoryCode"],
                    "categoryName": category["categoryName"],
                    "industries": industries,
                }
            )

    return {
        "type": "market_industry_codebook",
        "success": True,
        "query": _trim_to_none(query),
        "summary": (
            "상권분석 업종명과 industryCode 매핑입니다. "
            "사용자가 말한 업종명을 코드로 바꿀 때 사용합니다."
        ),
        "usage": [
            "market_search_areas의 industryCode 필터로 사용할 수 있습니다.",
            "franchise_search_brands의 industryCode로 사용할 수 있습니다.",
            "지역 기반 추천에서는 market_get_dong_report의 industryRankings에 나온 industryCode를 우선 사용합니다.",
        ],
        "categories": categories,
        "matchedCount": sum(len(category["industries"]) for category in categories),
    }


@tool
async def market_get_dong_report(
    dongCode: str,
    period: str = "latest",
) -> dict[str, Any]:
    """행정동 코드로 상권 상세 리포트를 조회하고 한국어 의미를 붙여 반환합니다."""

    dong_code = _trim_to_none(dongCode)
    normalized_period = _trim_to_none(period) or "latest"
    if dong_code is None:
        return _tool_error_result(
            result_type="market_dong_report",
            message="dongCode는 필수입니다.",
            next_actions=[
                "지역명만 알고 있다면 market_search_areas를 먼저 호출하여 정확한 dongCode를 확인합니다.",
                "market_search_areas 결과 areas[*].dongCode 값을 이 도구의 dongCode로 다시 전달합니다.",
            ],
        )

    try:
        payload = await market_service_client.get_dong_report(
            dong_code=dong_code,
            period=normalized_period,
        )
    except httpx.HTTPStatusError as exc:
        return _tool_error_result(
            result_type="market_dong_report",
            message=f"상권 상세 조회가 실패했습니다. status={exc.response.status_code}",
            next_actions=[
                "dongCode가 정확한지 market_search_areas를 호출하여 다시 확인합니다.",
                "정확한 dongCode인데도 실패하면 해당 행정동 또는 기간에 상권 상세 데이터가 없을 수 있습니다.",
                "period를 생략하거나 latest로 다시 호출해 봅니다.",
            ],
        )
    except (httpx.HTTPError, RuntimeError, ValueError):
        return _tool_error_result(
            result_type="market_dong_report",
            message="상권 상세 조회 호출에 실패했습니다.",
            next_actions=[
                "잠시 후 같은 dongCode로 다시 호출합니다.",
                "계속 실패하면 market_search_areas로 다른 행정동 후보를 확인합니다.",
            ],
        )

    dong = payload.get("dong") if isinstance(payload.get("dong"), dict) else {}
    floating_population = (
        payload.get("floatingPopulation")
        if isinstance(payload.get("floatingPopulation"), dict)
        else {}
    )
    resident_population = (
        payload.get("residentPopulation")
        if isinstance(payload.get("residentPopulation"), dict)
        else {}
    )
    sales = payload.get("sales") if isinstance(payload.get("sales"), dict) else {}
    stores = payload.get("stores") if isinstance(payload.get("stores"), dict) else {}
    trade_area_change = (
        payload.get("tradeAreaChange") if isinstance(payload.get("tradeAreaChange"), dict) else {}
    )
    data_quality = (
        payload.get("dataQuality") if isinstance(payload.get("dataQuality"), dict) else {}
    )
    raw_rankings = (
        sales.get("industryRankings") if isinstance(sales.get("industryRankings"), list) else []
    )
    industry_rankings = [
        ranking
        for ranking in (_normalize_ranking(raw_item) for raw_item in raw_rankings)
        if ranking is not None
    ]
    top_industry = industry_rankings[0] if industry_rankings else None
    raw_recommendations = (
        payload.get("franchiseRecommendations")
        if isinstance(payload.get("franchiseRecommendations"), list)
        else []
    )
    low_closure_rankings = (
        stores.get("lowClosureRateTop3")
        if isinstance(stores.get("lowClosureRateTop3"), list)
        else []
    )
    high_closure_rankings = (
        stores.get("highClosureRateTop3")
        if isinstance(stores.get("highClosureRateTop3"), list)
        else []
    )
    high_open_rankings = (
        stores.get("highOpenRateTop3") if isinstance(stores.get("highOpenRateTop3"), list) else []
    )

    return {
        "type": "market_dong_report",
        "success": True,
        "summary": (
            f"{_string_or_none(dong.get('sigunguName')) or ''} "
            f"{_string_or_none(dong.get('dongName')) or dong_code} 상권 상세 리포트입니다."
        ).strip(),
        "dong": {
            "dongCode": _string_or_none(dong.get("dongCode")) or dong_code,
            "dongName": _string_or_none(dong.get("dongName")) or dong_code,
            "sigunguCode": _string_or_none(dong.get("sigunguCode")),
            "sigunguName": _string_or_none(dong.get("sigunguName")),
            "centerLat": _number_or_none(dong.get("centerLat")),
            "centerLng": _number_or_none(dong.get("centerLng")),
            "meaning": "상권 상세 조회 기준 행정동입니다.",
        },
        "period": _normalize_period(payload.get("period")),
        "floatingPopulation": {
            "total": _number_or_none(floating_population.get("total")),
            "peakTimeSlot": _string_or_none(floating_population.get("peakTimeSlot")),
            "peakWeekday": _string_or_none(floating_population.get("peakWeekday")),
            "youngAdultRatio": _number_or_none(floating_population.get("youngAdultRatio")),
            "meaning": "행정동 유동인구 요약입니다.",
        },
        "residentPopulation": {
            "total": _number_or_none(resident_population.get("total")),
            "meaning": "행정동 상주인구 요약입니다.",
        },
        "sales": {
            "totalSalesAmount": _format_won(sales.get("totalSalesAmount")),
            "totalSalesCount": _number_or_none(sales.get("totalSalesCount")),
            "weekdaySalesAmount": _format_won(sales.get("weekdaySalesAmount")),
            "weekendSalesAmount": _format_won(sales.get("weekendSalesAmount")),
            "weekdaySalesRatio": _number_or_none(sales.get("weekdaySalesRatio")),
            "weekendSalesRatio": _number_or_none(sales.get("weekendSalesRatio")),
            "industryRankings": industry_rankings,
            "topIndustryCodeForFranchiseSearch": top_industry["industryCode"]
            if top_industry
            else None,
            "meaning": "추정매출과 업종별 매출 순위입니다. 프랜차이즈 추천에는 industryRankings의 industryCode를 사용할 수 있습니다.",
        },
        "stores": {
            "totalStores": _number_or_none(stores.get("totalStores")),
            "franchiseStores": _number_or_none(stores.get("franchiseStores")),
            "openedStores": _number_or_none(stores.get("openedStores")),
            "closedStores": _number_or_none(stores.get("closedStores")),
            "lowClosureRateTop3": [
                item
                for item in (
                    _normalize_store_ranking(raw_item) for raw_item in low_closure_rankings
                )
                if item is not None
            ],
            "highClosureRateTop3": [
                item
                for item in (
                    _normalize_store_ranking(raw_item) for raw_item in high_closure_rankings
                )
                if item is not None
            ],
            "highOpenRateTop3": [
                item
                for item in (_normalize_store_ranking(raw_item) for raw_item in high_open_rankings)
                if item is not None
            ],
            "meaning": "점포 수, 프랜차이즈 점포 수, 개업·폐업 흐름입니다.",
        },
        "tradeAreaChange": {
            "changeIndex": _string_or_none(trade_area_change.get("changeIndex")),
            "changeIndexName": _string_or_none(trade_area_change.get("changeIndexName")),
            "displayDescription": _string_or_none(trade_area_change.get("displayDescription")),
            "operationMonthsAverage": _number_or_none(
                trade_area_change.get("operationMonthsAverage")
            ),
            "closureMonthsAverage": _number_or_none(trade_area_change.get("closureMonthsAverage")),
            "meaning": "상권 변화 지표입니다.",
        },
        "dataQuality": {
            "availableSections": data_quality.get("availableSections", []),
            "missingSections": data_quality.get("missingSections", []),
            "note": _string_or_none(data_quality.get("note")),
            "meaning": "어떤 섹션의 데이터가 있고 없는지 알려주는 품질 정보입니다.",
        },
        "franchiseRecommendations": [
            item
            for item in (
                _normalize_recommended_franchise(raw_item) for raw_item in raw_recommendations
            )
            if item is not None
        ],
        "nextActions": [
            "특정 업종 프랜차이즈를 더 보려면 sales.industryRankings[*].industryCode로 franchise_search_brands를 호출합니다.",
            "사용자가 말한 업종명이 애매하면 market_list_industries로 정확한 industryCode를 먼저 확인합니다.",
        ],
    }


@tool
async def franchise_search_brands(
    industryCode: str | None = None,
    size: int = 10,
) -> dict[str, Any]:
    """프랜차이즈 브랜드를 업종 코드 기준 또는 전체 기준 평균매출순으로 조회합니다."""

    industry_code = _trim_to_none(industryCode)
    if industry_code is not None and not _industry_code_exists(industry_code):
        return _tool_error_result(
            result_type="franchise_brand_search_results",
            message=f"알 수 없는 industryCode입니다: {industry_code}",
            next_actions=[
                "market_list_industries를 호출하여 정확한 업종 코드와 업종명을 확인한 뒤 다시 호출합니다.",
                "지역 기반 추천이라면 market_get_dong_report의 sales.industryRankings[*].industryCode를 사용합니다.",
                "정확한 업종 코드인데도 계속 실패하면 해당 업종에 프랜차이즈 데이터가 없을 수 있습니다.",
            ],
        )

    safe_size = _clamp_franchise_size(size)
    try:
        payload = await franchise_service_client.get_franchises(
            industry_code=industry_code,
            size=safe_size,
        )
    except httpx.HTTPStatusError as exc:
        return _tool_error_result(
            result_type="franchise_brand_search_results",
            message=f"프랜차이즈 브랜드 조회가 실패했습니다. status={exc.response.status_code}",
            next_actions=[
                "industryCode를 입력했다면 market_list_industries로 정확한 업종 코드를 확인한 후 다시 호출합니다.",
                "정확한 업종 코드임에도 실패하면 해당 업종에 데이터가 없거나 franchise-service가 일시적으로 응답하지 않는 경우일 수 있습니다.",
                "업종 필터 없이 전체 평균매출 상위 브랜드 조회를 시도할 수 있습니다.",
            ],
        )
    except (httpx.HTTPError, RuntimeError, ValueError):
        return _tool_error_result(
            result_type="franchise_brand_search_results",
            message="프랜차이즈 브랜드 조회 호출에 실패했습니다.",
            next_actions=[
                "잠시 후 다시 호출합니다.",
                "industryCode가 필요하다면 market_list_industries 또는 market_get_dong_report로 정확한 코드를 확인합니다.",
            ],
        )

    raw_items = payload.get("items") if isinstance(payload.get("items"), list) else []
    items = [
        item
        for item in (_normalize_franchise_brand(raw_item) for raw_item in raw_items)
        if item is not None
    ]
    return {
        "type": "franchise_brand_search_results",
        "success": True,
        "industryCode": industry_code,
        "size": safe_size,
        "summary": (
            f"{industry_code} 업종의 프랜차이즈 브랜드 평균매출 상위 {len(items)}개입니다."
            if industry_code is not None
            else f"전체 프랜차이즈 브랜드 평균매출 상위 {len(items)}개입니다."
        ),
        "items": items,
        "nextActions": [
            "지역 기반 추천이면 market_get_dong_report의 매출·점포·상권 변화 지표와 함께 해석합니다.",
            "업종이 사용자 의도와 다르면 market_list_industries로 더 정확한 industryCode를 찾아 다시 호출합니다.",
        ],
    }


MARKET_TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        tool=market_search_areas,
        name="market_search_areas",
        description=(
            "지도 화면에서 지역을 찾거나 지도에 표시할 상권 후보가 필요할 때 호출합니다. "
            "keyword에 행정동 이름을 넣으면 해당 지역의 행정동 목록을 반환합니다. 가령 '성수동'이 아닌 '성수1가1동', '성수' 와 같이 입력해야 합니다."
            '예: keyword="성수", keyword="을지로", keyword="신당동". '
            "결과의 areas는 지도 UI가 표시할 행정동 코드·이름·중심좌표입니다."
        ),
        category="rag",
        args_schema=market_search_areas.args_schema,
        default_allowed=True,
        allowed_decisions=DECISIONS,
    ),
    ToolSpec(
        tool=market_list_industries,
        name="market_list_industries",
        description=(
            "상권분석 업종명과 industryCode 매핑이 필요할 때 호출합니다. "
            "외부 API를 호출하지 않고 내부 코드북에서 업종 코드, 업종명, 동의어를 반환합니다. "
            "query에 '카페', '커피', '치킨', '편의점' 같은 자연어 업종명을 넣으면 관련 업종만 좁혀 반환합니다. "
            "반환된 industryCode는 market_search_areas의 업종 필터나 franchise_search_brands의 업종 필터로 사용할 수 있습니다."
        ),
        category="rag",
        args_schema=market_list_industries.args_schema,
        default_allowed=True,
        allowed_decisions=DECISIONS,
    ),
    ToolSpec(
        tool=market_get_dong_report,
        name="market_get_dong_report",
        description=(
            "행정동 코드(dongCode)로 상권 상세 리포트를 조회합니다. "
            "dongCode는 market_search_areas 결과 areas[*].dongCode에서 얻습니다. "
            "지역명만 알고 있으면 먼저 market_search_areas를 호출한 뒤 이 도구를 호출합니다. "
            "결과에는 유동인구, 상주인구, 매출, 업종별 매출 순위, 점포·개폐업, 상권 변화, 추천 프랜차이즈가 한국어 의미와 함께 포함됩니다. "
            "프랜차이즈를 더 조회할 때는 결과의 sales.industryRankings[*].industryCode 또는 topIndustryCodeForFranchiseSearch를 franchise_search_brands에 전달합니다."
        ),
        category="rag",
        args_schema=market_get_dong_report.args_schema,
        default_allowed=True,
        allowed_decisions=DECISIONS,
    ),
    ToolSpec(
        tool=franchise_search_brands,
        name="franchise_search_brands",
        description=(
            "프랜차이즈 브랜드를 평균매출 높은 순으로 조회합니다. "
            "industryCode를 넣으면 해당 상권 업종의 브랜드만 조회하고, 생략하면 전체 브랜드 상위 목록을 조회합니다. "
            "industryCode를 모르면 market_list_industries로 업종명과 코드를 확인하거나, 지역 기반 추천에서는 market_get_dong_report의 업종 순위 코드를 사용합니다. "
            "결과에는 브랜드명, 운영사, 업종, 기준연도, 창업예상비용, 평균매출, 가맹점 수가 한국어 의미와 단위 환산과 함께 포함됩니다."
        ),
        category="rag",
        args_schema=franchise_search_brands.args_schema,
        default_allowed=True,
        allowed_decisions=DECISIONS,
    ),
)
