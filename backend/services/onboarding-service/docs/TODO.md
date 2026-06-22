# TODO

`app/models/category_profile/features.py`는 업종 메타 피처를 만든다.

```text
estimated_sales_hdong_2025.sample.csv
+ store_hdong_2025.sample.csv
+ small_business_activity_by_sector.sample.csv
-> service_category_code 기준 업종 프로파일
```

`app/models/onboarding_category_tower/`는 업종 추천용 학습과 추론 런타임을 만든다.

```text
train.py
-> .artifacts/onboarding_category_tower/
   + user_tower.weights.h5
   + item_tower.weights.h5
   + category_embeddings.csv
   + metadata.json
```

## app/models/onboarding_category_tower

현재 유저 입력 축은 아래 17개다.

```text
stability_level
competition_tolerance_level
weekend_preference_level
lunch_preference_level
evening_preference_level
late_night_preference_level
target_age_10_level
target_age_20_level
target_age_30_level
target_age_40_level
target_age_50_plus_level
female_preference_level
avg_ticket_preference
traffic_volume_preference
franchise_affinity_level
labor_intensity_tolerance
space_efficiency_preference
```

현재 샘플 학습은 synthetic user를 쓴다.

```text
업종 프로파일 1개
-> 기준 프로토타입 1개
-> jitter를 준 synthetic user 6개
-> target_category_code 1개
```

이 단계에서는 설문 연동이 아직 없다.

## app/surveys/contracts.py

`preferred_category_code`를 설문 미리보기 입력에서 바로 강제하지 않도록 바꿔야 한다.

지금 흐름:

```text
SurveyPreviewRequest
-> preferred_category_code required
```

다음 흐름:

```text
SurveyPreviewRequest
-> answers
-> profile_name
-> top_k
-> preferred_category_code optional
```

업종 추천 단계 응답 shape를 별도로 추가한다.

```text
survey
+ category_recommendations
  + service_category_code
  + service_category_name
  + score
+ category_user_profile
```

## app/surveys/service.py

`_score_definition()`는 현재 9개 상권추천 점수만 만든다.

여기서 해야 할 일:

1. 기존 9개 상권추천 점수 계산은 유지한다.
2. 업종 추천용 17개 파라미터를 계산하는 함수 하나를 추가한다.
3. 설문 미리보기 응답에서 `onboarding_category_tower.runtime.predict_payload()`를 먼저 호출한다.
4. 사용자가 업종을 확정하기 전까지는 기존 `two_tower.resolve_prediction_response()`를 호출하지 않는다.

권장 흐름:

```text
preview_survey_result()
-> area_user_profile 계산
-> category_user_profile 계산
-> category 추천 5개 반환
```

```text
confirm_selected_category()
-> selected_category_code
-> area_user_profile
-> two_tower 추천 반환
```

## app/db/models.py

지금 `survey_responses.preferred_category_code`는 설문 단계에서 바로 채워진다.
업종 추천 단계를 넣으면 저장 시점이 둘로 나뉜다.

확인할 필드:

```text
survey_responses
+ preferred_category_code
+ answers_json
+ scored_profile_json
```

추천 작업:

1. `preferred_category_code`를 nullable로 바꾼다.
2. `scored_profile_json`에 `area_user_profile`과 `category_user_profile`을 같이 넣는다.
3. 업종 선택 후 확정된 `preferred_category_code`를 업데이트한다.
4. 업종 추천 5개 snapshot을 보관할지 결정한다.

snapshot을 저장하면 아래 shape가 필요하다.

```json
{
  "category_recommendations": [
    {
      "service_category_code": "CS100005",
      "score": 0.82
    }
  ]
}
```

## app/api/routes.py

현재 공개 설문 경로는 한 번의 preview로 바로 상권추천까지 내려보낸다.

추가할 경로:

```text
POST /surveys/active/preview
-> 업종 추천 5개 반환

POST /surveys/active/confirm-category
-> 선택 업종으로 상권추천 반환
```

`/surveys/results/{profile_code}`도 업종 선택 이후 결과만 공개할지, 업종 추천 단계 코드도 허용할지 결정해야 한다.

## app/two_tower/codecs.py

현재 공유코드는 `preferred_category_code + 9개 상권 점수`만 담는다.

```text
r + version + survey_code + category + 9개 점수
```

업종 추천 단계에서는 아직 업종이 확정되지 않았으므로 지금 공유코드를 바로 만들 수 없다.

선택지:

1. 업종 확정 이후에만 기존 공유코드를 발급한다.
2. 업종 추천 단계 전용 임시 코드 포맷을 새로 만든다.

첫 단계에서는 `1`이 더 단순하다.

## tests

현재 추가된 테스트:

- `tests/test_category_profile.py`
- `tests/test_onboarding_category_tower.py`

다음 테스트가 더 필요하다.

1. 설문 preview가 업종 추천만 반환하는지 확인
2. 업종 선택 후 상권추천으로 이어지는지 확인
3. 업종 미확정 설문 저장과 업종 확정 저장이 모두 되는지 확인
4. 공유코드가 업종 확정 이후에만 발급되는지 확인

## 학습 명령

업종 추천 모델 학습:

```bash
uv run --python 3.11 python -m app.models.onboarding_category_tower.train --epochs 24
```

샘플 예측:

```bash
uv run --python 3.11 python -m app.models.onboarding_category_tower.predict --user-id category_proto_cs100005 --top-k 5
```

샘플 검증:

```bash
uv run --python 3.11 python -m unittest tests.test_category_profile tests.test_onboarding_category_tower -v
```

## 주요 파일

- `app/models/category_profile/features.py`
- `app/models/onboarding_category_tower/contracts.py`
- `app/models/onboarding_category_tower/user_profiles.py`
- `app/models/onboarding_category_tower/train.py`
- `app/models/onboarding_category_tower/predict.py`
- `app/models/onboarding_category_tower/runtime.py`
- `tests/test_category_profile.py`
- `tests/test_onboarding_category_tower.py`
