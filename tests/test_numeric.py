"""NUM-01..NUM-06 numeric tests."""
from decimal import Decimal

from app.services.grading_service import clear_audit_log, grade_submission
from tests.conftest import make_submission


def setup_function(_):
    clear_audit_log()


def test_num01_exact_answer(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q2 = next(r for r in result.question_results if r.question_id == "Q2")
    assert q2.status == "correct"
    assert q2.awarded_score == Decimal("10.00")


def test_num02_inside_tolerance(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.05, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q2 = next(r for r in result.question_results if r.question_id == "Q2")
    assert q2.status == "correct"


def test_num03_outside_tolerance(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 20.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q2 = next(r for r in result.question_results if r.question_id == "Q2")
    assert q2.status == "incorrect"
    assert q2.awarded_score == Decimal("0.00")


def test_num04_partial_range(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.4, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q2 = next(r for r in result.question_results if r.question_id == "Q2")
    assert q2.status == "partially_correct"
    assert q2.awarded_score == Decimal("5.00")


def test_num05_invalid_input(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": "not-a-number", "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q2 = next(r for r in result.question_results if r.question_id == "Q2")
    assert q2.status == "invalid"


def test_num06_decimal_precision(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": "10.05", "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    assert result.raw_score.as_tuple().exponent == -2
    assert result.final_score.as_tuple().exponent == -2
