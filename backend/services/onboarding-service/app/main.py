from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.db.session import dispose_database, prepare_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    await prepare_database()
    try:
        yield
    finally:
        await dispose_database()


openapi_tags = [
    {
        "name": "system",
        "description": "서비스 상태와 기본 헬스체크 경로",
    },
    {
        "name": "survey",
        "description": "설문 정의 조회, 설문 기반 미리보기, JWT 저장 경로",
    },
]

if settings.expose_legacy_two_tower_routes or settings.expose_internal_model_admin_routes:
    openapi_tags.append(
        {
            "name": "two-tower",
            "description": "내부 예제/검증에서만 쓰는 레거시 투타워 경로",
        }
    )

app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    description="사용자 온보딩 과정에서 투타워 추천 결과를 제공하는 서비스.",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, settings.frontend_origin_alt],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
