from __future__ import annotations

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SurveyDefinitionRecord, SurveyResponseRecord


class SurveyDefinitionRepository:
    async def get_active(self, session: AsyncSession) -> SurveyDefinitionRecord | None:
        result = await session.execute(
            select(SurveyDefinitionRecord).where(SurveyDefinitionRecord.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_by_survey_code(self, session: AsyncSession, survey_code: str) -> SurveyDefinitionRecord | None:
        result = await session.execute(
            select(SurveyDefinitionRecord).where(SurveyDefinitionRecord.survey_code == survey_code)
        )
        return result.scalar_one_or_none()

    async def upsert_active_definition(
        self,
        session: AsyncSession,
        *,
        slug: str,
        version: int,
        survey_code: str,
        scoring_version: str,
        title: str,
        description: str,
        question_count: int,
        definition_json: dict,
    ) -> SurveyDefinitionRecord:
        result = await session.execute(
            select(SurveyDefinitionRecord).where(
                SurveyDefinitionRecord.slug == slug,
                SurveyDefinitionRecord.version == version,
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            record = SurveyDefinitionRecord(
                slug=slug,
                version=version,
                survey_code=survey_code,
                scoring_version=scoring_version,
                title=title,
                description=description,
                question_count=question_count,
                is_active=True,
                definition_json=definition_json,
            )
            session.add(record)
        else:
            record.survey_code = survey_code
            record.scoring_version = scoring_version
            record.title = title
            record.description = description
            record.question_count = question_count
            record.is_active = True
            record.definition_json = definition_json

        await session.flush()
        await session.execute(
            update(SurveyDefinitionRecord)
            .where(SurveyDefinitionRecord.id != record.id)
            .values(is_active=False)
        )
        await session.flush()
        return record


class SurveyResponseRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        survey_definition_id: int,
        survey_slug: str,
        survey_version: int,
        survey_code: str,
        scoring_version: str,
        source: str,
        profile_code: str,
        profile_schema_version: int,
        profile_name: str,
        preferred_category_code: str,
        answers_json: dict,
        scored_profile_json: dict,
    ) -> SurveyResponseRecord:
        record = SurveyResponseRecord(
            survey_definition_id=survey_definition_id,
            survey_slug=survey_slug,
            survey_version=survey_version,
            survey_code=survey_code,
            scoring_version=scoring_version,
            source=source,
            profile_code=profile_code,
            profile_schema_version=profile_schema_version,
            profile_name=profile_name,
            preferred_category_code=preferred_category_code,
            answers_json=answers_json,
            scored_profile_json=scored_profile_json,
        )
        session.add(record)
        await session.flush()
        return record

    async def get_by_id(self, session: AsyncSession, response_id: int) -> SurveyResponseRecord | None:
        result = await session.execute(
            select(SurveyResponseRecord).where(SurveyResponseRecord.id == response_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_by_profile_code(
        self,
        session: AsyncSession,
        profile_code: str,
    ) -> SurveyResponseRecord | None:
        result = await session.execute(
            select(SurveyResponseRecord)
            .where(SurveyResponseRecord.profile_code == profile_code)
            .order_by(desc(SurveyResponseRecord.created_at), desc(SurveyResponseRecord.id))
        )
        return result.scalars().first()
