"""Guardrails: PII detection, prompt-injection checks, output validation.

Real, basic, dependency-free implementations. These run on the input before it
reaches the model and on the output before it is returned.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\b(?:\+?\d[\d\-\s]{7,}\d)\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CC_RE = re.compile(r"\b(?:\d[ -]?){13,16}\b")

_INJECTION_PATTERNS = [
    re.compile(r"ignore (?:all |the )?(?:previous|prior|above) instructions", re.I),
    re.compile(r"disregard (?:all |the )?(?:previous|prior|above)", re.I),
    re.compile(r"you are now", re.I),
    re.compile(r"reveal (?:your )?(?:system )?prompt", re.I),
    re.compile(r"developer mode", re.I),
]


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str | None = None
    sanitized: str | None = None


def detect_pii(text: str) -> list[str]:
    """Return a list of PII types found in the text."""
    found: list[str] = []
    if _EMAIL_RE.search(text):
        found.append("email")
    if _SSN_RE.search(text):
        found.append("ssn")
    if _CC_RE.search(text):
        found.append("credit_card")
    if _PHONE_RE.search(text):
        found.append("phone")
    return found


def redact_pii(text: str) -> str:
    """Redact detected PII from text."""
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = _SSN_RE.sub("[REDACTED_SSN]", text)
    text = _CC_RE.sub("[REDACTED_CC]", text)
    text = _PHONE_RE.sub("[REDACTED_PHONE]", text)
    return text


def detect_prompt_injection(text: str) -> bool:
    """Return True if the text looks like a prompt-injection attempt."""
    return any(pattern.search(text) for pattern in _INJECTION_PATTERNS)


def check_input(text: str) -> GuardrailResult:
    """Validate user input. Blocks prompt injection; redacts PII."""
    if detect_prompt_injection(text):
        return GuardrailResult(allowed=False, reason="prompt_injection_detected")
    sanitized = redact_pii(text)
    return GuardrailResult(allowed=True, sanitized=sanitized)


def check_output(text: str, *, max_chars: int = 8000) -> GuardrailResult:
    """Validate model output. Redacts PII and enforces a length cap."""
    sanitized = redact_pii(text)[:max_chars]
    return GuardrailResult(allowed=True, sanitized=sanitized)
