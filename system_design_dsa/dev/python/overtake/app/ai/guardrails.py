"""Guardrails: real (basic) input/output safety checks.

- PII detection + redaction (emails, phone numbers, SSN-like, credit-card-like).
- Prompt-injection heuristics (classic override phrases).
- Output validation (block empty / overly long responses).

These are intentionally lightweight, deterministic, and dependency-free so they
run offline. Swap for a dedicated guardrails library in production.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CC = re.compile(r"\b(?:\d[ -]?){13,16}\b")

_INJECTION_PATTERNS = [
    re.compile(r"ignore (all |the )?(previous|prior|above) instructions", re.I),
    re.compile(r"disregard (all |the )?(previous|prior) (instructions|prompts)", re.I),
    re.compile(r"you are now (a |an )?\w+", re.I),
    re.compile(r"reveal (your |the )?(system )?prompt", re.I),
    re.compile(r"(act|pretend) as (if you are |a |an )", re.I),
]

_MAX_OUTPUT_CHARS = 20_000


@dataclass
class GuardrailResult:
    """Outcome of a guardrail check."""

    ok: bool
    text: str
    reason: str | None = None


def redact_pii(text: str) -> str:
    """Replace detected PII with typed placeholders."""
    text = _EMAIL.sub("[REDACTED_EMAIL]", text)
    text = _SSN.sub("[REDACTED_SSN]", text)
    text = _CC.sub("[REDACTED_CARD]", text)
    text = _PHONE.sub("[REDACTED_PHONE]", text)
    return text


def detect_prompt_injection(text: str) -> bool:
    """Return True if the text looks like a prompt-injection attempt."""
    return any(p.search(text) for p in _INJECTION_PATTERNS)


def check_input(text: str) -> GuardrailResult:
    """Validate and sanitise user input before it reaches the model."""
    if not text or not text.strip():
        return GuardrailResult(ok=False, text=text, reason="empty input")
    if detect_prompt_injection(text):
        return GuardrailResult(
            ok=False, text=text, reason="possible prompt injection"
        )
    return GuardrailResult(ok=True, text=redact_pii(text))


def check_output(text: str) -> GuardrailResult:
    """Validate model output before returning it to the caller."""
    if not text or not text.strip():
        return GuardrailResult(ok=False, text=text, reason="empty output")
    if len(text) > _MAX_OUTPUT_CHARS:
        return GuardrailResult(
            ok=True, text=text[:_MAX_OUTPUT_CHARS], reason="truncated"
        )
    return GuardrailResult(ok=True, text=redact_pii(text))
