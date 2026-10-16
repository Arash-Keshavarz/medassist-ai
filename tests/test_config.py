"""Validate configuration defaults, precedence, constraints, and secret handling."""

from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from medassist.core.config import Settings


def test_defaults_need_no_credentials() -> None:
    settings = Settings()

    assert settings.service_name == "medassist-ai"
    assert settings.llm_provider == "openai"
    assert settings.llm_model is None
    assert settings.llm_api_key is None
    assert settings.llm_max_output_tokens == 1024
    assert settings.pubmed_result_limit == 10
    assert settings.request_timeout_seconds == 30.0


def test_environment_overrides_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    values = {
        "SERVICE_NAME": "research-api",
        "LLM_PROVIDER": "another-provider",
        "LLM_MODEL": "test-model",
        "LLM_API_KEY": "test-only-secret",
        "LLM_MAX_OUTPUT_TOKENS": "512",
        "PUBMED_RESULT_LIMIT": "5",
        "REQUEST_TIMEOUT_SECONDS": "12.5",
    }
    for name, value in values.items():
        monkeypatch.setenv(f"MEDASSIST_{name}", value)

    settings = Settings()

    assert settings.service_name == "research-api"
    assert settings.llm_provider == "another-provider"
    assert settings.llm_model == "test-model"
    assert isinstance(settings.llm_api_key, SecretStr)
    assert settings.llm_api_key.get_secret_value() == "test-only-secret"
    assert settings.llm_max_output_tokens == 512
    assert settings.pubmed_result_limit == 5
    assert settings.request_timeout_seconds == 12.5


def test_dotenv_and_setting_precedence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / ".env").write_text(
        "MEDASSIST_LLM_MODEL=file-model\n"
        "MEDASSIST_PUBMED_RESULT_LIMIT=7\n"
        "UNRELATED_SETTING=ignored\n",
        encoding="utf-8",
    )
    assert Settings().llm_model == "file-model"
    assert Settings().pubmed_result_limit == 7

    monkeypatch.setenv("MEDASSIST_LLM_MODEL", "environment-model")
    assert Settings().llm_model == "environment-model"
    assert Settings(llm_model="explicit-model").llm_model == "explicit-model"


def test_example_environment_starts_without_credentials(tmp_path: Path) -> None:
    example = Path(__file__).resolve().parents[1] / ".env.example"
    (tmp_path / ".env").write_text(
        example.read_text(encoding="utf-8"), encoding="utf-8"
    )

    settings = Settings()
    assert settings.llm_model is None
    assert settings.llm_api_key is None


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("LLM_MAX_OUTPUT_TOKENS", "0"),
        ("LLM_MAX_OUTPUT_TOKENS", "-1"),
        ("LLM_MAX_OUTPUT_TOKENS", "many"),
        ("PUBMED_RESULT_LIMIT", "0"),
        ("PUBMED_RESULT_LIMIT", "101"),
        ("REQUEST_TIMEOUT_SECONDS", "0"),
        ("REQUEST_TIMEOUT_SECONDS", "-1"),
        ("REQUEST_TIMEOUT_SECONDS", "nan"),
        ("REQUEST_TIMEOUT_SECONDS", "inf"),
        ("SERVICE_NAME", " "),
        ("LLM_PROVIDER", " "),
        ("LLM_MODEL", " "),
    ],
)
def test_invalid_environment_fails_validation(
    monkeypatch: pytest.MonkeyPatch, name: str, value: str
) -> None:
    monkeypatch.setenv(f"MEDASSIST_{name}", value)

    with pytest.raises(ValidationError):
        Settings()


def test_secrets_are_masked() -> None:
    settings = Settings(llm_api_key="test-only-secret")

    assert "test-only-secret" not in repr(settings)
    assert "test-only-secret" not in settings.model_dump_json()
    assert "test-only-secret" not in str(settings.llm_api_key)


def test_settings_are_immutable() -> None:
    settings = Settings()

    with pytest.raises(ValidationError, match="frozen"):
        settings.pubmed_result_limit = 20
