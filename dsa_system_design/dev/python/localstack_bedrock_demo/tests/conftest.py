"""Shared test fixtures. All tests run offline (EchoProvider) with no keys."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(llm_provider="echo", api_key=None)


@pytest.fixture
def client(monkeypatch) -> TestClient:
    # Force the offline provider so tests never touch LocalStack/Bedrock.
    monkeypatch.setenv("LLM_PROVIDER", "echo")
    from app.core import config as config_module

    config_module.get_settings.cache_clear()
    app = create_app()
    return TestClient(app)
