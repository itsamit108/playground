"""Interactive Rich CLI — a thin client over the service/provider layer.

Preserves the original chatbot UX (Rich TUI + slash commands /help /reset
/model /models /system /quit) but now calls into ``app.services`` and
``app.ai`` rather than its own boto3 code. Runs offline via the EchoProvider
when LocalStack/Bedrock is not reachable.

Entry point: ``chatbot = "scripts.chat_cli:main"`` in pyproject.toml.
"""

from __future__ import annotations

import asyncio
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme

from app.ai.models.factory import get_llm_client
from app.ai.tools.builtins import list_models
from app.core.config import get_settings
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService

custom_theme = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "user_prompt": "bold bright_white",
    }
)
console = Console(theme=custom_theme)

BANNER = r"""
[bold cyan]╔══════════════════════════════════════════════╗
║   🤖  LocalStack Bedrock GenAI Chatbot  🤖   ║
╚══════════════════════════════════════════════╝[/bold cyan]
"""

HELP_TEXT = """
[info]Commands:[/info]
  [bold]/help[/bold]    – Show this help message
  [bold]/reset[/bold]   – Clear conversation history
  [bold]/model[/bold]   – Show current model info
  [bold]/models[/bold]  – List available foundation models
  [bold]/system[/bold]  – Show the system prompt
  [bold]/quit[/bold]    – Exit the chatbot  (also: Ctrl+C)
"""

SESSION_ID = "cli"


def _print_help() -> None:
    console.print(HELP_TEXT)


def _print_models(settings) -> None:
    try:
        models = list_models(settings)
        console.print(f"\n[info]Available foundation models ({len(models)}):[/info]")
        for m in models[:20]:
            console.print(
                f"  • [bold]{m['modelId']}[/bold]  "
                f"({m['providerName']} / {m['modelName']})"
            )
        if len(models) > 20:
            console.print(f"  … and {len(models) - 20} more")
    except Exception as exc:  # noqa: BLE001
        console.print(f"[error]Failed to list models:[/error] {exc}")


def _handle_command(cmd: str, service: ChatService, settings) -> bool:
    if cmd in ("/quit", "/exit", "/q"):
        console.print("[success]Goodbye! 👋[/success]")
        sys.exit(0)
    if cmd == "/help":
        _print_help()
        return True
    if cmd == "/reset":
        service.reset(SESSION_ID)
        console.print("[warning]Conversation history cleared.[/warning]")
        return True
    if cmd == "/model":
        console.print(f"[info]Current model:[/info] {settings.bedrock_model_id}")
        return True
    if cmd == "/models":
        _print_models(settings)
        return True
    if cmd == "/system":
        console.print(f"[info]System prompt:[/info] {settings.system_prompt}")
        return True
    return False


async def _send(service: ChatService, text: str) -> None:
    with console.status("[cyan]Thinking…[/cyan]", spinner="dots"):
        try:
            resp = await service.chat(
                ChatRequest(message=text, session_id=SESSION_ID)
            )
        except Exception as exc:  # noqa: BLE001
            console.print(f"\n[error]Error:[/error] {exc}")
            return
    console.print()
    console.print(
        Panel(
            Markdown(resp.reply),
            title=f"🤖 Assistant  (turn {resp.turn}, provider {resp.provider})",
            border_style="green",
            padding=(1, 2),
        )
    )


async def _run() -> None:
    settings = get_settings()
    llm = await get_llm_client(settings)
    service = ChatService(llm=llm, settings=settings)

    console.print(BANNER)
    console.print(
        Panel(
            f"[info]Model:[/info]  {settings.bedrock_model_id}\n"
            f"[info]Provider:[/info] {getattr(llm, 'name', '?')}\n"
            f"[info]System:[/info] {settings.system_prompt[:80]}",
            title="Session Info",
            border_style="cyan",
        )
    )
    _print_help()

    while True:
        try:
            user_input = console.input("\n[user_prompt]You ❯ [/user_prompt]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[success]Goodbye! 👋[/success]")
            return

        if not user_input:
            continue
        if user_input.startswith("/") and _handle_command(
            user_input.lower(), service, settings
        ):
            continue
        await _send(service, user_input)


def main() -> None:
    """Console-script entry point."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
