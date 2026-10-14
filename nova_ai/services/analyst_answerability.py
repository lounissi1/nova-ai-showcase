# ─────────────────────────────────────────────────────────────────────────────
# Nova AI · showcase excerpt
# Source: nova_ai/services/analyst_answerability.py (private repository)
# Excerpt: the deterministic check that runs before any model is asked anything.
# © Apex Intelligence. Shown for demonstration only; all rights reserved.
# ─────────────────────────────────────────────────────────────────────────────

"""Single deterministic answerability classifier shared by Ask AI and Nova SKI."""

from __future__ import annotations

import re
from typing import Any

ANSWERABLE_FROM_DATA = "answerable_from_data"
PARTIALLY_ANSWERABLE = "partially_answerable"
GENERAL_SUGGESTION_AVAILABLE = "general_suggestion_available"
NOT_ANSWERABLE_SAFELY = "not_answerable_safely"
NEEDS_MAPPING = "needs_mapping"
NEEDS_MORE_HISTORY = "needs_more_history"
NEEDS_CONNECTOR_VALIDATION = "needs_connector_validation"

_FORECAST = re.compile(r"\b(forecast|predict|projection|next (?:week|month|year)|years?)\b", re.I)
_VISUAL = re.compile(r"\b(chart|graph|visuali[sz](?:e|ation)?|plot|donut|histogram|dashboard widget)\b", re.I)
_QUALITY = re.compile(r"\b(quality|mapping|missing|rejected|reject rate|trust|readiness|improve(?: in)? (?:this|the) source)\b", re.I)
_UNSAFE = re.compile(r"\b(sql|raw rows?|passwords?|credentials?|api key|secret|token|execute|database access)\b", re.I)
_CONNECTOR = re.compile(r"\b(connector|sync|connection|webhook)\b", re.I)
_GENERAL = re.compile(r"\b(ideas?|best practices?|strategy|recommend|suggest|what should (?:i|we)|marketing|business improvement)\b", re.I)
_KNOWN = re.compile(r"\b(revenue|profit|margin|cost|orders?|items?|customers?|category|product|region|source|dataset)\b", re.I)
_UNKNOWN = re.compile(r"\b(churn|conversion|inventory|ad spend|lifetime value|ltv|retention)\b", re.I)


# ... ASK_AI_INTENTS (18 intents) and classify_ask_ai_intent() omitted ...


def evaluate_answerability(question: str, context: dict[str, Any]) -> dict[str, Any]:
    """Classify from question intent plus deterministic context availability."""
    q = (question or "").strip()
    has_data = bool((context.get("workspace_summary") or {}).get("metrics", {}).get("metric_days"))
    sources = context.get("sources") or []
    has_profile = any((source.get("profile") or {}).get("columns") for source in sources)
    has_mapping = any(source.get("mapped_metrics") for source in sources)
    forecast = context.get("forecast_availability") or {}

    if _UNSAFE.search(q):
        status, missing = NOT_ANSWERABLE_SAFELY, "A safe aggregated metric or profile field (raw access is not permitted)."
    elif _FORECAST.search(q):
        status = ANSWERABLE_FROM_DATA if forecast.get("available") else NEEDS_MORE_HISTORY
        missing = None if forecast.get("available") else forecast.get("reason_if_unavailable")
    elif _CONNECTOR.search(q):
        status = ANSWERABLE_FROM_DATA if sources else NEEDS_CONNECTOR_VALIDATION
        missing = None if sources else "A connected source with a recorded sync status."
    elif _VISUAL.search(q):
        status, missing = GENERAL_SUGGESTION_AVAILABLE, None
    elif _QUALITY.search(q):
        status = ANSWERABLE_FROM_DATA if sources else GENERAL_SUGGESTION_AVAILABLE
        missing = None
    elif _UNKNOWN.search(q) and _KNOWN.search(q):
        status, missing = PARTIALLY_ANSWERABLE, "The requested unmapped metric (for example churn, conversion, or retention)."
    elif _UNKNOWN.search(q):
        status = NEEDS_MAPPING if has_profile and not has_mapping else NOT_ANSWERABLE_SAFELY
        missing = "A mapped source column for the requested metric."
    elif _GENERAL.search(q):
        status, missing = GENERAL_SUGGESTION_AVAILABLE, None
    elif _KNOWN.search(q) and (has_data or has_profile):
        status, missing = ANSWERABLE_FROM_DATA, None
    elif _KNOWN.search(q):
        status, missing = NEEDS_MAPPING, "A connected source and canonical metric mapping."
    else:
        status, missing = GENERAL_SUGGESTION_AVAILABLE, None
    return {"status": status, "missing_requirement": missing}

# ... build_ski_analyst_questions() and answer_mode_for() omitted ...
