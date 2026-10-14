# ─────────────────────────────────────────────────────────────────────────────
# Nova AI · showcase excerpt
# Source: nova_ai/services/llm_output_sanitizer.py (private repository)
# Complete module, unchanged.
# © Apex Intelligence. Shown for demonstration only; all rights reserved.
# ─────────────────────────────────────────────────────────────────────────────

"""Shared mechanical sanitizer for LLM narration displayed or persisted by Nova.

The sanitizer is deliberately deterministic.  It never decides whether a claim
is plausible: it removes unsafe output shapes and permits a numeric token only
when that exact token occurs in the freshly rendered deterministic context.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


UNVERIFIED_FIGURE = "[unverified figure removed]"
UNSAFE_CONTENT = "[unsafe generated content removed]"

_NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?%?")
_FENCED_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>()]+", re.IGNORECASE)
_SECRET_ASSIGNMENT_RE = re.compile(
    r"\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret)\b"
    r"\s*(?:=|:|is)\s*[^\s,;]+",
    re.IGNORECASE,
)
_SECRET_VALUE_RE = re.compile(
    r"\b(?:Bearer\s+[A-Za-z0-9._~+/-]{8,}|sk-[A-Za-z0-9_-]{8,})\b",
    re.IGNORECASE,
)
_SOURCE_CONFIG_RE = re.compile(
    r"(?im)^.*\b(?:source_config|connection_config|credentials?)\b\s*[:=]\s*.*$"
)
_EXECUTABLE_SQL_LINE_RE = re.compile(
    r"(?im)^[ \t]*(?:[-*]\s*)?(?:`+)?"
    r"(?:SELECT\s+.+\s+FROM\b|INSERT\s+INTO\b|UPDATE\s+\S+\s+SET\b|"
    r"DELETE\s+FROM\b|DROP\s+(?:TABLE|DATABASE|SCHEMA)\b|"
    r"ALTER\s+TABLE\b|CREATE\s+(?:TABLE|DATABASE|SCHEMA)\b|"
    r"TRUNCATE\s+TABLE\b|EXEC(?:UTE)?\s+\S+).*$"
)


@dataclass(frozen=True)
class SanitizedLLMOutput:
    """Sanitized narration and mechanical event labels for audit metadata."""

    text: str
    events: tuple[str, ...]


def sanitize_llm_output(text: str, deterministic_context: str) -> SanitizedLLMOutput:
    """Remove unsafe shapes and ungrounded numbers from generated narration."""
    cleaned = str(text or "")
    events: list[str] = []

    rules = (
        ("code_fence_removed", _FENCED_BLOCK_RE),
        ("executable_sql_removed", _EXECUTABLE_SQL_LINE_RE),
        ("url_removed", _URL_RE),
        ("secret_removed", _SECRET_ASSIGNMENT_RE),
        ("secret_removed", _SECRET_VALUE_RE),
        ("source_config_removed", _SOURCE_CONFIG_RE),
    )
    for label, pattern in rules:
        cleaned, count = pattern.subn(UNSAFE_CONTENT, cleaned)
        events.extend([label] * count)

    allowed_numbers = set(_NUMBER_RE.findall(str(deterministic_context or "")))

    def numeric_key(token: str) -> tuple[str, str]:
        is_percent = token.endswith("%")
        raw = token[:-1] if is_percent else token
        try:
            value = Decimal(raw.replace(",", ""))
            return ("percent" if is_percent else "number", format(value.normalize(), "f"))
        except InvalidOperation:
            return ("literal", token)

    allowed_numeric_keys = {numeric_key(token) for token in allowed_numbers}

    def replace_number(match: re.Match[str]) -> str:
        token = match.group(0)
        if token in allowed_numbers or numeric_key(token) in allowed_numeric_keys:
            return token
        events.append("unverified_numeric_claim_removed")
        return UNVERIFIED_FIGURE

    cleaned = _NUMBER_RE.sub(replace_number, cleaned)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned).strip()
    return SanitizedLLMOutput(text=cleaned, events=tuple(events))
