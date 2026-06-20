# authentik MSA user API

## service token

`.env`의 `AUTHENTIK_MSA_USER_API_TOKEN`은 authentik REST API 호출용 Bearer token이다.
`AUTHENTIK_CLIENT_SECRET`은 OIDC authorization code 교환용 client secret이라 MSA user DB 조회에 쓰지 않는다.

```env
AUTHENTIK_MSA_USER_API_TOKEN=...
```

`docker-compose.yml`은 이 값을 `authentik-server`와 `authentik-worker`에 주입한다.
`backend/authentik/blueprints/pickle-web.yaml`은 `svc-msa-user-api` 유저와 `msa-user-api-token`을 선언한다.

```yaml
AUTHENTIK_MSA_USER_API_TOKEN: ${AUTHENTIK_MSA_USER_API_TOKEN}
```

`backend/authentik/scripts/bootstrap-msa-user-api.py`는 blueprint가 만든 role/user/token에 user model 권한을 붙인다.
authentik blueprint의 `permissions:` 필드는 object-level permission이라 `/core/users/` 목록 조회에 필요한 global/model permission을 만들지 않는다.

```bash
make authentik-bootstrap-msa-user-api
```

이 스크립트는 재실행 가능하다.
토큰 값을 바꾼 뒤 같은 명령을 다시 실행하면 `msa-user-api-token.key`가 `.env` 값으로 갱신된다.

```text
svc-msa-user-api
  -> role: msa-user-api-manager
  -> token: msa-user-api-token
  -> permissions:
     authentik_core.view_user
     authentik_core.change_user
```

## Authorization

MSA 컨테이너 안에서는 authentik REST API를 내부 주소로 호출한다.

```http
GET http://authentik-server:9000/api/v3/core/users/?page_size=20
Authorization: Bearer ${AUTHENTIK_MSA_USER_API_TOKEN}
```

브라우저/프론트 개발 환경에서는 Traefik 라벨이 붙은 `/api/authentik` 경로를 쓴다.
`docker-compose.yml`의 `authentik-strip` middleware가 `/api/authentik` prefix를 제거하고 authentik으로 넘긴다.

```text
/api/authentik/core/users/
-> authentik-server:9000/api/v3/core/users/
```

## /core/users/

MSA에서 1차로 쓰는 authentik user DB API는 `/api/v3/core/users/` 아래로 제한한다.
Orval 카탈로그에는 `app.api.name=authentik-users`로 들어간다.

```http
GET /api/v3/core/users/
GET /api/v3/core/users/{id}/
PATCH /api/v3/core/users/{id}/
```

`id`는 authentik REST API의 `pk`다.
서비스 DB에서 장기 외부키로 들고 갈 값은 `uuid`를 우선한다.
`pk`는 REST 상세 호출용 캐시 컬럼으로 둔다.

```json
{
  "pk": 5,
  "uuid": "27bc9058-687c-4dba-a409-0ef1bea8ff24",
  "username": "user@example.com",
  "name": "Example User",
  "email": "user@example.com",
  "is_active": true,
  "attributes": {
    "displayName": "example-user"
  }
}
```

프로필 표시명처럼 서비스 전체에서 공유할 값은 authentik user `attributes`에 둔다.

```http
PATCH /api/v3/core/users/5/
Authorization: Bearer ${AUTHENTIK_MSA_USER_API_TOKEN}
Content-Type: application/json

{
  "attributes": {
    "displayName": "example-user"
  }
}
```

## JWT

현재 `pickle-web` OAuth2 provider는 `sub_mode: hashed_user_id`다.
이 값은 authentik REST user의 `pk`나 `uuid`가 아니다.

```yaml
issuer_mode: per_provider
sub_mode: hashed_user_id
include_claims_in_id_token: true
```

백엔드 서비스가 JWT만으로 authentik user DB row를 찾아야 하면 authentik OAuth scope mapping에 별도 claim을 추가한다.

```json
{
  "sub": "hashed-provider-subject",
  "authentik_user_pk": 5,
  "authentik_user_uuid": "27bc9058-687c-4dba-a409-0ef1bea8ff24"
}
```

JWT 검증은 지금처럼 JWKS/issuer/audience 계약으로 한다.
user profile 원본 조회와 수정은 `AUTHENTIK_MSA_USER_API_TOKEN`으로 `/core/users/`를 호출한다.

```text
Browser
  -> Authorization: Bearer <authentik access token>
  -> MSA verifies JWT with JWKS
  -> MSA reads auth user profile with AUTHENTIK_MSA_USER_API_TOKEN
```

## 주요 파일

- `docker-compose.yml`
- `.env.example`
- `backend/authentik/blueprints/pickle-web.yaml`
- `backend/authentik/scripts/bootstrap-msa-user-api.py`
- `frontend/scripts/fetch-service-catalog.mjs`
- `frontend/orval.config.ts`

## 참고 문서

- https://docs.goauthentik.io/developer-docs/api/
- https://docs.goauthentik.io/sys-mgmt/blueprints/
- https://docs.goauthentik.io/add-secure-apps/providers/oauth2/
