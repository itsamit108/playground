"""Agent / run state dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A single tool invocation within an agent run."""

    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)
    result: Any = None


@dataclass
class AgentState:
    """Mutable state carried through an agent run."""

    goal: str
    steps: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    final_answer: str | None = None

    def record_step(self, description: str) -> None:
        self.steps.append(description)

    def record_tool_call(self, call: ToolCall) -> None:
        self.tool_calls.append(call)
