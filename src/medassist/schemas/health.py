"""Public health response contract."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Service identity and application liveness, excluding configuration secrets."""

    service: str
    version: str
    status: Literal["ok"]
