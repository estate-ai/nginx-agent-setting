from __future__ import annotations

import unittest

from app.models.item_catalog.features import build_item_features


class ItemCatalogTestCase(unittest.TestCase):
    def test_sample_catalog_contains_expected_area_features(self) -> None:
        """샘플 카탈로그는 행정동-업종 후보와 보강된 상권 피처를 만든다."""

        catalog = build_item_features(data_mode="sample")
        item = catalog[catalog["item_id"] == "11110515:CS100005"].iloc[0]

        self.assertEqual(item["area_name"], "청운효자동")
        self.assertEqual(item["area_profile_type"], "residential")
        self.assertGreater(float(item["resident_population"]), 0)
        self.assertGreater(float(item["worker_population"]), 0)
        self.assertIn(
            "subway_commercial_trend_score",
            catalog.columns.tolist(),
        )

    def test_raw_catalog_uses_dynamic_category_cost_proxy(self) -> None:
        """raw 카탈로그는 편의점 후보와 동적 창업 비용 프록시를 포함해야 한다."""

        catalog = build_item_features(data_mode="raw")
        convenience_items = catalog[catalog["service_category_code"] == "CS300002"]

        self.assertFalse(convenience_items.empty)
        self.assertIn("startup_cost_million_krw_proxy", catalog.columns.tolist())
        self.assertGreater(float(convenience_items.iloc[0]["startup_cost_million_krw_proxy"]), 0)


if __name__ == "__main__":
    unittest.main()
