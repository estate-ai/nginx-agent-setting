"""수동 배치 진입점: (선택)이름 적재 → forward-slope 모델 예측 → DB 저장.

데이터가 월 단위로 갱신되므로 상시 실행하지 않는다. fetch로 정제본을 갱신한 뒤
`python -m app.batch`로 1회 실행한다(보통 cron에서 `fetch && batch`).

학습과 결과 갱신을 분리한다:
- 이 배치는 모델을 학습하지 않는다.
- 학습 완료 모델·메타를 확인한 뒤, 정제본을 읽어 예측·인기 배너 스냅샷을 DB에 저장한다.

사용:
    python -m app.batch            # 정제본에 새 데이터 있으면 예측, 없으면 스킵
    python -m app.batch --force    # 새 데이터 여부와 무관하게 실행
    python -m app.batch --ingest   # 행정동 이름 CSV(.raw) 재적재까지 포함
    python -m app.batch --refresh-banner  # 배너 스냅샷만 DB에 갱신
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime

from app.models.commercial_trend.runtime import (
    build_banner_sections_from_rankings,
    compute_theme_rankings,
    refresh_banner_sections,
    require_model_artifacts,
)
from app.models.commercial_trend.time_of_day import latest_aggregate_date


def run_batch(
    data_mode: str = "db", ingest: bool = False, force: bool = False, refresh_banner: bool = False
) -> dict[str, object]:
    if data_mode != "db":
        raise ValueError("배치는 db 모드에서만 동작한다(결과를 DB에 저장하므로).")

    from app.db.session import prepare_database

    prepare_database()  # 테이블 보장(설정에 따라 행정동 이름 부트스트랩)

    if ingest:
        from app.trend.ingest import ingest_bootstrap_into_db

        ingest_bootstrap_into_db()

    if refresh_banner:
        sections = refresh_banner_sections(data_mode)
        return {
            "skipped": False,
            "refreshed_banner": True,
            "forecast_counts": {theme: len(rows) for theme, rows in sections["forecast"].items()},
            "popular_counts": {theme: len(rows) for theme, rows in sections["popular"].items()},
        }

    from app.trend.repository import last_trained_as_of, save_prediction_run

    # 새 데이터가 없으면(정제본 최신일 <= 마지막 예측 기준일) 건너뛴다.
    source_date = latest_aggregate_date()
    last_date = last_trained_as_of()
    if not force and source_date is not None and last_date is not None and source_date <= last_date:
        return {
            "skipped": True,
            "reason": "새 데이터 없음",
            "source_date": str(source_date),
            "last_trained": str(last_date),
        }

    model_meta = require_model_artifacts()

    # 정제본을 읽어 예측·배너 스냅샷을 계산한 뒤 같은 회차로 저장한다.
    rankings = compute_theme_rankings(data_mode)
    sections = build_banner_sections_from_rankings(data_mode, rankings)
    # 정제본이 없어 compute 중 시드된 경우를 위해 as_of를 다시 읽는다.
    as_of_date = source_date or latest_aggregate_date()
    saved_scores = save_prediction_run(
        rankings=rankings,
        sections=sections,
        run_at=datetime.now(UTC),
        as_of_date=as_of_date,
        data_mode=data_mode,
    )

    return {
        "skipped": False,
        "as_of": str(as_of_date),
        "model_id": model_meta.get("model_id"),
        "model_trained_at": model_meta.get("trained_at"),
        "model_validation": model_meta.get("validation"),
        "saved_themes": list(rankings),
        "saved_scores": saved_scores,
        "saved_banner_forecast": {theme: len(rows) for theme, rows in sections["forecast"].items()},
        "saved_banner_popular": {theme: len(rows) for theme, rows in sections["popular"].items()},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="상권 트렌드 배치(forward-slope 모델 예측→DB 저장)")
    parser.add_argument("--data-mode", default="db", choices=["db"])
    parser.add_argument("--ingest", action="store_true", help="실행 전 .raw 행정동 이름 CSV 재적재")
    parser.add_argument("--force", action="store_true", help="새 데이터 여부와 무관하게 실행")
    parser.add_argument("--refresh-banner", action="store_true", help="배너 결과 스냅샷만 DB에 갱신")
    args = parser.parse_args()
    result = run_batch(args.data_mode, ingest=args.ingest, force=args.force, refresh_banner=args.refresh_banner)
    print(json.dumps(result, ensure_ascii=False, indent=2))
