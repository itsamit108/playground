"""Shared pytest fixtures. Forces offline mode (no API keys) for all tests."""

from __future__ import annotations

import os

import pytest

# Ensure tests never accidentally hit a real provider.
os.environ.pop("GOOGLE_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)
os.environ.pop("LLAMA_CLOUD_API_KEY", None)
os.environ["LLM_PROVIDER"] = "echo"


@pytest.fixture
def settings():
    from app.core.config import Settings

    return Settings(_env_file=None, llm_provider="echo")


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c
