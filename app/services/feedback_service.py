"""Baseline feedback helper (grading_service builds feedback inline instead)."""
from __future__ import annotations


def build_feedback(status: str) -> str:
    if status == "correct":
        return "Correct."
    if status == "partially_correct":
        return "Partially correct."
    if status == "unanswered":
        return "No answer provided."
    return "Incorrect. Please review the material."
