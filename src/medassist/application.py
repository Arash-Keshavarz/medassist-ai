"""Application composition without loading configuration at import time."""

from fastapi import FastAPI

from medassist import __version__
from medassist.api.health import router as health_router
from medassist.core.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build an independent application with validated configuration."""
    settings = settings if settings is not None else Settings()
    application = FastAPI(
        title=settings.service_name,
        version=__version__,
        description="An evidence-grounded medical literature research assistant.",
    )
    application.state.settings = settings
    application.include_router(health_router)
    return application
