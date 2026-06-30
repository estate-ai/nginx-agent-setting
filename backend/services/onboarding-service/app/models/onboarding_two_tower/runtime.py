from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.models.onboarding_two_tower.user_profiles import (
    USER_CONTROL_SPECS,
    category_options,
    load_user_profiles,
)
from app.models.onboarding_two_tower.predict import predict_with_runtime
from app.models.onboarding_two_tower.train import load_model, resolve_data_mode, train_and_save
from app.models.item_catalog.features import build_item_features
from app.two_tower.contracts import UserProfilePayload

_RUNTIME_MODEL: Any | None = None
_RUNTIME_METADATA: dict[str, Any] | None = None


def _runtime_data_mode(metadata: dict[str, Any]) -> str:
    return resolve_data_mode(settings.category_data_mode, metadata)


def _sample_profiles(data_mode: str) -> list[dict[str, Any]]:
    users = load_user_profiles(data_mode=data_mode).to_dict(orient="records")
    return [UserProfilePayload(**user).model_dump() for user in users]


def get_runtime() -> tuple[Any, dict[str, Any]]:
    global _RUNTIME_MODEL, _RUNTIME_METADATA
    # 학습 후 첫 요청부터는 같은 프로세스 안에서 모델과 metadata를 재사용한다.
    if _RUNTIME_MODEL is None or _RUNTIME_METADATA is None:
        _RUNTIME_MODEL, _RUNTIME_METADATA = load_model(data_mode=settings.category_data_mode)
    return _RUNTIME_MODEL, _RUNTIME_METADATA


def train_runtime(epochs: int, data_mode: str | None = None) -> dict[str, Any]:
    global _RUNTIME_MODEL, _RUNTIME_METADATA
    metadata = train_and_save(epochs=epochs, data_mode=data_mode)
    _RUNTIME_MODEL, _RUNTIME_METADATA = load_model(data_mode=metadata.get("data_mode"))
    return metadata


def evaluation_payload() -> dict[str, Any]:
    _, metadata = get_runtime()
    return metadata


def catalog_payload() -> dict[str, Any]:
    _, metadata = get_runtime()
    data_mode = _runtime_data_mode(metadata)
    items = build_item_features(data_mode=data_mode).copy()
    item_preview = (
        items.sort_values(["sales_amount", "subway_commercial_trend_score"], ascending=[False, False])
        .head(8)[
            [
                "item_id",
                "area_name",
                "service_category_name",
                "area_profile_type",
                "sales_amount",
                "weekend_sales_ratio",
                "evening_sales_ratio",
            ]
        ]
        .to_dict(orient="records")
    )
    return {
        "model_id": metadata["model_id"],
        "feature_controls": USER_CONTROL_SPECS,
        "category_options": category_options(data_mode=data_mode),
        "sample_profiles": _sample_profiles(data_mode=data_mode),
        "item_preview": item_preview,
        "evaluation": metadata,
    }


def predict_payload(user_profile: dict[str, Any], top_k: int) -> dict[str, Any]:
    model, metadata = get_runtime()
    data_mode = _runtime_data_mode(metadata)
    return predict_with_runtime(
        model=model,
        metadata=metadata,
        user_profile=user_profile,
        top_k=top_k,
        data_mode=data_mode,
    )
