from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserTowerPredictionCacheRecord, UserTowerProfileRecord


class UserTowerProfileRepository:
    async def get_by_auth_user_uuid(
        self,
        session: AsyncSession,
        auth_user_uuid: str,
    ) -> UserTowerProfileRecord | None:
        result = await session.execute(
            select(UserTowerProfileRecord).where(UserTowerProfileRecord.auth_user_uuid == auth_user_uuid)
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        session: AsyncSession,
        auth_user_uuid: str,
        profile_code: str,
        schema_version: int,
        source: str,
        raw_answers: dict[str, Any] | None,
        user_profile: dict[str, Any],
        survey_definition_id: int | None = None,
        survey_response_id: int | None = None,
        survey_slug: str | None = None,
        survey_version: int | None = None,
        survey_code: str | None = None,
        scoring_version: str | None = None,
    ) -> UserTowerProfileRecord:
        record = await self.get_by_auth_user_uuid(session, auth_user_uuid)
        if record is None:
            record = UserTowerProfileRecord(
                auth_user_uuid=auth_user_uuid,
                profile_code=profile_code,
                schema_version=schema_version,
                source=source,
                survey_definition_id=survey_definition_id,
                survey_response_id=survey_response_id,
                survey_slug=survey_slug,
                survey_version=survey_version,
                survey_code=survey_code,
                scoring_version=scoring_version,
                raw_answers=raw_answers,
                **user_profile,
            )
            session.add(record)
        else:
            record.profile_code = profile_code
            record.schema_version = schema_version
            record.source = source
            record.survey_definition_id = survey_definition_id
            record.survey_response_id = survey_response_id
            record.survey_slug = survey_slug
            record.survey_version = survey_version
            record.survey_code = survey_code
            record.scoring_version = scoring_version
            record.raw_answers = raw_answers
            for field_name, value in user_profile.items():
                setattr(record, field_name, value)
        await session.flush()
        return record


class UserTowerPredictionCacheRepository:
    async def get(
        self,
        session: AsyncSession,
        profile_code: str,
        model_signature: str,
        top_k: int,
    ) -> UserTowerPredictionCacheRecord | None:
        result = await session.execute(
            select(UserTowerPredictionCacheRecord).where(
                UserTowerPredictionCacheRecord.profile_code == profile_code,
                UserTowerPredictionCacheRecord.model_signature == model_signature,
                UserTowerPredictionCacheRecord.top_k == top_k,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        session: AsyncSession,
        profile_code: str,
        model_signature: str,
        top_k: int,
        prediction_json: dict[str, Any],
    ) -> UserTowerPredictionCacheRecord:
        record = await self.get(session, profile_code, model_signature, top_k)
        if record is None:
            record = UserTowerPredictionCacheRecord(
                profile_code=profile_code,
                model_signature=model_signature,
                top_k=top_k,
                prediction_json=prediction_json,
            )
            session.add(record)
        else:
            record.prediction_json = prediction_json
        await session.flush()
        return record
