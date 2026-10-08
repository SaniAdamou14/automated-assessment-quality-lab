"""PEN-01..PEN-06 penalty tests."""

from decimal import Decimal

import pytest

from app.exceptions import LateSubmissionRejectedError
from app.services.grading_service import clear_audit_log, grade_submission
from tests.conftest import make_submission


def setup_function(_):
    clear_audit_log()


def base_answers():
    return {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"}


def test_pen01_ontime_no_penalty(assessment):
    sub = make_submission(assessment, base_answers(), late_hours=0)
    result = grade_submission(assessment, sub)
    assert result.penalty == Decimal("0.00")
    assert result.raw_score == Decimal("25.00")
    assert result.final_score == Decimal("25.00")


def test_pen02_late_24h_10pct(assessment):
    sub = make_submission(assessment, base_answers(), late_hours=10)
    result = grade_submission(assessment, sub)
    assert result.penalty == Decimal("2.50")
    assert result.final_score == Decimal("22.50")


def test_pen03_late_72h_25pct(assessment):
    sub = make_submission(assessment, base_answers(), late_hours=48)
    result = grade_submission(assessment, sub)
    assert result.penalty == Decimal("6.25")
    assert result.final_score == Decimal("18.75")


def test_pen04_too_late_rejected(assessment):
    sub = make_submission(assessment, base_answers(), late_hours=80)
    with pytest.raises(LateSubmissionRejectedError):
        grade_submission(assessment, sub)


def test_pen05_never_negative(assessment):
    sub = make_submission(assessment, {"Q1": "wrong", "Q2": 999, "Q3": "wrong"}, late_hours=48)
    result = grade_submission(assessment, sub)
    assert result.final_score >= Decimal("0.00")


def test_pen06_applied_once(assessment):
    sub = make_submission(assessment, base_answers(), late_hours=10)
    r1 = grade_submission(assessment, sub)
    # penalty must equal 10% of raw, not compounded
    assert r1.penalty == (r1.raw_score * Decimal("0.10")).quantize(Decimal("0.01"))
