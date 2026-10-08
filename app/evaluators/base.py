"""Evaluator interface."""

from __future__ import annotations

from typing import Protocol


class QuestionEvaluator(Protocol):
    def evaluate(self, question, answer) -> object: ...
