"""SA-01..SA-05 short answer tests."""
from decimal import Decimal

from app.services.grading_service import clear_audit_log, grade_submission
from tests.conftest import make_submission


def setup_function(_):
    clear_audit_log()


def test_sa01_exact_gives_full(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q3 = next(r for r in result.question_results if r.question_id == "Q3")
    assert q3.status == "correct"
    assert q3.awarded_score == Decimal("10.00")


def test_sa02_keywords_partial(assessment):
    ans = "Chlorophyll captures SUNLIGHT and uses carbon dioxide"
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": ans})
    result = grade_submission(assessment, sub)
    q3 = next(r for r in result.question_results if r.question_id == "Q3")
    assert q3.status in ("correct", "partially_correct")
    assert q3.awarded_score > Decimal("0.00")


def test_sa03_insufficient_keywords_zero(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "plants are green"})
    result = grade_submission(assessment, sub)
    q3 = next(r for r in result.question_results if r.question_id == "Q3")
    assert q3.status == "incorrect"
    assert q3.awarded_score == Decimal("0.00")


def test_sa04_case_normalization(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "  PhotoSynthesis  "})
    result = grade_submission(assessment, sub)
    q3 = next(r for r in result.question_results if r.question_id == "Q3")
    assert q3.status == "correct"


def test_sa05_empty_unanswered(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "   "})
    result = grade_submission(assessment, sub)
    q3 = next(r for r in result.question_results if r.question_id == "Q3")
    assert q3.status == "unanswered"
