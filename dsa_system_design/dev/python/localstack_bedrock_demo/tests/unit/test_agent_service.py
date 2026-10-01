"""Agent service: tool-using workflow runs offline."""

from app.ai.models.providers import EchoProvider
from app.core.config import Settings
from app.schemas.agents import AgentRunRequest
from app.services.agent_service import AgentService


def _service() -> AgentService:
    return AgentService(llm=EchoProvider(), settings=Settings(llm_provider="echo"))


async def test_agent_calls_list_models_tool():
    service = _service()
    resp = await service.run(AgentRunRequest(goal="list available models"))
    assert any(c.tool == "list_models" for c in resp.tool_calls)
    assert "ollama.llama3.2" in resp.answer or "echo-1" in resp.answer


async def test_agent_lists_tools():
    service = _service()
    names = {t["name"] for t in service.available_tools()}
    assert {"list_models", "echo"} <= names
