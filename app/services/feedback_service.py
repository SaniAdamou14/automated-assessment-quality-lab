"""Feedback generation mapped from result statuses (no answer disclosure)."""

from __future__ import annotations


def build_feedback(status: str) -> str:
    mapping = {
        "correct": "Correct.",
        "partially_correct": "Partially correct.",
        "unanswered": "No answer provided.",
        "incorrect": "Incorrect. Please review the material.",
        "invalid": "Invalid answer format. Please check the expected type.",
    }
    return mapping.get(status, "Incorrect. Please review the material.")


def build_summary_feedback(passed: bool, correct: int, partial: int, total: int) -> str:
    if passed and correct == total:
        return "Excellent work. All answers correct."
    if passed:
        return f"Passed with {correct} correct and {partial} partially correct."
    if partial > 0:
        return f"Not passed. {partial} partially correct, keep practicing."
    return "Not passed. Please review the material and retry."
