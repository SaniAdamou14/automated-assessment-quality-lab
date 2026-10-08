"""Numeric evaluator using Decimal only (no float)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.models.result import QuestionResult


def _quant(value: Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as err:
        raise ValueError("invalid numeric input") from err


def _partial_credit(question, diff: Decimal, max_score: Decimal) -> QuestionResult | None:
    rules = question.partial_credit_rules or {}
    if "partial_tolerance" not in rules:
        return None
    partial_tol = _to_decimal(rules["partial_tolerance"])
    if diff > partial_tol:
        return None
    fraction = Decimal(str(rules.get("partial_fraction", "0.5")))
    awarded = _quant(max_score * fraction)
    if awarded > max_score:
        awarded = max_score
    return QuestionResult(
        question_id=question.question_id,
        awarded_score=awarded,
        maximum_score=max_score,
        status="partially_correct",
        feedback_code="num_partial",
    )


class NumericEvaluator:
    def evaluate(self, question, answer) -> QuestionResult:
        max_score = _quant(Decimal(str(question.maximum_score)))
        if answer is None or (isinstance(answer, str) and answer.strip() == ""):
            return QuestionResult(
                question_id=question.question_id,
                awarded_score=Decimal("0.00"),
                maximum_score=max_score,
                status="unanswered",
                feedback_code="unanswered",
            )
        parsed = self._parse_inputs(question, answer, max_score)
        if parsed is None:
            return QuestionResult(
                question_id=question.question_id,
                awarded_score=Decimal("0.00"),
                maximum_score=max_score,
                status="invalid",
                feedback_code="num_invalid",
            )
        submitted, correct, tolerance = parsed
        diff = abs(submitted - correct)
        if diff <= tolerance:
            return QuestionResult(
                question_id=question.question_id,
                awarded_score=max_score,
                maximum_score=max_score,
                status="correct",
                feedback_code="num_correct",
            )
        partial = _partial_credit(question, diff, max_score)
        if partial is not None:
            return partial
        return QuestionResult(
            question_id=question.question_id,
            awarded_score=Decimal("0.00"),
            maximum_score=max_score,
            status="incorrect",
            feedback_code="num_incorrect",
        )

    def _parse_inputs(self, question, answer, max_score):
        try:
            submitted = _to_decimal(answer)
            correct = _to_decimal(question.correct_answer)
            tolerance = _to_decimal(question.tolerance)
        except ValueError:
            return None
        return (submitted, correct, tolerance)
