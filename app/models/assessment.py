"""Assessment model."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Assessment:
    assessment_id: str
    version: str
    questions: list
    maximum_score: Decimal
    passing_score: Decimal  # percentage threshold, e.g. Decimal("60")
    late_penalty_percent: Decimal = Decimal("0")
    scoring_policy_version: str = "v1"
    max_attempts: int = 3
