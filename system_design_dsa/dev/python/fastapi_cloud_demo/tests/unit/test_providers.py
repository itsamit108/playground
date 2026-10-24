"""Unit tests for LLM providers and the factory."""

from __future__ import annotations

import pytest

from app.ai.models.base import LLMClient, make_message
from app.ai.models.factory import get_llm_client
from app.ai.models.providers import EchoProvider
from app.core.config import Settings


@pytest.mark.asyncio
async def test_echo_provider_echoes_last_user_message():
    provider = EchoProvider()
    result = await provider.generate([make_message("user", "ping")])
    assert result["content"] == "Echo: ping"
    assert result["provider"] == "echo"


def test_echo_provider_satisfies_protocol():
    assert isinstance(EchoProvider(), LLMClient)


def test_factory_defaults_to_echo():
    client = get_llm_client(Settings())
    assert isinstance(client, EchoProvider)


def test_factory_openai_without_key_falls_back_to_echo():
    client = get_llm_client(Settings(llm_provider="openai", openai_api_key=None))
    assert isinstance(client, EchoProvider)
