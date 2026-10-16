"""Exercise the ASGI application in memory, without internet access."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from medassist import __version__
from medassist.application import create_app
from medassist.core.config import Settings


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


def test_health_without_llm_credentials(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "medassist-ai",
        "version": __version__,
        "status": "ok",
    }


def test_docs_and_openapi(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text

    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["version"] == __version__
    assert "/health" in schema["paths"]
    assert schema["components"]["schemas"]["HealthResponse"]["required"] == [
        "service",
        "version",
        "status",
    ]


def test_factories_keep_settings_separate() -> None:
    first = create_app(Settings(service_name="first", llm_api_key="test-only-secret"))
    second = create_app(Settings(service_name="second"))

    with TestClient(first) as first_client, TestClient(second) as second_client:
        first_response = first_client.get("/health")
        second_response = second_client.get("/health")

    assert first_response.json()["service"] == "first"
    assert second_response.json()["service"] == "second"
    assert set(first_response.json()) == {"service", "version", "status"}
    assert "test-only-secret" not in first_response.text


def test_uvicorn_entrypoint(client: TestClient) -> None:
    from medassist.main import app

    with TestClient(app) as entrypoint_client:
        assert entrypoint_client.get("/health").status_code == 200
