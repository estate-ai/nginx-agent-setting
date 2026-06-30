from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import settings
from app.models.category_profile.features import (
    build_category_profiles,
    category_options as category_profile_options,
)

SERVICE_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_USER_PROFILES = SERVICE_ROOT / ".sample" / "user_tower_profiles.sample.jsonl"
USER_TOWER_FEATURE_SCALE = "zero_to_one_v1"

USER_NUMERIC_FIELDS = [
    "budget_level",
    "stability_level",
    "subway_dependency_level",
    "weekend_preference_level",
    "evening_preference_level",
    "resident_focus_level",
    "worker_focus_level",
    "rent_sensitivity_level",
    "competition_tolerance_level",
]

USER_CONTROL_SPECS = [
    {
        "name": "budget_level",
        "label": "예산 허용치",
        "description": "0에 가까울수록 저비용 창업, 1에 가까울수록 고비용 업종까지 허용한다.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
    },
    {
        "name": "stability_level",
        "label": "안정성 선호",
        "description": "0은 성장형, 1은 안정형에 가깝다.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
    },
    {
        "name": "subway_dependency_level",
        "label": "지하철 의존도",
        "description": "높을수록 역세권 유입 신호를 강하게 반영한다.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
    },
    {
        "name": "weekend_preference_level",
        "label": "주말 매출 선호",
        "description": "높을수록 주말 비중이 큰 상권을 선호한다.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
    },
    {
        "name": "evening_preference_level",
        "label": "저녁 운영 선호",
        "description": "높을수록 저녁 매출 비중이 큰 후보를 선호한다.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
    },
    {
        "name": "resident_focus_level",
        "label": "거주민 집중도",
        "description": "높을수록 생활밀착형 거주 수요를 중시한다.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
    },
    {
        "name": "worker_focus_level",
        "label": "직장인 집중도",
        "description": "높을수록 오피스 수요가 강한 후보를 선호한다.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
    },
    {
        "name": "rent_sensitivity_level",
        "label": "임대료 민감도",
        "description": "높을수록 높은 비용 후보에 더 큰 페널티를 준다.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
    },
    {
        "name": "competition_tolerance_level",
        "label": "경쟁 허용도",
        "description": "높을수록 경쟁이 있는 상권도 감수한다.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
    },
]


def _resolve_data_mode(data_mode: str | None = None) -> str:
    normalized = str(data_mode or settings.category_data_mode).strip().lower()
    if normalized in {"sample", "raw"}:
        return normalized
    raise ValueError("data_mode must be 'sample' or 'raw'")


@lru_cache(maxsize=None)
def _category_option_rows(data_mode: str, trainable_only: bool) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (
            str(option["code"]),
            str(option["label"]),
            str(option.get("group", "unknown")),
        )
        for option in category_profile_options(data_mode=data_mode, trainable_only=trainable_only)
    )


def category_options(data_mode: str | None = None, trainable_only: bool = True) -> list[dict[str, str]]:
    resolved_data_mode = _resolve_data_mode(data_mode)
    return [
        {"code": code, "label": label, "group": group}
        for code, label, group in _category_option_rows(resolved_data_mode, trainable_only)
    ]


def category_label_by_code(data_mode: str | None = None, trainable_only: bool = True) -> dict[str, str]:
    return {
        option["code"]: option["label"]
        for option in category_options(data_mode=data_mode, trainable_only=trainable_only)
    }


def __getattr__(name: str) -> Any:
    if name == "CATEGORY_OPTIONS":
        return category_options()
    if name == "CATEGORY_LABEL_BY_CODE":
        return category_label_by_code()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _unit_interval(value: Any) -> float:
    return max(0.0, min(1.0, float(value)))


def _budget_level_from_startup_cost(startup_cost: Any) -> float:
    normalized = (float(startup_cost) - 50.0) / 270.0
    return round(_unit_interval(normalized + 0.08), 2)


def build_user_profile_from_category(category_row: pd.Series) -> dict[str, Any]:
    return {
        "user_id": f"category_area_{str(category_row['service_category_code']).lower()}",
        "profile_name": f"{category_row['service_category_name']} 상권 탐색 프로필",
        "preferred_category_code": str(category_row["service_category_code"]),
        "budget_level": _budget_level_from_startup_cost(category_row["startup_cost_million_krw_proxy"]),
        "stability_level": round(_unit_interval(category_row["stability_prior_score"]), 2),
        "subway_dependency_level": round(_unit_interval(category_row["sales_count_score"]), 2),
        "weekend_preference_level": round(_unit_interval(category_row["weekend_sales_ratio"]), 2),
        "evening_preference_level": round(_unit_interval(category_row["evening_sales_ratio"]), 2),
        "resident_focus_level": 0.5,
        "worker_focus_level": 0.5,
        "rent_sensitivity_level": round(1.0 - _budget_level_from_startup_cost(category_row["startup_cost_million_krw_proxy"]), 2),
        "competition_tolerance_level": round(_unit_interval(category_row["competition_pressure_score"]), 2),
    }


@lru_cache(maxsize=None)
def _generated_user_profile_rows(data_mode: str) -> tuple[str, ...]:
    categories = build_category_profiles(data_mode=data_mode, trainable_only=True)
    rows = [
        build_user_profile_from_category(category)
        for _, category in categories.iterrows()
    ]
    return tuple(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)


def generate_user_profiles(data_mode: str | None = None) -> list[dict[str, Any]]:
    resolved_data_mode = _resolve_data_mode(data_mode)
    return [
        json.loads(row)
        for row in _generated_user_profile_rows(resolved_data_mode)
    ]


def ensure_sample_user_profiles(path: Path = SAMPLE_USER_PROFILES) -> Path:
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, ensure_ascii=False) for row in generate_user_profiles(data_mode="sample"))
    path.write_text(payload + "\n", encoding="utf-8")
    return path


def load_user_profiles(path: Path | None = None, data_mode: str | None = None) -> pd.DataFrame:
    if path is None:
        return pd.DataFrame(generate_user_profiles(data_mode=data_mode))

    source = ensure_sample_user_profiles(path)
    rows: list[dict[str, Any]] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return pd.DataFrame(rows)


def budget_limit_from_score(score: float) -> float:
    anchors = [
        (0.0, 50.0),
        (0.25, 100.0),
        (0.5, 150.0),
        (0.75, 220.0),
        (1.0, 320.0),
    ]
    normalized_score = max(0.0, min(1.0, round(float(score), 2)))
    for index, (left_score, left_value) in enumerate(anchors[:-1]):
        right_score, right_value = anchors[index + 1]
        if normalized_score <= right_score:
            if right_score == left_score:
                return left_value
            ratio = (normalized_score - left_score) / (right_score - left_score)
            return left_value + ((right_value - left_value) * ratio)
    return anchors[-1][1]


def score_user_item(user: pd.Series, item: pd.Series) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if str(user["preferred_category_code"]) == str(item["service_category_code"]):
        score += 3.0
        reasons.append("preferred_category_match")

    budget_limit = budget_limit_from_score(float(user["budget_level"]))
    startup_cost = float(item["startup_cost_million_krw_proxy"])
    if startup_cost <= budget_limit:
        score += 1.8
        reasons.append("budget_fit")
    else:
        score -= 2.4
        reasons.append("budget_over")

    subway_weight = float(user["subway_dependency_level"])
    score += 1.8 * subway_weight * float(item["subway_commercial_trend_score"])
    if subway_weight >= 0.8:
        reasons.append("subway_match")

    weekend_weight = float(user["weekend_preference_level"])
    evening_weight = float(user["evening_preference_level"])
    score += 1.0 * weekend_weight * float(item["weekend_sales_ratio"])
    score += 1.2 * evening_weight * float(item["evening_sales_ratio"])

    resident_total = float(item["resident_population"])
    worker_total = float(item["worker_population"])
    population_total = max(resident_total + worker_total, 1.0)
    resident_share = resident_total / population_total
    worker_share = worker_total / population_total

    score += float(user["resident_focus_level"]) * 1.1 * resident_share
    score += float(user["worker_focus_level"]) * 1.1 * worker_share

    stability_weight = float(user["stability_level"])
    growth_weight = 1.0 - stability_weight
    score += 1.0 * stability_weight * (1.0 - float(item["sales_momentum_down_probability"]))
    score -= 0.8 * stability_weight * float(item["demand_gap_score"])
    score += 1.2 * growth_weight * float(item["sales_momentum_up_probability"])
    score += 0.7 * growth_weight * float(item["category_opportunity_score"])

    rent_weight = float(user["rent_sensitivity_level"])
    apartment_penalty = float(item["apartment_average_price_normalized"])
    score -= 0.8 * rent_weight * apartment_penalty
    if rent_weight >= 0.8 and startup_cost > budget_limit * 0.85:
        score -= 1.1
        reasons.append("rent_pressure")

    competition_weight = float(user["competition_tolerance_level"])
    score += 0.5 * competition_weight * float(item["category_opportunity_score"])
    score -= 0.4 * (1.0 - competition_weight) * float(item["demand_gap_score"])

    area_profile_type = str(item["area_profile_type"])
    if worker_share >= resident_share and float(user["worker_focus_level"]) >= 0.75 and area_profile_type == "office":
        score += 0.5
        reasons.append("office_profile_match")
    if resident_share > worker_share and float(user["resident_focus_level"]) >= 0.75 and area_profile_type == "residential":
        score += 0.5
        reasons.append("residential_profile_match")

    return score, reasons


def build_user_item_labels(users: pd.DataFrame, items: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, user in users.iterrows():
        scored: list[dict[str, Any]] = []
        for _, item in items.iterrows():
            score, reasons = score_user_item(user, item)
            scored.append(
                {
                    "user_id": user["user_id"],
                    "profile_name": user["profile_name"],
                    "item_id": item["item_id"],
                    "area_code": item["area_code"],
                    "area_name": item["area_name"],
                    "service_category_code": item["service_category_code"],
                    "service_category_name": item["service_category_name"],
                    "match_score": round(float(score), 6),
                    "reasons": "|".join(reasons),
                }
            )
        scored_frame = pd.DataFrame(scored).sort_values("match_score", ascending=False).reset_index(drop=True)
        scored_frame["label"] = 0
        valid_positive = ~scored_frame["reasons"].str.contains("budget_over", regex=False)
        positive_index = scored_frame[valid_positive].head(3).index
        scored_frame.loc[positive_index, "label"] = 1
        rows.extend(scored_frame.to_dict("records"))
    return pd.DataFrame(rows)
