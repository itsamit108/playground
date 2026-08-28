"""Concrete agent workflow(s).

``ModelInfoAgent`` is a real, runnable tool-using agent: when the user's goal
mentions models, it calls the ``list_models`` tool and then asks the LLM to
summarise the result. Works fully offline (EchoProvider + offline tool list).
"""

from __future__ import annotations

from app.ai.agents.base import BaseAgent
from app.ai.agents.state import AgentState, ToolCall


class ModelInfoAgent(BaseAgent):
    """Single agent that answers questions about available models via a tool."""

    async def plan(self, state: AgentState) -> list[str]:
        goal = state.goal.lower()
        plan = ["Interpret the user's goal."]
        if any(k in goal for k in ("model", "models", "list", "available")):
            plan.append("Call the list_models tool.")
        plan.append("Summarise findings into a final answer.")
        return plan

    async def act(self, state: AgentState) -> None:
        goal = state.goal.lower()
        if any(k in goal for k in ("model", "models", "list", "available")):
            tool = self.tools.get("list_models")
            result = tool()
            state.record_tool_call(ToolCall(tool="list_models", result=result))

    async def respond(self, state: AgentState) -> str:
        tool_summary_lines: list[str] = []
        for call in state.tool_calls:
            if call.tool == "list_models" and isinstance(call.result, list):
                ids = ", ".join(m["modelId"] for m in call.result)
                tool_summary_lines.append(f"Available models: {ids}")

        context = "\n".join(tool_summary_lines) if tool_summary_lines else ""
        prompt = (
            f"User goal: {state.goal}\n"
            f"{context}\n"
            "Answer the user's goal using the information above."
        )
        result = await self.llm.generate(
            messages=[{"role": "user", "content": prompt}],
        )
        answer = result["text"]
        # Ensure tool findings are always surfaced even with the EchoProvider.
        if context and context not in answer:
            answer = f"{answer}\n\n{context}"
        return answer
