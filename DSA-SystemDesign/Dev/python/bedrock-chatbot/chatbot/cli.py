"""Interactive CLI entry-point for the Bedrock chatbot."""

from __future__ import annotations

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme

from chatbot.client import get_bedrock_client
from chatbot.config import BEDROCK_MODEL_ID, SYSTEM_PROMPT
from chatbot.conversation import Conversation

# ── theme ───────────────────────────────────────────────────────
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

# ── banner ──────────────────────────────────────────────────────
BANNER = r"""
[bold cyan]╔══════════════════════════════════════════════╗
║   🤖  LocalStack Bedrock CLI Chatbot  🤖    ║
╚══════════════════════════════════════════════╝[/bold cyan]
"""

HELP_TEXT = """
[info]Commands:[/info]
  [bold]/help[/bold]    – Show this help message
  [bold]/reset[/bold]   – Clear conversation history
  [bold]/model[/bold]   – Show current model info
  [bold]/models[/bold]  – List available foundation models
  [bold]/system[/bold]  – Show / change the system prompt
  [bold]/quit[/bold]    – Exit the chatbot  (also: Ctrl+C)
"""


def _print_help() -> None:
    console.print(HELP_TEXT)


def _print_models() -> None:
    """List foundation models from the Bedrock control-plane."""
    try:
        client = get_bedrock_client()
        resp = client.list_foundation_models()
        models = resp.get("modelSummaries", [])
        if not models:
            console.print("[warning]No foundation models returned.[/warning]")
            return
        console.print(f"\n[info]Available foundation models ({len(models)}):[/info]")
        for m in models[:20]:  # show first 20
            mid = m.get("modelId", "?")
            name = m.get("modelName", "?")
            provider = m.get("providerName", "?")
            console.print(f"  • [bold]{mid}[/bold]  ({provider} / {name})")
        if len(models) > 20:
            console.print(f"  … and {len(models) - 20} more")
    except Exception as exc:
        console.print(f"[error]Failed to list models:[/error] {exc}")


def _handle_command(cmd: str, convo: Conversation) -> bool:
    """Handle slash commands. Return True if the command was recognised."""
    if cmd in ("/quit", "/exit", "/q"):
        console.print("[success]Goodbye! 👋[/success]")
        sys.exit(0)
    if cmd == "/help":
        _print_help()
        return True
    if cmd == "/reset":
        convo.reset()
        console.print("[warning]Conversation history cleared.[/warning]")
        return True
    if cmd == "/model":
        console.print(f"[info]Current model:[/info] {convo.model_id}")
        return True
    if cmd == "/models":
        _print_models()
        return True
    if cmd == "/system":
        console.print(f"[info]System prompt:[/info] {convo.system_prompt}")
        return True
    return False


def _send_message(user_input: str, convo: Conversation) -> None:
    """Send a user message to Bedrock and print the reply."""
    with console.status("[cyan]Thinking…[/cyan]", spinner="dots"):
        try:
            reply = convo.send(user_input)
        except Exception as exc:
            console.print(f"\n[error]Error:[/error] {exc}")
            console.print(
                "[warning]Tip: Make sure LocalStack is running "
                "(docker compose up -d) and the Bedrock engine "
                "is ready.[/warning]"
            )
            if convo.messages and convo.messages[-1]["role"] == "user":
                convo.messages.pop()
            return

    console.print()
    console.print(
        Panel(
            Markdown(reply),
            title=f"🤖 Assistant  (turn {convo.turn_count})",
            border_style="green",
            padding=(1, 2),
        )
    )


def _print_banner() -> None:
    """Print the startup banner and session info."""
    sys_preview = SYSTEM_PROMPT[:80]
    ellipsis = "…" if len(SYSTEM_PROMPT) > 80 else ""
    console.print(BANNER)
    console.print(
        Panel(
            f"[info]Model:[/info]  {BEDROCK_MODEL_ID}\n"
            f"[info]System:[/info] {sys_preview}{ellipsis}",
            title="Session Info",
            border_style="cyan",
        )
    )
    _print_help()


def main() -> None:
    """Run the interactive chatbot loop."""
    _print_banner()
    convo = Conversation()

    while True:
        try:
            user_input = console.input("\n[user_prompt]You ❯ [/user_prompt]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[success]Goodbye! 👋[/success]")
            sys.exit(0)

        if not user_input:
            continue

        if user_input.startswith("/"):
            if _handle_command(user_input.lower(), convo):
                continue

        _send_message(user_input, convo)


if __name__ == "__main__":
    main()
