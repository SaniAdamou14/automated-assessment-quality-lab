"""Scoring policy: pure aggregation of question results (Decimal)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def _quant(value: Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ScoringPolicy:
    version = "v1"

    def aggregate(self, question_results) -> Decimal:
        total = sum((r.awarded_score for r in question_results), Decimal("0.00"))
        return _quant(total)

    def percentage(self, final_score: Decimal, maximum_score: Decimal) -> Decimal:
        maximum = Decimal(str(maximum_score))
        if maximum <= Decimal("0"):
            return Decimal("0.00")
        pct = Decimal(str(final_score)) / maximum * Decimal("100")
        return _quant(pct)

    def is_passing(self, percentage: Decimal, threshold: Decimal) -> bool:
        return Decimal(str(percentage)) >= Decimal(str(threshold))
