from __future__ import annotations

import unittest

from app.models.category_profile.features import build_category_profiles


class CategoryProfileTestCase(unittest.TestCase):
    def test_sample_category_profiles_include_joined_sales_store_and_activity_features(self) -> None:
        """샘플 업종 프로파일은 매출, 점포, 영세자영업 피처를 한 프레임으로 합쳐야 한다."""

        frame = build_category_profiles(data_mode="sample", trainable_only=False)
        bakery = frame[frame["service_category_code"] == "CS100005"].iloc[0]

        self.assertEqual(len(frame), 5)
        self.assertEqual(bakery["service_category_name"], "제과점")
        self.assertEqual(bakery["category_group"], "외식업")
        self.assertEqual(int(bakery["is_trainable"]), 1)
        self.assertGreater(float(bakery["weekend_sales_ratio"]), 0)
        self.assertGreater(float(bakery["avg_business_years"]), 0)
        self.assertIn("stability_prior_score", frame.columns.tolist())
        self.assertIn("competition_pressure_score", frame.columns.tolist())
        self.assertIn("startup_cost_million_krw_proxy", frame.columns.tolist())

    def test_raw_category_profiles_include_convenience_store(self) -> None:
        """raw 업종 프로파일은 기존 5개 외 편의점 코드도 포함해야 한다."""

        frame = build_category_profiles(data_mode="raw", trainable_only=True)

        self.assertIn("CS300002", set(frame["service_category_code"].astype(str)))
        self.assertGreaterEqual(len(frame), 60)


if __name__ == "__main__":
    unittest.main()
