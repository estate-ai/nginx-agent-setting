from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserTowerProfileRecord(Base):
    __tablename__ = "user_tower_profiles"
    __table_args__ = (
        UniqueConstraint("auth_user_uuid", name="uq_user_tower_profiles_auth_user_uuid"),
        Index("ix_user_tower_profiles_profile_code", "profile_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    auth_user_uuid: Mapped[str] = mapped_column(String(64), nullable=False)
    profile_code: Mapped[str] = mapped_column(String(32), nullable=False)
    schema_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    survey_definition_id: Mapped[int | None] = mapped_column(
        ForeignKey("survey_definitions.id"),
        nullable=True,
    )
    survey_response_id: Mapped[int | None] = mapped_column(
        ForeignKey("survey_responses.id"),
        nullable=True,
    )
    survey_slug: Mapped[str | None] = mapped_column(String(64), nullable=True)
    survey_version: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    survey_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    scoring_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    profile_name: Mapped[str] = mapped_column(String(128), nullable=False)
    preferred_category_code: Mapped[str] = mapped_column(String(32), nullable=False)
    budget_level: Mapped[float] = mapped_column(Float, nullable=False)
    stability_level: Mapped[float] = mapped_column(Float, nullable=False)
    subway_dependency_level: Mapped[float] = mapped_column(Float, nullable=False)
    weekend_preference_level: Mapped[float] = mapped_column(Float, nullable=False)
    evening_preference_level: Mapped[float] = mapped_column(Float, nullable=False)
    resident_focus_level: Mapped[float] = mapped_column(Float, nullable=False)
    worker_focus_level: Mapped[float] = mapped_column(Float, nullable=False)
    rent_sensitivity_level: Mapped[float] = mapped_column(Float, nullable=False)
    competition_tolerance_level: Mapped[float] = mapped_column(Float, nullable=False)
    raw_answers: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        onupdate=_utc_now,
    )


class SurveyDefinitionRecord(Base):
    __tablename__ = "survey_definitions"
    __table_args__ = (
        UniqueConstraint("slug", "version", name="uq_survey_definitions_slug_version"),
        UniqueConstraint("survey_code", name="uq_survey_definitions_survey_code"),
        Index("ix_survey_definitions_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    survey_code: Mapped[str] = mapped_column(String(8), nullable=False)
    scoring_version: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    question_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    definition_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        onupdate=_utc_now,
    )


class SurveyResponseRecord(Base):
    __tablename__ = "survey_responses"
    __table_args__ = (
        Index("ix_survey_responses_profile_code", "profile_code"),
        Index("ix_survey_responses_survey_code", "survey_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    survey_definition_id: Mapped[int] = mapped_column(ForeignKey("survey_definitions.id"), nullable=False)
    survey_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    survey_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    survey_code: Mapped[str] = mapped_column(String(8), nullable=False)
    scoring_version: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="guest")
    profile_code: Mapped[str] = mapped_column(String(32), nullable=False)
    profile_schema_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    profile_name: Mapped[str] = mapped_column(String(128), nullable=False)
    preferred_category_code: Mapped[str] = mapped_column(String(32), nullable=False)
    answers_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    scored_profile_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        onupdate=_utc_now,
    )


class UserTowerPredictionCacheRecord(Base):
    __tablename__ = "user_tower_prediction_cache"
    __table_args__ = (
        UniqueConstraint(
            "profile_code",
            "model_signature",
            "top_k",
            name="uq_user_tower_prediction_cache_lookup",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_code: Mapped[str] = mapped_column(String(32), nullable=False)
    model_signature: Mapped[str] = mapped_column(String(128), nullable=False)
    top_k: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    prediction_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        onupdate=_utc_now,
    )
