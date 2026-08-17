"""Shared pytest fixtures. Forces offline mode (no API keys) for all tests."""

from __future__ import annotations

import os

import pytest

# Ensure tests never accidentally hit a real provider. Setting these to EMPTY
# (rather than popping them) is essential: pydantic-settings also reads the real
# ``.env`` file, and OS env vars take precedence over it — so an empty env var
# overrides any key present in .env, guaranteeing fully offline test runs.
os.environ["GOOGLE_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["LLAMA_CLOUD_API_KEY"] = ""
os.environ["LLM_PROVIDER"] = "echo"

# Drop any settings cached before the env was scrubbed.
from app.core.config import get_settings  # noqa: E402

get_settings.cache_clear()


@pytest.fixture
def settings():
    from app.core.config import Settings

    # Env keys are scrubbed to empty at module load (overriding any .env), so a
    # plain Settings() already resolves to fully-offline values.
    return Settings(llm_provider="echo")


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c
