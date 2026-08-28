"""Tool registry + schema/permissions.

A minimal internal tool registry. MCP note: MCP is an *integration protocol* —
external MCP tools would be registered here too (wrapped as ``Tool``), not used
to replace this registry. Per the MCP spec, tool invocations should support
human-in-the-loop denial; ``requires_approval`` models that here.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Tool:
    """A callable tool with a JSON-schema-ish parameter description."""

    name: str
    description: str
    func: Callable[..., Any]
    parameters: dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = False

    def schema(self) -> dict[str, Any]:
        """Return the tool's invocation schema (provider-neutral)."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "requires_approval": self.requires_approval,
        }

    def __call__(self, **kwargs: Any) -> Any:
        return self.func(**kwargs)


class ToolRegistry:
    """Holds tools and exposes lookup + schema listing."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def names(self) -> list[str]:
        return list(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schema() for t in self._tools.values()]
