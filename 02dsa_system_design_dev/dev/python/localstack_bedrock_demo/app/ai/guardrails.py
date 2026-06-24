"""Basic guardrails: PII redaction, prompt-injection + output checks.

These are deliberately simple, dependency-free implementations so they run
offline. Swap for Presidio / LLM-based classifiers in production.
"""

from __future__ import annotations

import re

from app.core.exceptions import GuardrailError

_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE = re.compile(r"\b(?:\+?\d{1,2}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous",
    "disregard the above",
    "you are now",
    "reveal your system prompt",
    "print your instructions",
)


def redact_pii(text: str) -> str:
    """Redact emails, phone numbers, and SSNs from text."""
    text = _EMAIL.sub("[REDACTED_EMAIL]", text)
    text = _SSN.sub("[REDACTED_SSN]", text)
    text = _PHONE.sub("[REDACTED_PHONE]", text)
    return text


def detect_prompt_injection(text: str) -> bool:
    """Return True if the text looks like a prompt-injection attempt."""
    lowered = text.lower()
    return any(p in lowered for p in _INJECTION_PATTERNS)


def check_input(text: str) -> str:
    """Validate + sanitise user input. Raises GuardrailError on injection."""
    if detect_prompt_injection(text):
        raise GuardrailError("Potential prompt-injection detected in input.")
    return redact_pii(text)


def check_output(text: str) -> str:
    """Redact any PII that may have leaked into model output."""
    return redact_pii(text)
