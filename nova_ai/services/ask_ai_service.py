# ─────────────────────────────────────────────────────────────────────────────
# Nova AI · showcase excerpt
# Source: nova_ai/services/ask_ai_service.py (private repository, ~1,100 lines)
# Excerpt: the hard rules and the shape of one Ask-AI turn. Context building,
# answer templates, prompts and the provider call are omitted.
# © Apex Intelligence. Shown for demonstration only; all rights reserved.
# ─────────────────────────────────────────────────────────────────────────────

"""
Ask AI grounding service.

Builds a compact, trusted context from Nova's deterministic revenue/quality
metrics and answers natural-language questions grounded in that context.

Hard rules enforced here:
* NEVER execute model-generated SQL.
* NEVER send raw records / full datasets to the LLM — only compact summaries.
* Workspace-scoped and ownership-checked; no cross-workspace data.
* Honest behavior: insufficient data, disabled AI, and deterministic fallback
  are all clearly labeled — no fabricated demo product answers.
"""

from typing import Any, Dict, List, Optional

from nova_ai.services.ai_data_context_service import build_ai_data_context
from nova_ai.services.analyst_answerability import (
    answer_mode_for,
    classify_ask_ai_intent,
    evaluate_answerability,
)
from nova_ai.services.llm_output_sanitizer import sanitize_llm_output
from nova_ai.services.llm_provider import get_llm_provider


async def answer_question(
    db,
    current_user,
    question: str,
    *,
    workspace_id: Optional[str] = None,
    source_id: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """One Ask-AI turn, freshly grounded on every call."""

    # 1. Trusted context: deterministic metrics, data quality, forecast availability.
    #    Scoped to the caller's workspace; raw rows never leave the database.
    context = await build_ai_data_context(db, current_user, workspace_id=workspace_id, source_id=source_id)

    # 2. Decide before asking a model: can this be answered safely from the data?
    decision = evaluate_answerability(question, context)
    intent = classify_ask_ai_intent(question)
    mode = answer_mode_for(decision["status"], question)

    # 3. A deterministic answer always exists, so the feature works with AI switched off.
    answer, limitations, charts, kpis = _deterministic_analyst_answer(
        mode, question, context, decision.get("missing_requirement")
    )

    # 4. Optional narration by the configured LLM, then mechanical sanitising:
    #    unsafe shapes are removed and any number not in the context is replaced.
    provider = get_llm_provider()
    if provider.is_configured() and mode not in {"cannot_answer_safely", "general_suggestion"}:
        prompt_context = ...  # compact grounded context, history and limits omitted
        result = await provider.explain_metrics(question, prompt_context)
        answer = sanitize_llm_output(str(result["text"]), context["rendered_text"]).text

    # 5. The UI always receives the evidence and the limitations with the answer.
    return {
        "answer": answer,
        "answerability": decision,
        "intent": intent,
        "limitations": limitations,
        "suggested_charts": charts,
        "suggested_kpis": kpis,
        # ... trust score, grounding sources, forecast metadata ...
    }
