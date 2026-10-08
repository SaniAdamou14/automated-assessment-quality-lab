"""Shared fixtures for assessment engine tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.models.assessment import Assessment
from app.models.question import Question
from app.models.submission import Submission


def make_assessment() -> Assessment:
    q1 = Question(
        question_id="Q1",
        question_type="multiple_choice",
        prompt="What is 2+2?",
        maximum_score=Decimal("5"),
        correct_answer="B",
    )
    q2 = Question(
        question_id="Q2",
        question_type="numeric",
        prompt="Value of pi*? use 10.0",
        maximum_score=Decimal("10"),
        correct_answer=Decimal("10.0"),
        tolerance=Decimal("0.1"),
        partial_credit_rules={"partial_tolerance": Decimal("0.5"), "partial_fraction": 0.5},
    )
    q3 = Question(
        question_id="Q3",
        question_type="short_answer",
        prompt="Explain photosynthesis",
        maximum_score=Decimal("10"),
        accepted_answers=["photosynthesis"],
        keywords=["chlorophyll", "sunlight", "carbon"],
        partial_credit_rules={"min_keywords": 2, "partial_fraction": 0.5, "full_fraction": 1.0},
    )
    return Assessment(
        assessment_id="A1",
        version="1.0",
        questions=[q1, q2, q3],
        maximum_score=Decimal("25"),
        passing_score=Decimal("60"),
        scoring_policy_version="v1",
        max_attempts=3,
    )


def make_submission(assessment, answers, late_hours=0, attempt=1, sid="S1"):
    deadline = datetime(2026, 10, 1, 12, 0, 0)
    submitted = deadline + timedelta(hours=late_hours)
    return Submission(
        submission_id=sid,
        assessment_id=assessment.assessment_id,
        assessment_version=assessment.version,
        student_id="STU-001",
        answers=answers,
        submitted_at=submitted,
        deadline=deadline,
        attempt_number=attempt,
        max_attempts=3,
    )


@pytest.fixture
def assessment():
    return make_assessment()
