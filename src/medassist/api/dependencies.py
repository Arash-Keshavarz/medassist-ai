"""Resolve dependencies from the current application's state."""

from fastapi import Request

from medassist.core.config import Settings


def get_settings(request: Request) -> Settings:
    """Return the settings owned by this application instance."""
    return request.app.state.settings
