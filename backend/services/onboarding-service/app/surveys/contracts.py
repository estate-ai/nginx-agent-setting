from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.two_tower.contracts import PredictResponse, StoredUserTowerProfile, UserProfilePayload


class SurveyOption(BaseModel):
    code: str
    label: str


class SurveyQuestion(BaseModel):
    id: str
    selection_type: Literal["single", "multi"]
    prompt: str
    max_selections: int | None = None
    options: list[SurveyOption]
    primary_parameters: list[str]
    secondary_parameters: list[str]


class SurveyDefinitionSummary(BaseModel):
    id: int
    slug: str
    version: int
    survey_code: str
    scoring_version: str
    title: str
    description: str
    question_count: int


class SurveyDefinitionResponse(SurveyDefinitionSummary):
    questions: list[SurveyQuestion]


class SurveyPreviewRequest(BaseModel):
    top_k: int = Field(default=5, ge=1, le=10, description="반환할 추천 개수")
    preferred_category_code: str = Field(default="CS100001", description="설문 바깥에서 따로 고른 선호 업종 코드")
    profile_name: str = Field(default="설문 결과 프로필", description="프론트에 표시할 프로필 이름")
    answers: dict[str, Any] = Field(description="문항 id 기준 응답 JSON")


class SaveSurveyResultRequest(BaseModel):
    profile_code: str = Field(description="미리보기 응답에서 받은 base36 공유 코드")
    top_k: int = Field(default=5, ge=1, le=10, description="반환할 추천 개수")
    profile_name: str | None = Field(default=None, description="저장 시 덮어쓸 프로필 이름")
    survey_response_id: int | None = Field(
        default=None,
        description="같은 미리보기 응답을 그대로 저장할 때 넘기는 설문 응답 ID",
    )


class SurveyResultEnvelope(BaseModel):
    survey: SurveyDefinitionSummary
    survey_response_id: int | None
    profile: StoredUserTowerProfile
    prediction: PredictResponse


class SurveyAnswerValidationRequest(BaseModel):
    question: SurveyQuestion
    answer: Any

    @model_validator(mode="after")
    def validate_answer_shape(self) -> "SurveyAnswerValidationRequest":
        if self.question.selection_type == "single":
            if not isinstance(self.answer, str):
                raise ValueError("단일선택 문항은 문자열 코드 하나를 받아야 한다.")
            return self

        if not isinstance(self.answer, list) or not all(isinstance(item, str) for item in self.answer):
            raise ValueError("복수선택 문항은 문자열 코드 배열을 받아야 한다.")
        if self.question.max_selections is not None and len(self.answer) > self.question.max_selections:
            raise ValueError("복수선택 허용 개수를 초과했다.")
        return self


class SurveyScoredProfile(BaseModel):
    survey_code: str
    user_profile: UserProfilePayload
    answers: dict[str, Any]
