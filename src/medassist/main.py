"""Uvicorn entry point; validate environment configuration on startup."""

from medassist.application import create_app

app = create_app()
