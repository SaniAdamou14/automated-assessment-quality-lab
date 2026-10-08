"""Result models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class QuestionResult:
    question_id: str
    awarded_score: Decimal
    maximum_score: Decimal
    status: str  # correct | partially_correct | incorrect | unanswered | invalid
    feedback_code: str = ""


@dataclass
class GradingResult:
    submission_id: str
    raw_score: Decimal
    penalty: Decimal
    final_score: Decimal
    percentage: Decimal
    passed: bool
    question_results: list
    feedback: str
    assessment_version: str
    scoring_policy_version: str
    graded_at: datetime = None
