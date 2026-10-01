"""Concrete agent workflow: the Ops Assistant.

A single-agent plan/act/respond workflow that can answer questions about the
host system by calling the ``get_system_specs`` / ``summarize_specs`` tools, then
asking the LLM to phrase the answer. Works fully offline with the EchoProvider.
"""

from __future__ import annotations

from app.ai.agents.base import BaseAgent
from app.ai.agents.state import AgentState, ToolCall
from app.ai.models.base import make_message
from app.ai.prompts.loader import load_prompt

# Keywords that indicate the user is asking about the host/system.
_SPEC_KEYWORDS = (
    "spec", "system", "cpu", "memory", "ram", "disk", "gpu",
    "os", "machine", "resource", "hardware", "usage",
)


class OpsAssistantAgent(BaseAgent):
    """Answers operational questions, using system-spec tools when relevant."""

    async def plan(self, state: AgentState) -> None:
        objective = state.objective.lower()
        if any(keyword in objective for keyword in _SPEC_KEYWORDS):
            state.log("plan: question is about system specs -> use summarize_specs tool")
            state.steps.append("use_tool:summarize_specs")
        else:
            state.log("plan: general question -> answer directly with the LLM")

    async def act(self, state: AgentState) -> None:
        if "use_tool:summarize_specs" in state.steps:
            result = self.tools.call("summarize_specs")
            state.tool_calls.append(
                ToolCall(name="summarize_specs", arguments={}, result=result)
            )
            state.log("act: called summarize_specs")

    async def respond(self, state: AgentState) -> str:
        system_prompt = load_prompt("system")

        context_lines = []
        for call in state.tool_calls:
            context_lines.append(f"[tool:{call.name}] {call.result}")
        context = "\n".join(context_lines)

        user_content = state.objective
        if context:
            user_content = f"{state.objective}\n\nTool results:\n{context}"

        messages = [
            make_message("system", system_prompt),
            make_message("user", user_content),
        ]
        result = await self.llm.generate(messages, tools=self.tools.schemas())
        return result["content"]
