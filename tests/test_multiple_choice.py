"""MC-01..MC-05 multiple choice tests."""
from decimal import Decimal

from app.services.grading_service import clear_audit_log, grade_submission
from tests.conftest import make_submission


def setup_function(_):
    clear_audit_log()


def test_mc01_correct_gives_full_score(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q1 = next(r for r in result.question_results if r.question_id == "Q1")
    assert q1.awarded_score == Decimal("5.00")
    assert q1.status == "correct"


def test_mc02_incorrect_gives_zero(assessment):
    sub = make_submission(assessment, {"Q1": "A", "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q1 = next(r for r in result.question_results if r.question_id == "Q1")
    assert q1.awarded_score == Decimal("0.00")
    assert q1.status == "incorrect"


def test_mc03_unanswered_status(assessment):
    sub = make_submission(assessment, {"Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q1 = next(r for r in result.question_results if r.question_id == "Q1")
    assert q1.status == "unanswered"
    assert q1.awarded_score == Decimal("0.00")


def test_mc04_whitespace_handled(assessment):
    sub = make_submission(assessment, {"Q1": "  B  ", "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q1 = next(r for r in result.question_results if r.question_id == "Q1")
    assert q1.status == "correct"


def test_mc05_invalid_type_rejected_or_zero(assessment):
    # list answer should not crash grading; treated as incorrect/invalid deterministically
    sub = make_submission(assessment, {"Q1": ["B"], "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q1 = next(r for r in result.question_results if r.question_id == "Q1")
    assert q1.awarded_score == Decimal("0.00")
    assert q1.status in ("incorrect", "invalid", "unanswered")
