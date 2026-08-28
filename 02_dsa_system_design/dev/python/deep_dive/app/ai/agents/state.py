"""Agent / run state dataclasses.

A minimal, framework-agnostic state model. This is the slot for LangGraph state
graphs or OpenAI Agents SDK run state if/when the project adopts them.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StepStatus(str, Enum):
    OK = "ok"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class StepRecord:
    name: str
    status: StepStatus = StepStatus.OK
    detail: str = ""
    started_at: float = field(default_factory=time.time)


@dataclass
class RunState:
    """Mutable state threaded through an agent workflow."""

    goal: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    scratch: dict[str, Any] = field(default_factory=dict)
    steps: list[StepRecord] = field(default_factory=list)
    output: dict[str, Any] = field(default_factory=dict)
    failed: bool = False

    def record(self, name: str, *, status: StepStatus = StepStatus.OK, detail: str = "") -> None:
        self.steps.append(StepRecord(name=name, status=status, detail=detail))
        if status is StepStatus.ERROR:
            self.failed = True
