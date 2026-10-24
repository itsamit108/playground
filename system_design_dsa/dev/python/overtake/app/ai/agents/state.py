"""Agent / run state dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class ToolCall:
    """A record of one tool invocation during an agent run."""

    name: str
    arguments: dict[str, Any]
    result: Any = None


@dataclass
class AgentState:
    """Mutable state threaded through an agent run."""

    user_id: int
    task: str
    status: RunStatus = RunStatus.PENDING
    steps: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    answer: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def log(self, step: str) -> None:
        self.steps.append(step)
