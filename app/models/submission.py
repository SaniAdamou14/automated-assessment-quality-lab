"""Submission model."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Submission:
    submission_id: str
    assessment_id: str
    assessment_version: str
    student_id: str
    answers: dict
    submitted_at: datetime
    deadline: datetime
    attempt_number: int = 1
    max_attempts: int = 3
