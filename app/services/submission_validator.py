"""Submission validation with specific domain exceptions."""

from __future__ import annotations

from app.exceptions import (
    AssessmentNotFoundError,
    AssessmentVersionError,
    MaximumAttemptsExceededError,
    UnknownQuestionError,
)


def validate_submission(assessment, submission) -> None:
    """Raise specific errors if submission is invalid; return None when valid."""
    if submission.assessment_id != assessment.assessment_id:
        raise AssessmentNotFoundError("assessment mismatch")
    if submission.assessment_version != assessment.version:
        raise AssessmentVersionError("version mismatch")
    if submission.attempt_number > submission.max_attempts:
        raise MaximumAttemptsExceededError("too many attempts")
    if submission.attempt_number > assessment.max_attempts:
        raise MaximumAttemptsExceededError("too many attempts")
    if len(submission.answers) > len(assessment.questions):
        raise UnknownQuestionError("too many answers")
    known = {q.question_id for q in assessment.questions}
    for qid in submission.answers:
        if qid not in known:
            raise UnknownQuestionError(f"unknown question: {qid}")
