"""Agent/run state dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A record of a single tool invocation during a run."""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    result: Any = None


@dataclass
class AgentState:
    """Mutable state for one agent run."""

    objective: str
    steps: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    answer: str | None = None

    def log(self, step: str) -> None:
        self.steps.append(step)
