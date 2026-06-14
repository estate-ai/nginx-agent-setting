# new-svc.md

## Swagger (OpenAPI)

새로운 서비스를 추가할 때는 Swagger(OpenAPI) 명세를 제공해야 한다.
서비스 내부에 OpenAPI JSON을 반환하는 엔드포인트를 구현한다.

## docker-compose.yml 설정

`docker-compose.yml`에 서비스를 등록하고, `app.api.*` 라벨을 설정한다.

```yaml
    labels:
      - app.api.enabled=true
      - app.api.name=서비스이름
      - app.api.publicPath=라우팅경로
      - app.api.openapiPath=OpenAPI경로
      - app.api.schemasType=zod
```

`app.api.schemasType` 라벨의 기본값은 `zod`이다.

## 주요 파일

- [docker-compose.yml](../../docker-compose.yml)
