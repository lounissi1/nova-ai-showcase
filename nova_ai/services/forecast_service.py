# ─────────────────────────────────────────────────────────────────────────────
# Nova AI · showcase excerpt
# Source: nova_ai/services/forecast_service.py (private repository)
# Excerpt: horizon rules, method selection and residual-based confidence bands.
# © Apex Intelligence. Shown for demonstration only; all rights reserved.
# ─────────────────────────────────────────────────────────────────────────────

"""Deterministic, horizon-gated forecasting for Nova's aggregated revenue series.

Exactly two named methods exist:

* ``seasonal_naive`` repeats the last complete season only when at least two
  complete seasons exist at the selected aggregation (52 weekly or 12 monthly
  periods).
* ``linear_trend`` is the least-squares fallback for every other eligible
  series, including annual long-term output.

Availability, method selection, residual confidence bands, API output, and AI
context metadata all originate here. No LLM produces forecast numbers.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Iterable




HORIZON_90_DAY = "90_day"
HORIZON_1_YEAR = "1_year"
HORIZON_LONG_TERM = "long_term"
SUPPORTED_HORIZONS = (HORIZON_90_DAY, HORIZON_1_YEAR, HORIZON_LONG_TERM)

# Source-history freshness is disclosed separately and never changes forecast
# availability, method selection, values, or residual-derived confidence.
STALENESS_THRESHOLD_DAYS = 14

_RULES = {
    HORIZON_90_DAY: {"aggregation": "week", "minimum": 8, "periods": 13, "season": 52},
    HORIZON_1_YEAR: {"aggregation": "month", "minimum": 24, "periods": 12, "season": 12},
    HORIZON_LONG_TERM: {"aggregation": "year", "minimum": 3, "periods": 3, "season": None},
}

# ... date helpers and aggregate_series() omitted ...


def _least_squares(values: list[float]) -> tuple[float, float, list[float]]:
    n = len(values)
    mean_x = (n - 1) / 2
    mean_y = sum(values) / n
    denominator = sum((index - mean_x) ** 2 for index in range(n))
    slope = (
        sum((index - mean_x) * (value - mean_y) for index, value in enumerate(values))
        / denominator
        if denominator
        else 0.0
    )
    intercept = mean_y - slope * mean_x
    fitted = [intercept + slope * index for index in range(n)]
    return slope, intercept, fitted


def _residual_error(values: list[float], fitted: list[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum((actual - expected) ** 2 for actual, expected in zip(values, fitted)) / len(values))

# ... _unavailable_metadata() omitted ...


def build_forecast(points: Iterable[dict[str, Any]], horizon: str = HORIZON_90_DAY) -> dict[str, Any]:
    """Return separated actual/forecast series and the canonical metadata contract."""
    if horizon not in _RULES:
        horizon = HORIZON_90_DAY
    point_list = list(points)
    source_dates = [_as_date(point["date"]) for point in point_list if point.get("date") is not None]
    last_synced = max(source_dates) if source_dates else None
    rule = _RULES[horizon]
    aggregation = str(rule["aggregation"])
    series = aggregate_series(point_list, aggregation)
    minimum = int(rule["minimum"])
    if len(series) < minimum:
        return {
            "actual": series,
            "forecast": [],
            "metadata": _unavailable_metadata(
                horizon=horizon, aggregation=aggregation, minimum=minimum, series=series,
                last_synced=last_synced,
            ),
        }

    values = [float(point["revenue"]) for point in series]
    season = rule["season"]
    if season and len(values) >= int(season) * 2:
        method = "seasonal_naive"
        season_length = int(season)
        fitted = values[:season_length] + [
            values[index - season_length] for index in range(season_length, len(values))
        ]
        residual_values = values[season_length:]
        residual_fitted = fitted[season_length:]
        future_values = [values[-season_length + (index % season_length)] for index in range(int(rule["periods"]))]
    else:
        method = "linear_trend"
        slope, intercept, fitted = _least_squares(values)
        residual_values = values
        residual_fitted = fitted
        future_values = [intercept + slope * (len(values) + index) for index in range(int(rule["periods"]))]

    residual_error = _residual_error(residual_values, residual_fitted)
    next_date = _next_period(_as_date(series[-1]["date"]), aggregation)
    forecast = []
    for value in future_values:
        safe_value = max(0.0, value)
        forecast.append({
            "date": next_date.isoformat(),
            "revenue": round(safe_value, 2),
            "confidence_lower": round(max(0.0, safe_value - 1.96 * residual_error), 2),
            "confidence_upper": round(max(0.0, safe_value + 1.96 * residual_error), 2),
            "isForecast": True,
        })
        next_date = _next_period(next_date, aggregation)
    # ... horizon labelling, metadata contract and limitations omitted ...
    return {"actual": series, "forecast": forecast, "metadata": {"method": method}}
