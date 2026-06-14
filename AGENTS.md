# AGENTS

- 문서를 작성할 때에는 [writing-docs.md](docs/agents/writing-docs.md)를 참고한다.
- 신규 백엔드 서비스를 생성할 때에는 [new-svc.md](docs/agents/new-svc.md)를 참고한다.

커밋을 작성할 때에는 아래 규칙의 멀티라인 커밋 형식을 사용한다.

```text
타입: 한국어 요약

- 한국어 상세 내용
- 한국어 상세 내용
```

타입 종류: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ui`

- `ui` - 비즈니스 로직 변경 없이 디자인/스타일만 변경
- `feat` - 사용자에게 영향을 주는 새로운 기능 추가
- `chore` - 빌드 설정, 의존성 패키지 관리, 환경 설정 등 관리성 작업 변경
- `test` - 테스트 코드 추가 및 수정
- `refactor` - 테스트 코드 및 기능(사용자 경험) 변경 없는 코드 구조 개선
- `fix` - 버그 및 장애 원인 수정
- `docs` - 문서 추가 및 수정
