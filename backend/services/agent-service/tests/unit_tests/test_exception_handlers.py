from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from agent.core.exception_handlers import setup_global_exception_handlers


class Payload(BaseModel):
    name: str


def build_client() -> TestClient:
    app = FastAPI()
    setup_global_exception_handlers(app)

    @app.get("/unauthorized")
    async def unauthorized() -> None:
        raise HTTPException(
            status_code=401,
            detail="invalid api key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.post("/validate")
    async def validate(payload: Payload) -> Payload:
        return payload

    return TestClient(app, raise_server_exceptions=False)


def test_http_exception_uses_problem_detail_media_type_and_preserves_headers() -> None:
    client = build_client()

    response = client.get("/unauthorized")

    assert response.status_code == 401
    assert response.headers["content-type"] == "application/problem+json"
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "type": "about:blank",
        "title": "Unauthorized",
        "status": 401,
        "detail": "invalid api key",
        "instance": "/unauthorized",
    }


def test_validation_exception_uses_problem_detail_media_type() -> None:
    client = build_client()

    response = client.post("/validate", json={})

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json() == {
        "type": "about:blank",
        "title": "Bad Request",
        "status": 400,
        "detail": "body.name: Field required",
        "instance": "/validate",
    }
