"""Unit tests for the model layer (EchoProvider + factory)."""

from __future__ import annotations

import pytest

from app.ai.models.base import LLMClient
from app.ai.models.factory import get_llm_client
from app.ai.models.providers import EchoProvider


def test_echo_provider_conforms_to_protocol():
    assert isinstance(EchoProvider(), LLMClient)


@pytest.mark.asyncio
async def test_echo_provider_generates_deterministically():
    provider = EchoProvider()
    out1 = await provider.generate([{"role": "user", "content": "hello"}])
    out2 = await provider.generate([{"role": "user", "content": "hello"}])
    assert out1["content"] == out2["content"]
    assert "hello" in out1["content"]
    assert out1["provider"] == "echo"


@pytest.mark.asyncio
async def test_echo_provider_produces_valid_xhtml_for_epub():
    from lxml import etree

    provider = EchoProvider()
    out = await provider.generate(
        [
            {"role": "system", "content": "Produce XHTML for EPUB3."},
            {"role": "user", "content": "Page 1\nSome text"},
        ]
    )
    wrapped = f"<root>{out['content']}</root>"
    # Should parse without raising.
    etree.fromstring(wrapped.encode("utf-8"))


def test_factory_defaults_to_echo_without_key(settings):
    client = get_llm_client(settings)
    assert getattr(client, "name", None) == "echo"
