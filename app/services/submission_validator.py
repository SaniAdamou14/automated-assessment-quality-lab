"""Baseline submission validator (exists but grading_service re-implements checks inline)."""
from __future__ import annotations


def validate_submission_basic(assessment, submission) -> bool:
    if submission.assessment_id != assessment.assessment_id:
        return False
    if submission.assessment_version != assessment.version:
        return False
    return True
