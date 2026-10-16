"""Application liveness endpoint; no external services are contacted."""

from typing import Annotated

from fastapi import APIRouter, Depends

from medassist import __version__
from medassist.api.dependencies import get_settings
from medassist.core.config import Settings
from medassist.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    """Report application identity and liveness."""
    return HealthResponse(
        service=settings.service_name,
        version=__version__,
        status="ok",
    )
