from typing import Optional

from pydantic import BaseModel, Field


class ProblemDetail(BaseModel):
    """
    RFC 7807 Problem Details for HTTP APIs
    FastAPI 예외 응답을 Spring Boot와 동일한 규격으로 통일하기 위한 모델입니다.
    """

    type: str = Field(default="about:blank", description="에러 유형을 나타내는 URI")
    title: Optional[str] = Field(default=None, description="에러에 대한 짧은 요약")
    status: int = Field(description="HTTP 상태 코드")
    detail: Optional[str] = Field(default=None, description="에러 발생 원인 상세 설명")
    instance: Optional[str] = Field(default=None, description="에러가 발생한 API 엔드포인트 URI")
