"""Validator tests."""

import pytest

from app.exceptions import (
    AssessmentNotFoundError,
    AssessmentVersionError,
    MaximumAttemptsExceededError,
    UnknownQuestionError,
)
from app.services.grading_service import clear_audit_log, grade_submission
from tests.conftest import make_submission


def setup_function(_):
    clear_audit_log()


def test_rejects_wrong_assessment_id(assessment):
    sub = make_submission(assessment, {"Q1": "B"})
    sub.assessment_id = "WRONG"
    with pytest.raises(AssessmentNotFoundError):
        grade_submission(assessment, sub)


def test_rejects_wrong_version(assessment):
    sub = make_submission(assessment, {"Q1": "B"})
    sub.assessment_version = "9.9"
    with pytest.raises(AssessmentVersionError):
        grade_submission(assessment, sub)


def test_rejects_too_many_attempts(assessment):
    sub = make_submission(assessment, {"Q1": "B"}, attempt=99)
    with pytest.raises(MaximumAttemptsExceededError):
        grade_submission(assessment, sub)


def test_rejects_too_many_answers(assessment):
    answers = {"Q1": "B", "Q2": 10.0, "Q3": "x", "QX": "extra", "QY": "extra2", "QZ": "e"}
    sub = make_submission(assessment, answers)
    with pytest.raises(UnknownQuestionError):
        grade_submission(assessment, sub)
