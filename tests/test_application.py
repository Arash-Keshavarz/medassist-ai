"""Verify factory imports and startup validation in fresh Python processes."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("source", ["environment", "dotenv"])
def test_factory_import_allows_explicit_settings(
    monkeypatch: pytest.MonkeyPatch, source: str
) -> None:
    if source == "environment":
        monkeypatch.setenv("MEDASSIST_SERVICE_NAME", " ")
    else:
        Path(".env").write_text('MEDASSIST_SERVICE_NAME=" "\n', encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from medassist.application import create_app\n"
            "from medassist.core.config import Settings\n"
            "from fastapi.testclient import TestClient\n"
            "settings = Settings(service_name='explicit-service')\n"
            "with TestClient(create_app(settings)) as client:\n"
            "    response = client.get('/health')\n"
            "    assert response.status_code == 200\n"
            "    assert response.json()['service'] == 'explicit-service'\n",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "startup",
    [
        "from medassist.application import create_app; create_app()",
        "import medassist.main",
    ],
)
def test_default_startup_rejects_invalid_environment(
    monkeypatch: pytest.MonkeyPatch, startup: str
) -> None:
    monkeypatch.setenv("MEDASSIST_SERVICE_NAME", " ")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pydantic import ValidationError\n"
            "try:\n"
            f"    {startup}\n"
            "except ValidationError as exc:\n"
            "    assert any(e['loc'] == ('service_name',) for e in exc.errors())\n"
            "else:\n"
            "    raise AssertionError('Invalid configuration was accepted')\n",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
