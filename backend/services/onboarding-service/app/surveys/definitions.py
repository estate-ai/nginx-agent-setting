from __future__ import annotations

from typing import Any

ACTIVE_SURVEY_SLUG = "founder-fit-10-final"
ACTIVE_SURVEY_VERSION = 1
ACTIVE_SURVEY_CODE = "A"
ACTIVE_SCORING_VERSION = "founder_fit_v1"

_ACTIVE_SURVEY_DEFINITION: dict[str, Any] = {
    "slug": ACTIVE_SURVEY_SLUG,
    "version": ACTIVE_SURVEY_VERSION,
    "survey_code": ACTIVE_SURVEY_CODE,
    "scoring_version": ACTIVE_SCORING_VERSION,
    "title": "창업 성향 설문 10문항 최종",
    "description": "비회원도 바로 응답하고 base36 추천 코드를 받을 수 있는 현재 활성 설문 정의다.",
    "questions": [
        {
            "id": "q1",
            "selection_type": "single",
            "prompt": "내 가게에 가장 자주 왔으면 하는 손님은 어떤 분인가요?",
            "options": [
                {
                    "code": "A",
                    "label": "집 근처라 자주 오는 동네 주민",
                    "effects": {
                        "resident_focus_level": 1.0,
                        "worker_focus_level": 0.1,
                        "subway_dependency_level": 0.2,
                        "weekend_preference_level": 0.4,
                    },
                },
                {
                    "code": "B",
                    "label": "점심이나 퇴근길에 들르는 직장인",
                    "effects": {
                        "resident_focus_level": 0.1,
                        "worker_focus_level": 1.0,
                        "subway_dependency_level": 0.6,
                        "weekend_preference_level": 0.2,
                    },
                },
                {
                    "code": "C",
                    "label": "일부러 찾아오는 목적형 손님",
                    "effects": {
                        "resident_focus_level": 0.2,
                        "worker_focus_level": 0.2,
                        "subway_dependency_level": 0.8,
                        "weekend_preference_level": 0.5,
                    },
                },
                {
                    "code": "D",
                    "label": "주말에 가족이나 연인과 오는 손님",
                    "effects": {
                        "resident_focus_level": 0.4,
                        "worker_focus_level": 0.1,
                        "subway_dependency_level": 0.3,
                        "weekend_preference_level": 1.0,
                    },
                },
            ],
            "primary_parameters": ["resident_focus_level", "worker_focus_level"],
            "secondary_parameters": ["subway_dependency_level", "weekend_preference_level"],
        },
        {
            "id": "q2",
            "selection_type": "single",
            "prompt": "가게가 가장 바빴으면 하는 시간대는 언제인가요?",
            "options": [
                {
                    "code": "A",
                    "label": "평일 점심",
                    "effects": {
                        "weekend_preference_level": 0.1,
                        "evening_preference_level": 0.1,
                        "worker_focus_level": 0.9,
                    },
                },
                {
                    "code": "B",
                    "label": "평일 저녁",
                    "effects": {
                        "weekend_preference_level": 0.2,
                        "evening_preference_level": 1.0,
                        "worker_focus_level": 0.5,
                    },
                },
                {
                    "code": "C",
                    "label": "주말 낮",
                    "effects": {
                        "weekend_preference_level": 0.85,
                        "evening_preference_level": 0.2,
                        "worker_focus_level": 0.1,
                    },
                },
                {
                    "code": "D",
                    "label": "주말 저녁",
                    "effects": {
                        "weekend_preference_level": 1.0,
                        "evening_preference_level": 0.8,
                        "worker_focus_level": 0.2,
                    },
                },
            ],
            "primary_parameters": ["weekend_preference_level", "evening_preference_level"],
            "secondary_parameters": ["worker_focus_level"],
        },
        {
            "id": "q3",
            "selection_type": "single",
            "prompt": "자리 고를 때 지하철역과의 거리는 얼마나 중요하다고 느끼시나요?",
            "options": [
                {
                    "code": "A",
                    "label": "역이 가까워야 거의 안심이 된다",
                    "effects": {
                        "subway_dependency_level": 1.0,
                        "resident_focus_level": 0.1,
                    },
                },
                {
                    "code": "B",
                    "label": "가까우면 좋지만 절대 조건은 아니다",
                    "effects": {
                        "subway_dependency_level": 0.7,
                        "resident_focus_level": 0.3,
                    },
                },
                {
                    "code": "C",
                    "label": "크게 신경 쓰지 않는다",
                    "effects": {
                        "subway_dependency_level": 0.3,
                        "resident_focus_level": 0.6,
                    },
                },
                {
                    "code": "D",
                    "label": "골목이나 생활권 안쪽도 괜찮다",
                    "effects": {
                        "subway_dependency_level": 0.0,
                        "resident_focus_level": 0.8,
                    },
                },
            ],
            "primary_parameters": ["subway_dependency_level"],
            "secondary_parameters": ["resident_focus_level"],
        },
        {
            "id": "q4",
            "selection_type": "single",
            "prompt": "창업 초기에 가장 중요하게 생각하는 것은 무엇인가요?",
            "options": [
                {
                    "code": "A",
                    "label": "초기 투자금을 최대한 낮게 시작하는 것",
                    "effects": {
                        "budget_level": 0.1,
                        "stability_level": 0.6,
                        "rent_sensitivity_level": 0.9,
                    },
                },
                {
                    "code": "B",
                    "label": "투자금이 들더라도 좋은 자리를 잡는 것",
                    "effects": {
                        "budget_level": 1.0,
                        "stability_level": 0.35,
                        "rent_sensitivity_level": 0.2,
                    },
                },
                {
                    "code": "C",
                    "label": "초반 수익이 늦어도 버틸 여유를 남기는 것",
                    "effects": {
                        "budget_level": 0.45,
                        "stability_level": 0.9,
                        "rent_sensitivity_level": 0.6,
                    },
                },
                {
                    "code": "D",
                    "label": "빠르게 매출을 만들고 회수하는 것",
                    "effects": {
                        "budget_level": 0.8,
                        "stability_level": 0.2,
                        "rent_sensitivity_level": 0.3,
                    },
                },
            ],
            "primary_parameters": ["budget_level", "stability_level"],
            "secondary_parameters": ["rent_sensitivity_level"],
        },
        {
            "id": "q5",
            "selection_type": "single",
            "prompt": "같은 돈을 쓴다면 어디에 더 쓰고 싶으신가요?",
            "options": [
                {
                    "code": "A",
                    "label": "월세와 보증금 부담을 낮추는 데",
                    "effects": {
                        "rent_sensitivity_level": 1.0,
                        "budget_level": 0.2,
                        "stability_level": 0.6,
                    },
                },
                {
                    "code": "B",
                    "label": "월세가 높아도 더 좋은 위치를 잡는 데",
                    "effects": {
                        "rent_sensitivity_level": 0.1,
                        "budget_level": 0.85,
                        "stability_level": 0.3,
                    },
                },
                {
                    "code": "C",
                    "label": "운영자금까지 남겨두는 데",
                    "effects": {
                        "rent_sensitivity_level": 0.7,
                        "budget_level": 0.45,
                        "stability_level": 0.9,
                    },
                },
                {
                    "code": "D",
                    "label": "초반 홍보와 빠른 자리 잡기에",
                    "effects": {
                        "rent_sensitivity_level": 0.2,
                        "budget_level": 0.7,
                        "stability_level": 0.25,
                    },
                },
            ],
            "primary_parameters": ["rent_sensitivity_level", "budget_level"],
            "secondary_parameters": ["stability_level"],
        },
        {
            "id": "q6",
            "selection_type": "single",
            "prompt": "창업 후 1~2년 동안 어떤 흐름이 더 마음 편할 것 같나요?",
            "options": [
                {
                    "code": "A",
                    "label": "크게 안 벌어도 꾸준히 유지되는 흐름",
                    "effects": {
                        "stability_level": 1.0,
                        "competition_tolerance_level": 0.2,
                    },
                },
                {
                    "code": "B",
                    "label": "변동이 있어도 성장 가능성이 큰 흐름",
                    "effects": {
                        "stability_level": 0.3,
                        "competition_tolerance_level": 0.8,
                    },
                },
                {
                    "code": "C",
                    "label": "위험은 적지만 확장성도 크지 않은 흐름",
                    "effects": {
                        "stability_level": 0.85,
                        "competition_tolerance_level": 0.25,
                    },
                },
                {
                    "code": "D",
                    "label": "리스크가 있더라도 빨리 커질 수 있는 흐름",
                    "effects": {
                        "stability_level": 0.1,
                        "competition_tolerance_level": 1.0,
                    },
                },
            ],
            "primary_parameters": ["stability_level"],
            "secondary_parameters": ["competition_tolerance_level"],
        },
        {
            "id": "q7",
            "selection_type": "single",
            "prompt": "경쟁이 많은 상권을 보면 어떤 생각이 드나요?",
            "options": [
                {
                    "code": "A",
                    "label": "이미 수요가 검증된 곳이라 오히려 괜찮다",
                    "effects": {
                        "competition_tolerance_level": 0.8,
                        "stability_level": 0.4,
                    },
                },
                {
                    "code": "B",
                    "label": "굳이 그 안에서 싸우고 싶지는 않다",
                    "effects": {
                        "competition_tolerance_level": 0.1,
                        "stability_level": 0.8,
                    },
                },
                {
                    "code": "C",
                    "label": "내가 더 잘할 수 있다면 들어갈 수 있다",
                    "effects": {
                        "competition_tolerance_level": 1.0,
                        "stability_level": 0.3,
                    },
                },
                {
                    "code": "D",
                    "label": "상황을 조금 더 지켜본 뒤 판단하고 싶다",
                    "effects": {
                        "competition_tolerance_level": 0.4,
                        "stability_level": 0.7,
                    },
                },
            ],
            "primary_parameters": ["competition_tolerance_level"],
            "secondary_parameters": ["stability_level"],
        },
        {
            "id": "q8",
            "selection_type": "single",
            "prompt": "내가 생각하는 좋은 상권은 어떤 모습에 더 가깝나요?",
            "options": [
                {
                    "code": "A",
                    "label": "아파트와 빌라가 많아 생활 수요가 보이는 곳",
                    "effects": {
                        "resident_focus_level": 1.0,
                        "worker_focus_level": 0.1,
                        "subway_dependency_level": 0.2,
                        "stability_level": 0.7,
                    },
                },
                {
                    "code": "B",
                    "label": "오피스 건물이 많아 점심과 퇴근 수요가 보이는 곳",
                    "effects": {
                        "resident_focus_level": 0.1,
                        "worker_focus_level": 1.0,
                        "subway_dependency_level": 0.6,
                        "stability_level": 0.6,
                    },
                },
                {
                    "code": "C",
                    "label": "역세권이라 유동인구가 계속 흐르는 곳",
                    "effects": {
                        "resident_focus_level": 0.3,
                        "worker_focus_level": 0.4,
                        "subway_dependency_level": 1.0,
                        "stability_level": 0.4,
                    },
                },
                {
                    "code": "D",
                    "label": "너무 한쪽으로 치우치지 않은 혼합형 상권",
                    "effects": {
                        "resident_focus_level": 0.6,
                        "worker_focus_level": 0.6,
                        "subway_dependency_level": 0.5,
                        "stability_level": 0.8,
                    },
                },
            ],
            "primary_parameters": ["resident_focus_level", "worker_focus_level", "subway_dependency_level"],
            "secondary_parameters": ["stability_level"],
        },
        {
            "id": "q9",
            "selection_type": "single",
            "prompt": "장사가 안 되는 날, 어떤 상황이 가장 불안할 것 같나요?",
            "options": [
                {
                    "code": "A",
                    "label": "평일 점심에 직장인 손님이 안 오는 것",
                    "effects": {
                        "evening_preference_level": 0.1,
                        "weekend_preference_level": 0.1,
                        "worker_focus_level": 0.9,
                        "stability_level": 0.7,
                    },
                },
                {
                    "code": "B",
                    "label": "저녁 시간인데 가게가 한산한 것",
                    "effects": {
                        "evening_preference_level": 1.0,
                        "weekend_preference_level": 0.2,
                        "worker_focus_level": 0.3,
                        "stability_level": 0.5,
                    },
                },
                {
                    "code": "C",
                    "label": "주말인데 생각보다 조용한 것",
                    "effects": {
                        "evening_preference_level": 0.3,
                        "weekend_preference_level": 1.0,
                        "worker_focus_level": 0.1,
                        "stability_level": 0.5,
                    },
                },
                {
                    "code": "D",
                    "label": "며칠 연속으로 전체 흐름이 꺾이는 것",
                    "effects": {
                        "evening_preference_level": 0.5,
                        "weekend_preference_level": 0.5,
                        "worker_focus_level": 0.2,
                        "stability_level": 1.0,
                    },
                },
            ],
            "primary_parameters": ["evening_preference_level", "weekend_preference_level"],
            "secondary_parameters": ["worker_focus_level", "stability_level"],
        },
        {
            "id": "q10",
            "selection_type": "multi",
            "max_selections": 3,
            "prompt": "자영업을 통해 이루고 싶은 것을 골라주세요.",
            "options": [
                {
                    "code": "A",
                    "label": "안정적인 생활 기반",
                    "effects": {
                        "stability_level": 1.0,
                        "competition_tolerance_level": 0.2,
                        "resident_focus_level": 0.6,
                        "budget_level": 0.4,
                    },
                },
                {
                    "code": "B",
                    "label": "높은 수익과 확장 가능성",
                    "effects": {
                        "stability_level": 0.2,
                        "competition_tolerance_level": 1.0,
                        "resident_focus_level": 0.2,
                        "budget_level": 0.9,
                    },
                },
                {
                    "code": "C",
                    "label": "자유로운 시간과 운영 방식",
                    "effects": {
                        "stability_level": 0.6,
                        "competition_tolerance_level": 0.3,
                        "resident_focus_level": 0.4,
                        "budget_level": 0.3,
                    },
                },
                {
                    "code": "D",
                    "label": "동네에서 오래 인정받는 가게",
                    "effects": {
                        "stability_level": 0.8,
                        "competition_tolerance_level": 0.3,
                        "resident_focus_level": 1.0,
                        "budget_level": 0.3,
                    },
                },
                {
                    "code": "E",
                    "label": "내 감각이 드러나는 브랜드",
                    "effects": {
                        "stability_level": 0.4,
                        "competition_tolerance_level": 0.7,
                        "resident_focus_level": 0.2,
                        "budget_level": 0.6,
                    },
                },
            ],
            "primary_parameters": ["stability_level", "competition_tolerance_level"],
            "secondary_parameters": ["resident_focus_level", "budget_level"],
        },
    ],
}


def active_survey_definition() -> dict[str, Any]:
    return {
        **_ACTIVE_SURVEY_DEFINITION,
        "questions": [
            question.copy()
            | {
                "options": [
                    option.copy() | {"effects": dict(option.get("effects", {}))}
                    for option in question["options"]
                ]
            }
            for question in _ACTIVE_SURVEY_DEFINITION["questions"]
        ],
    }
