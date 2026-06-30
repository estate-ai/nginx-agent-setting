from __future__ import annotations

import unittest

from pydantic import ValidationError

from app.surveys.contracts import (
    SurveyDefinitionResponse,
    SurveyPreviewRequest,
    SurveyProfileUpdateRequest,
)
from app.surveys.definitions import active_survey_definition
from app.surveys.service import _category_codes_for_data_mode, _normalize_age_distribution, _score_definition
from app.two_tower.contracts import AreaUserProfilePayload
from app.models.onboarding_category_tower.contracts import CategoryUserProfilePayload


class SurveyScoringTestCase(unittest.TestCase):
    def test_profile_update_patch_accepts_only_zero_to_one_values(self) -> None:
        """채팅 기반 성향 패치는 유저타워 점수 범위를 벗어날 수 없다."""

        request = SurveyProfileUpdateRequest(
            base_result_code="r0a1b2c3d4e5f6g",
            patch={"budget_level": 0.72},
        )
        self.assertEqual(request.patch["budget_level"], 0.72)

        with self.assertRaises(ValidationError):
            SurveyProfileUpdateRequest(
                base_result_code="r0a1b2c3d4e5f6g",
                patch={"budget_level": 1.2},
            )

    def test_preview_scoring_builds_area_and_category_profiles(self) -> None:
        """설문 점수 계산은 상권용 9축과 업종용 17축을 함께 만들어야 한다."""

        raw_definition = active_survey_definition()
        definition = SurveyDefinitionResponse.model_validate(
            {
                "id": 1,
                "slug": raw_definition["slug"],
                "version": raw_definition["version"],
                "survey_code": raw_definition["survey_code"],
                "scoring_version": raw_definition["scoring_version"],
                "title": raw_definition["title"],
                "description": raw_definition["description"],
                "question_count": len(raw_definition["questions"]),
                "questions": raw_definition["questions"],
            }
        )

        scored = _score_definition(
            definition,
            SurveyPreviewRequest(
                profile_name="점수 계산 테스트",
                answers={
                    "q1": "A",
                    "q2": "A",
                    "q3": "A",
                    "q4": "A",
                    "q5": "A",
                    "q6": "A",
                    "q7": "A",
                    "q8": "A",
                    "q9": "A",
                    "q10": "A",
                    "q11": "A",
                    "q12": ["A", "C"],
                },
            ),
            question_lookup={
                str(question["id"]): dict(question)
                for question in raw_definition["questions"]
            },
        )

        self.assertEqual(scored.survey_code, "A")
        self.assertEqual(scored.answers["q12"], ["A", "C"])
        self.assertAlmostEqual(scored.area_user_profile.subway_dependency_level, 0.95)
        self.assertLess(scored.area_user_profile.budget_level, 0.2)
        self.assertGreater(scored.area_user_profile.stability_level, 0.7)
        self.assertGreater(scored.category_user_profile.lunch_preference_level, 0.8)
        self.assertGreater(scored.category_user_profile.female_preference_level, 0.8)
        self.assertLess(scored.category_user_profile.labor_intensity_tolerance, 0.2)
        self.assertAlmostEqual(
            scored.category_user_profile.target_age_10_level
            + scored.category_user_profile.target_age_20_level
            + scored.category_user_profile.target_age_30_level
            + scored.category_user_profile.target_age_40_level
            + scored.category_user_profile.target_age_50_plus_level,
            1.0,
            places=2,
        )

    def test_area_recommendation_category_codes_use_raw_catalog(self) -> None:
        """상권 추천 업종 검증 코드는 raw 카탈로그에서 동적으로 읽어야 한다."""

        codes = _category_codes_for_data_mode("raw")

        self.assertIn("CS300002", codes)
        self.assertGreaterEqual(len(codes), 60)

    def test_profile_payloads_clamp_minor_out_of_range_scores(self) -> None:
        """계산 과정에서 생긴 -0.01 같은 경계 오차는 Pydantic 에러 대신 0~1로 보정해야 한다."""

        area = AreaUserProfilePayload(budget_level=-0.01, stability_level=1.01)
        category = CategoryUserProfilePayload(stability_level=-0.01, franchise_affinity_level=1.01)

        self.assertEqual(area.budget_level, 0.0)
        self.assertEqual(area.stability_level, 1.0)
        self.assertEqual(category.stability_level, 0.0)
        self.assertEqual(category.franchise_affinity_level, 1.0)

    def test_age_distribution_normalization_never_goes_negative(self) -> None:
        """나이 비중 반올림은 마지막 값을 음수로 만들지 않고 합계 1.0을 유지해야 한다."""

        payload = {
            "target_age_10_level": 0.335,
            "target_age_20_level": 0.335,
            "target_age_30_level": 0.335,
            "target_age_40_level": 0.335,
            "target_age_50_plus_level": 0.001,
        }

        normalized = _normalize_age_distribution(payload)
        values = [normalized[field] for field in normalized]

        self.assertTrue(all(0.0 <= value <= 1.0 for value in values))
        self.assertAlmostEqual(sum(values), 1.0, places=2)


if __name__ == "__main__":
    unittest.main()
