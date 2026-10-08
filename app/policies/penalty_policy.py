"""Late-penalty policy with named constants and versioning."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.exceptions import LateSubmissionRejectedError

ON_TIME_LIMIT_SECONDS = 0
FIRST_TIER_LIMIT_SECONDS = 24 * 3600
SECOND_TIER_LIMIT_SECONDS = 72 * 3600
FIRST_TIER_RATE = Decimal("0.10")
SECOND_TIER_RATE = Decimal("0.25")

POLICY_VERSION = "v1"


def _quant(value: Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class PenaltyPolicy:
    version = POLICY_VERSION

    def rate_for_delay(self, delay_seconds: float) -> Decimal:
        if delay_seconds <= ON_TIME_LIMIT_SECONDS:
            return Decimal("0")
        if delay_seconds <= FIRST_TIER_LIMIT_SECONDS:
            return FIRST_TIER_RATE
        if delay_seconds <= SECOND_TIER_LIMIT_SECONDS:
            return SECOND_TIER_RATE
        raise LateSubmissionRejectedError("submission too late")

    def calculate(self, raw_score: Decimal, delay_seconds: float) -> Decimal:
        rate = self.rate_for_delay(delay_seconds)
        penalty = _quant(Decimal(str(raw_score)) * rate)
        return penalty

    def apply(self, raw_score: Decimal, delay_seconds: float) -> Decimal:
        penalty = self.calculate(raw_score, delay_seconds)
        final_score = _quant(Decimal(str(raw_score)) - penalty)
        if final_score < Decimal("0.00"):
            return Decimal("0.00")
        return final_score
