"""Factory resolves the right provider; auto falls back to echo offline."""

from app.ai.models.factory import get_llm_client
from app.ai.models.providers import BedrockProvider, EchoProvider
from app.core.config import Settings


async def test_factory_echo_forced():
    client = await get_llm_client(Settings(llm_provider="echo"))
    assert isinstance(client, EchoProvider)


async def test_factory_bedrock_forced():
    client = await get_llm_client(Settings(llm_provider="bedrock"))
    assert isinstance(client, BedrockProvider)


async def test_factory_auto_falls_back_to_echo(monkeypatch):
    async def _unreachable(self):
        return False

    monkeypatch.setattr(BedrockProvider, "is_reachable", _unreachable)
    client = await get_llm_client(Settings(llm_provider="auto"))
    assert isinstance(client, EchoProvider)
