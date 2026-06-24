"""Concrete agent workflow: the Notes Organizer agent.

A single-agent plan/act/respond workflow that uses the `search_notes` tool to
gather relevant notes, then asks the LLM to summarize or organize them. Runs
fully offline with the EchoProvider.
"""

from __future__ import annotations

from app.ai.agents.base import BaseAgent
from app.ai.agents.state import AgentState, ToolCall
from app.ai.models.base import LLMClient, msg
from app.ai.prompts.loader import system_prompt
from app.ai.tools.registry import get_registry


class NotesOrganizerAgent(BaseAgent):
    """Summarizes / organizes a user's notes using the search_notes tool."""

    def __init__(self, llm: LLMClient, *, top_k: int = 6) -> None:
        super().__init__(llm)
        self._top_k = top_k

    async def plan(self, state: AgentState) -> None:
        state.log(f"Plan: search notes relevant to task: {state.task!r}")

    async def act(self, state: AgentState) -> None:
        tool = get_registry().get("search_notes")
        args = {"user_id": state.user_id, "query": state.task, "top_k": self._top_k}
        results = tool(**args)
        state.tool_calls.append(
            ToolCall(name="search_notes", arguments=args, result=results)
        )
        state.metadata["retrieved"] = results
        state.log(f"Act: retrieved {len(results)} note snippet(s)")

    async def respond(self, state: AgentState) -> None:
        results = state.metadata.get("retrieved", [])
        if not results:
            state.answer = "I could not find any notes related to that task."
            state.log("Respond: no context available")
            return

        context = "\n".join(
            f"- ({r['note_title']}) {r['snippet']}" for r in results
        )
        messages = [
            msg("system", f"{system_prompt()}\n\nContext:\n{context}"),
            msg("user", state.task),
        ]
        out = await self.llm.generate(messages, temperature=0.2)
        state.answer = out.get("content", "")
        state.log("Respond: generated organized summary")
