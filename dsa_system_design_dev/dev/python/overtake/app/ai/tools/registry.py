"""Tool registry + tool schema/permissions.

A minimal internal tool registry. Each tool carries a JSON-schema-style
parameter description and a permission flag. MCP note: MCP is an *integration
protocol*, not a replacement for this registry — MCP client wrappers would
register their remote tools here (and, per the MCP spec, sensitive tool
invocations should support human-in-the-loop denial).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    """A callable tool with schema + permission metadata."""

    name: str
    description: str
    parameters: dict[str, Any]
    func: Callable[..., Any]
    requires_approval: bool = False

    def schema(self) -> dict[str, Any]:
        """Return an OpenAI-style function-tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def __call__(self, **kwargs: Any) -> Any:
        return self.func(**kwargs)


class ToolRegistry:
    """Registry of named tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> Tool:
        self._tools[tool.name] = tool
        return tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def names(self) -> list[str]:
        return list(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schema() for t in self._tools.values()]


_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Return the shared tool registry (populated by builtins import)."""
    # Import for side effect of registration; guarded against cycles.
    from app.ai.tools import builtins as _  # noqa: F401

    return _registry


# Internal handle used by builtins to register without triggering get_registry.
def _raw_registry() -> ToolRegistry:
    return _registry
