from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_auth_user, get_db_session
from app.core.config import settings
from app.core.jwt_auth import AuthUserContext
from app.models.onboarding_two_tower.runtime import evaluation_payload, train_runtime
from app.surveys.contracts import (
    SaveSurveyResultRequest,
    SurveyDefinitionResponse,
    SurveyPreviewRequest,
    SurveyResultEnvelope,
)
from app.surveys.service import (
    get_active_survey_definition,
    get_saved_survey_result,
    preview_survey_result,
    resolve_survey_result_by_code,
    save_survey_result_for_user,
)
from app.two_tower.contracts import (
    CatalogResponse,
    EvaluationResponse,
    PredictRequest,
    PredictResponse,
    ResolvedProfileResponse,
    SaveUserTowerProfileRequest,
    TrainRequest,
)
from app.two_tower.service import (
    get_catalog_response,
    get_saved_profile_response,
    resolve_prediction_response,
    resolve_shared_profile_response,
    upsert_saved_profile_response,
)

router = APIRouter()
public_router = APIRouter()
legacy_router = APIRouter()
admin_router = APIRouter()


def _ensure_same_auth_user(requested_auth_user_uuid: str, auth_user: AuthUserContext) -> None:
    if requested_auth_user_uuid != auth_user.auth_user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 저장 프로필에는 접근할 수 없다.",
        )


@public_router.get(
    "/health",
    tags=["system"],
    summary="서비스 상태 조회",
    description="현재 로드된 온보딩 투타워 모델의 기본 상태를 반환한다.",
)
async def health() -> dict[str, Any]:
    evaluation = await run_in_threadpool(evaluation_payload)
    return {
        "ok": True,
        "service": settings.service_name,
        "version": settings.service_version,
        "model_id": settings.model_id,
        "trained_at": evaluation["trained_at"],
        "item_count": evaluation["item_count"],
    }


@public_router.get(
    "/surveys/active",
    response_model=SurveyDefinitionResponse,
    tags=["survey"],
    summary="현재 활성 설문 정의 조회",
    description="프론트 설문 페이지가 렌더링할 문항, 선택지, 점수화 버전 정보를 반환한다.",
)
async def get_active_survey(
    session: AsyncSession = Depends(get_db_session),
) -> SurveyDefinitionResponse:
    return await get_active_survey_definition(session)


@public_router.post(
    "/surveys/active/preview",
    response_model=SurveyResultEnvelope,
    tags=["survey"],
    summary="설문 응답 미리보기",
    description="비회원도 설문 응답을 보내면 유저 타워 점수, base36 공유 코드, 추천 결과를 바로 받을 수 있다.",
)
async def preview_active_survey(
    request: SurveyPreviewRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SurveyResultEnvelope:
    return await preview_survey_result(session, request)


@public_router.get(
    "/surveys/results/{profile_code}",
    response_model=SurveyResultEnvelope,
    tags=["survey"],
    summary="설문 공유 코드 결과 조회",
    description="survey_code가 포함된 base36 공유 코드만으로 설문 메타데이터와 추천 결과를 복원한다.",
)
async def get_survey_result_by_code(
    profile_code: str,
    top_k: int = Query(default=5, ge=1, le=10, description="함께 조회할 추천 개수"),
    session: AsyncSession = Depends(get_db_session),
) -> SurveyResultEnvelope:
    return await resolve_survey_result_by_code(
        session=session,
        profile_code=profile_code,
        top_k=top_k,
    )


@public_router.put(
    "/surveys/me/profile",
    response_model=SurveyResultEnvelope,
    tags=["survey"],
    summary="내 설문 결과 저장 또는 수정",
    description="JWT의 user_profile.uuid를 기준으로 현재 설문 공유 코드를 최신 저장 상태로 반영한다.",
)
async def put_my_survey_profile(
    request: SaveSurveyResultRequest,
    auth_user: AuthUserContext = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_db_session),
) -> SurveyResultEnvelope:
    return await save_survey_result_for_user(
        session=session,
        auth_user_uuid=auth_user.auth_user_uuid,
        request=request,
    )


@public_router.get(
    "/surveys/me/profile",
    response_model=SurveyResultEnvelope,
    tags=["survey"],
    summary="내 저장 설문 결과 조회",
    description="JWT의 user_profile.uuid에 연결된 최신 설문 결과와 추천 결과를 조회한다.",
)
async def get_my_survey_profile(
    top_k: int = Query(default=5, ge=1, le=10, description="함께 조회할 추천 개수"),
    auth_user: AuthUserContext = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_db_session),
) -> SurveyResultEnvelope:
    return await get_saved_survey_result(
        session=session,
        auth_user_uuid=auth_user.auth_user_uuid,
        top_k=top_k,
    )


@legacy_router.get(
    "/two-tower/catalog",
    response_model=CatalogResponse,
    tags=["two-tower"],
    summary="투타워 카탈로그 조회",
    description="내부 예제 화면에서만 사용하는 유저 컨트롤, 샘플 프로필, 아이템 미리보기를 반환한다.",
)
async def two_tower_catalog() -> CatalogResponse:
    return await get_catalog_response()


@legacy_router.post(
    "/two-tower/predict",
    response_model=PredictResponse,
    tags=["two-tower"],
    summary="투타워 추천 계산",
    description="내부 예제 화면에서만 사용하는 직접 점수 조정 기반 추천 계산 경로다.",
)
async def predict_two_tower(
    request: PredictRequest,
    session: AsyncSession = Depends(get_db_session),
) -> PredictResponse:
    return await resolve_prediction_response(
        session=session,
        user_profile=request.user_profile.model_dump(),
        top_k=request.top_k,
    )


@legacy_router.get(
    "/two-tower/profiles/users/{auth_user_uuid}",
    response_model=ResolvedProfileResponse,
    tags=["two-tower"],
    summary="사용자 저장 프로필 조회",
    description="내부 레거시 경로다. JWT의 user_profile.uuid와 같은 사용자만 자신의 저장 프로필을 조회할 수 있다.",
)
async def get_two_tower_profile_by_user(
    auth_user_uuid: str,
    top_k: int = Query(default=5, ge=1, le=10, description="함께 조회할 추천 개수"),
    auth_user: AuthUserContext = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_db_session),
) -> ResolvedProfileResponse:
    _ensure_same_auth_user(auth_user_uuid, auth_user)
    return await get_saved_profile_response(
        session=session,
        auth_user_uuid=auth_user_uuid,
        top_k=top_k,
    )


@legacy_router.put(
    "/two-tower/profiles/users/{auth_user_uuid}",
    response_model=ResolvedProfileResponse,
    tags=["two-tower"],
    summary="사용자 유저 타워 저장 또는 수정",
    description="내부 레거시 경로다. JWT의 user_profile.uuid와 같은 사용자만 자신의 점수를 저장할 수 있다.",
)
async def put_two_tower_profile_by_user(
    auth_user_uuid: str,
    request: SaveUserTowerProfileRequest,
    auth_user: AuthUserContext = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_db_session),
) -> ResolvedProfileResponse:
    _ensure_same_auth_user(auth_user_uuid, auth_user)
    return await upsert_saved_profile_response(
        session=session,
        auth_user_uuid=auth_user_uuid,
        request=request,
    )


@legacy_router.get(
    "/two-tower/profiles/code/{profile_code}",
    response_model=ResolvedProfileResponse,
    tags=["two-tower"],
    summary="공유 코드 기반 프로필 조회",
    description="내부 예제 화면에서만 사용하는 레거시 공유 코드 복원 경로다.",
)
async def get_two_tower_profile_by_code(
    profile_code: str,
    top_k: int = Query(default=5, ge=1, le=10, description="함께 조회할 추천 개수"),
    session: AsyncSession = Depends(get_db_session),
) -> ResolvedProfileResponse:
    return await resolve_shared_profile_response(
        session=session,
        profile_code=profile_code,
        top_k=top_k,
    )


@admin_router.get(
    "/two-tower/evaluation",
    response_model=EvaluationResponse,
    tags=["two-tower"],
    summary="투타워 학습 지표 조회",
    description="내부 운영 검증에서만 사용하는 학습 지표 조회 경로다.",
)
async def two_tower_evaluation() -> EvaluationResponse:
    return EvaluationResponse.model_validate(await run_in_threadpool(evaluation_payload))


@admin_router.post(
    "/two-tower/train",
    response_model=EvaluationResponse,
    tags=["two-tower"],
    summary="투타워 모델 재학습",
    description="내부 운영 검증에서만 사용하는 재학습 경로다.",
)
async def train_two_tower(request: TrainRequest) -> EvaluationResponse:
    return EvaluationResponse.model_validate(await run_in_threadpool(train_runtime, request.epochs))


router.include_router(public_router)

if settings.expose_legacy_two_tower_routes:
    router.include_router(legacy_router)

if settings.expose_internal_model_admin_routes:
    router.include_router(admin_router)
