from __future__ import annotations

import unittest

from app.models.onboarding_category_tower.runtime import predict_payload, train_runtime


class OnboardingCategoryTowerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """테스트 시작 전에 경량 학습으로 업종 추천 artifact를 맞춘다."""

        cls.metadata = train_runtime(epochs=2)

    def test_training_metadata_contains_expected_fields(self) -> None:
        """학습 결과 메타데이터는 이후 API 연결에 필요한 핵심 필드를 포함해야 한다."""

        self.assertEqual(self.metadata["model_id"], "onboarding_category_tower")
        self.assertEqual(self.metadata["category_count"], 5)
        self.assertGreaterEqual(self.metadata["embedding_dim"], 16)
        self.assertIn("user_numeric_features", self.metadata)
        self.assertIn("item_numeric_features", self.metadata)

    def test_known_sample_profile_returns_target_category_within_top_k(self) -> None:
        """기준 프로토타입으로 예측하면 해당 업종이 상위 추천 안에 포함돼야 한다."""

        payload = predict_payload({"user_id": "category_proto_cs100005"}, top_k=3)
        codes = [row["service_category_code"] for row in payload["recommendations"]]

        self.assertEqual(payload["model_id"], "onboarding_category_tower")
        self.assertEqual(payload["user_profile"]["user_id"], "category_proto_cs100005")
        self.assertIn("CS100005", codes)
        self.assertEqual(len(payload["recommendations"]), 3)


if __name__ == "__main__":
    unittest.main()
