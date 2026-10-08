"""Regression: golden reference cases must stay stable across refactoring."""

from decimal import Decimal

from app.services.grading_service import clear_audit_log, grade_submission
from tests.conftest import make_submission


def setup_function(_):
    clear_audit_log()


def test_regression_golden_full_marks(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"}, sid="GOLD1")
    result = grade_submission(assessment, sub)
    assert result.raw_score == Decimal("25.00")
    assert result.final_score == Decimal("25.00")
    assert result.percentage == Decimal("100.00")


def test_regression_golden_partial_late(assessment):
    sub = make_submission(
        assessment,
        {"Q1": "A", "Q2": 10.4, "Q3": "plants are green"},
        late_hours=10,
        sid="GOLD2",
    )
    result = grade_submission(assessment, sub)
    # Q1 0 + Q2 5.00 + Q3 0 = 5.00 raw, 10% penalty = 0.50 -> 4.50
    assert result.raw_score == Decimal("5.00")
    assert result.penalty == Decimal("0.50")
    assert result.final_score == Decimal("4.50")
