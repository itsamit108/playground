"""Guardrails — PII detection, prompt-injection detection, output checks.

Basic, dependency-free real implementations suitable as a first line of defense
and as the integration point for richer safety frameworks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CC_RE = re.compile(r"\b(?:\d[ -]?){13,16}\b")

_INJECTION_PATTERNS = [
    re.compile(r"ignore (?:all |the )?(?:previous|prior|above) instructions", re.IGNORECASE),
    re.compile(r"disregard (?:all |the )?(?:previous|prior) (?:instructions|prompts)", re.IGNORECASE),
    re.compile(r"you are now (?:a |an )?", re.IGNORECASE),
    re.compile(r"reveal (?:your )?(?:system )?prompt", re.IGNORECASE),
    re.compile(r"developer mode", re.IGNORECASE),
]


@dataclass
class GuardrailResult:
    allowed: bool
    findings: list[str] = field(default_factory=list)
    sanitized: str | None = None


def detect_pii(text: str) -> list[str]:
    findings: list[str] = []
    if _EMAIL_RE.search(text):
        findings.append("email")
    if _SSN_RE.search(text):
        findings.append("ssn")
    if _CC_RE.search(text):
        findings.append("credit_card")
    if _PHONE_RE.search(text):
        findings.append("phone")
    return findings


def redact_pii(text: str) -> str:
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = _SSN_RE.sub("[REDACTED_SSN]", text)
    text = _CC_RE.sub("[REDACTED_CC]", text)
    text = _PHONE_RE.sub("[REDACTED_PHONE]", text)
    return text


def detect_prompt_injection(text: str) -> bool:
    return any(p.search(text) for p in _INJECTION_PATTERNS)


def check_input(text: str) -> GuardrailResult:
    """Inbound guardrail: block prompt injection, flag (don't block) PII."""
    findings: list[str] = []
    if detect_prompt_injection(text):
        return GuardrailResult(allowed=False, findings=["prompt_injection"])
    pii = detect_pii(text)
    findings.extend(f"pii:{p}" for p in pii)
    return GuardrailResult(allowed=True, findings=findings)


def check_output(text: str) -> GuardrailResult:
    """Outbound guardrail: redact any PII that slipped into the response."""
    pii = detect_pii(text)
    if pii:
        return GuardrailResult(
            allowed=True,
            findings=[f"pii:{p}" for p in pii],
            sanitized=redact_pii(text),
        )
    return GuardrailResult(allowed=True, sanitized=text)
