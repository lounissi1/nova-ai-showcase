# ─────────────────────────────────────────────────────────────────────────────
# Nova AI · showcase excerpt
# Source: tests/test_phase63_4_verified_metric_sanitizer.py (private repository)
# Complete test module, unchanged.
# © Apex Intelligence. Shown for demonstration only; all rights reserved.
# ─────────────────────────────────────────────────────────────────────────────

"""Phase 63.4 verified metric preservation and invented-claim blocking."""

from nova_ai.services.llm_output_sanitizer import (
    UNVERIFIED_FIGURE,
    UNSAFE_CONTENT,
    sanitize_llm_output,
)


def test_verified_numbers_survive_formatting_variations():
    context = (
        "Total revenue: 1,250.00; margin: 25.0%; trust score: 88; quality score: 92; "
        "rejected records: 3; range: 2026-01-01 to 2026-04-01; data points: 90; horizon: 90_day"
    )
    text = "Revenue 1250.0, margin 25%, trust 88.0, quality 92, rejects 3, dates 2026-01-01 to 2026-04-01, 90 points."
    result = sanitize_llm_output(text, context)
    assert result.text == text
    assert UNVERIFIED_FIGURE not in result.text


def test_invented_numbers_and_secret_shapes_are_blocked():
    context = "Verified total: 1250."
    text = "Verified 1,250.00; invented 77%; api_key=sk-supersecret\nsource_config: {'password':'bad'}"
    result = sanitize_llm_output(text, context)
    assert "1,250.00" in result.text
    assert "77%" not in result.text and UNVERIFIED_FIGURE in result.text
    assert "supersecret" not in result.text and "password" not in result.text
    assert UNSAFE_CONTENT in result.text


def test_percent_and_plain_number_are_not_interchangeable():
    result = sanitize_llm_output("Growth is 25%.", "Order count: 25")
    assert "25%" not in result.text
