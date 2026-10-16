"""Typed environment configuration, independent of HTTP and provider SDKs."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings; credentials and model selection are optional at startup."""

    model_config = SettingsConfigDict(
        env_prefix="MEDASSIST_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        frozen=True,
        str_strip_whitespace=True,
        hide_input_in_errors=True,
    )

    service_name: str = Field(default="medassist-ai", min_length=1)
    llm_provider: str = Field(default="openai", min_length=1)
    llm_model: str | None = Field(default=None, min_length=1)
    llm_api_key: SecretStr | None = Field(default=None, repr=False)
    llm_max_output_tokens: int = Field(default=1024, gt=0)
    pubmed_result_limit: int = Field(default=10, ge=1, le=100)
    request_timeout_seconds: float = Field(default=30.0, gt=0, allow_inf_nan=False)
