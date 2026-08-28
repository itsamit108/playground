"""Tool registry.

A minimal internal tool registry holding callable function tools, their JSON
schemas, and a permission flag (human-in-the-loop denial capability, per the
MCP tool spec). MCP is an *integration protocol* that would plug in here as an
additional source of tools -- it does not replace this internal registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    """A registered function tool."""

    name: str
    description: str
    func: Callable[..., Any]
    parameters: dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = False

    def schema(self) -> dict[str, Any]:
        """Return an OpenAI-style function-tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters or {"type": "object", "properties": {}},
            },
        }


class ToolRegistry:
    """In-process registry of callable tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def tool(
        self,
        name: str,
        description: str,
        *,
        parameters: dict[str, Any] | None = None,
        requires_approval: bool = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a function as a tool."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.register(
                Tool(
                    name=name,
                    description=description,
                    func=func,
                    parameters=parameters or {"type": "object", "properties": {}},
                    requires_approval=requires_approval,
                )
            )
            return func

        return decorator

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def names(self) -> list[str]:
        return sorted(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]

    def call(self, name: str, *, approved: bool = True, **kwargs: Any) -> Any:
        """Invoke a tool, honoring its approval requirement."""
        tool = self.get(name)
        if tool.requires_approval and not approved:
            raise PermissionError(f"Tool '{name}' requires human approval")
        return tool.func(**kwargs)


# Global registry instance populated by builtins.
registry = ToolRegistry()
