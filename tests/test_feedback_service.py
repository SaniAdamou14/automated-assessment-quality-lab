"""Feedback tests."""
from app.services.feedback_service import build_feedback
from app.services.grading_service import clear_audit_log, grade_submission
from tests.conftest import make_submission


def setup_function(_):
    clear_audit_log()


def test_feedback_helper_correct():
    assert "Correct" in build_feedback("correct")


def test_feedback_helper_partial():
    assert "Partially" in build_feedback("partially_correct")


def test_feedback_end_to_end_pass(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    assert "Passed" in result.feedback or "Excellent" in result.feedback


def test_feedback_end_to_end_fail(assessment):
    sub = make_submission(assessment, {"Q1": "wrong", "Q2": 999, "Q3": "wrong"})
    result = grade_submission(assessment, sub)
    assert "Not passed" in result.feedback
