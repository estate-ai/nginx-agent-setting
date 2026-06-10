# Simple Agent Template

아래의 명령어로 생성한 AGENT SERVER 입니다.

```
uvx --from langgraph-cli@latest langgraph new \
  경로명 \
  --template agent-python
```

ㅇㅋ 복사용으로 다시 정리.

## Agent Server 자체

* [**Agent Server 개념**](https://docs.langchain.com/langsmith/agent-server) — assistants / threads / runs / persistence / task queue 설명
* [**Agent Server changelog**](https://docs.langchain.com/langsmith/agent-server-changelog) — Agent Server가 API platform이라고 명확히 설명됨
* [**LangSmith Deployment**](https://docs.langchain.com/langsmith/deployment) — 배포 후 Agent Server 실행 모델

## CLI / 템플릿 / 로컬 실행

* [**LangGraph CLI**](https://docs.langchain.com/langsmith/cli) — Agent Server를 로컬에서 build/run하는 공식 CLI
* [**Local development & testing**](https://docs.langchain.com/langsmith/local-dev-testing) — `langgraph dev` vs `langgraph up`
* [**Python: Run a local server**](https://docs.langchain.com/oss/python/langgraph/local-server) — `langgraph new`, `langgraph dev`, `/docs`, `/runs/stream`
* [**JavaScript: Run a local server**](https://docs.langchain.com/oss/javascript/langgraph/local-server) — JS/TS 템플릿과 Agent Server 실행
* [**Application structure**](https://docs.langchain.com/langsmith/application-structure) — `langgraph.json`, `graphs`, `env`, dependencies 구조
* [**LangGraph Studio**](https://docs.langchain.com/oss/python/langgraph/studio) — `langgraph dev`가 local development server / Agent Server를 띄움

## React / SDK 연동

* [**Frontend overview**](https://docs.langchain.com/oss/python/langchain/frontend/overview) — `useStream`, `apiUrl`, `assistantId` 설명
* [**Streaming frontend**](https://docs.langchain.com/oss/python/langchain/streaming/frontend) — React 앱에서 LangGraph SDK / `useStream` 연결
* [**JavaScript LangGraph frontend overview**](https://docs.langchain.com/oss/javascript/langgraph/frontend/overview) — JS/TS 쪽 `@langchain/react` + `useStream`
* [**JavaScript streaming**](https://docs.langchain.com/oss/javascript/langgraph/streaming) — `@langchain/langgraph-sdk/react`의 `useStream` 언급
* [**LangGraph.js API Reference**](https://langchain-ai.github.io/langgraphjs/reference/) — `@langchain/langgraph-sdk` API 레퍼런스

## 운영 / 보안

* [**Authentication & access control**](https://docs.langchain.com/langsmith/auth) — Agent Server 인증/권한 개념
* [**Add custom authentication**](https://docs.langchain.com/langsmith/custom-auth) — custom auth 적용
* [**Set up custom authentication**](https://docs.langchain.com/langsmith/set-up-custom-auth) — 튜토리얼형 auth 세팅
* [**Custom routes**](https://docs.langchain.com/langsmith/custom-routes) — Agent Server에 커스텀 route 추가
* [**MCP endpoint in Agent Server**](https://docs.langchain.com/langsmith/server-mcp) — Agent Server의 `/mcp` 엔드포인트


Minimal deployment template for a LangChain agent built with `create_agent(...)`.

## What this template gives you

- A deployable LangGraph entrypoint at `src/simple_agent/graph.py`.
- Two small tools (`utc_now`, `calculator`) for predictable local behavior.
- `langgraph.json` configured for LangSmith/LangGraph deployment.
- A `uv`-managed local workflow with a small `Makefile` wrapper and starter tests.

## Quickstart

1. Sync the project with `uv`:

```bash
uv sync --dev
```

2. Configure environment:

```bash
cp .env.example .env
```

3. Run locally:

```bash
uv run langgraph dev
```

Optional `make` wrappers:

```bash
make dev
make run
```

## Tests and lint

```bash
make test
make integration-tests
make lint
make format
```

Integration tests are skipped unless `ANTHROPIC_API_KEY` is set.

## Deploy to LangSmith

1. Push this template to a Git repository.
2. In LangSmith, create a new Deployment from that repo.
3. Set required environment variables (`ANTHROPIC_API_KEY`, optionally `LANGSMITH_API_KEY`).
4. Deploy using `langgraph.json` defaults.

## Reference docs

- LangChain quickstart: https://docs.langchain.com/oss/python/langchain/quickstart
- LangChain deployment: https://docs.langchain.com/oss/python/langchain/deploy
