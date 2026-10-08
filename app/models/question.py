"""Question model."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class Question:
    question_id: str
    question_type: str  # multiple_choice | numeric | short_answer
    prompt: str
    maximum_score: Decimal
    correct_answer: Any = None
    accepted_answers: list = field(default_factory=list)
    tolerance: Decimal = Decimal("0")
    keywords: list = field(default_factory=list)
    partial_credit_rules: dict = field(default_factory=dict)
