import logging
import traceback
from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from agent.schemas.problem_detail import ProblemDetail

logger = logging.getLogger(__name__)
PROBLEM_JSON_MEDIA_TYPE = "application/problem+json"


def _problem_detail_response(
    status_code: int,
    problem_detail: ProblemDetail,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=problem_detail.model_dump(exclude_none=True),
        headers=headers,
        media_type=PROBLEM_JSON_MEDIA_TYPE,
    )


def setup_global_exception_handlers(app: FastAPI) -> None:
    """
    FastAPI 애플리케이션에 글로벌 예외 핸들러를 등록합니다.
    모든 예외를 RFC 7807 (ProblemDetail) 형식의 JSON으로 변환하여 반환합니다.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = str(exc.detail)
        try:
            title = HTTPStatus(exc.status_code).phrase
        except ValueError:
            title = "Error"

        pd = ProblemDetail(
            status=exc.status_code,
            title=title,
            detail=detail,
            instance=str(request.url.path),
        )
        return _problem_detail_response(
            status_code=exc.status_code,
            problem_detail=pd,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        messages = []
        for error in errors:
            loc = ".".join(str(part) for part in error.get("loc", []))
            msg = error.get("msg", "")
            messages.append(f"{loc}: {msg}")

        detail = ", ".join(messages) if messages else "요청 파라미터 검증에 실패했습니다."

        pd = ProblemDetail(
            status=status.HTTP_400_BAD_REQUEST,
            title="Bad Request",
            detail=detail,
            instance=str(request.url.path),
        )
        return _problem_detail_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            problem_detail=pd,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            f"Unhandled Exception at {request.method} {request.url.path}: {exc}\n{traceback.format_exc()}"
        )
        pd = ProblemDetail(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail="서버 내부 오류가 발생했습니다.",
            instance=str(request.url.path),
        )
        return _problem_detail_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            problem_detail=pd,
        )
