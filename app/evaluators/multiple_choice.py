"""Multiple-choice evaluator (pure, Decimal, low complexity)."""

from __future__ import annotations

from decimal import Decimal

from app.models.result import QuestionResult


def _quant(value: Decimal) -> Decimal:
    from decimal import ROUND_HALF_UP

    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class MultipleChoiceEvaluator:
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
        submitted = str(answer).strip()
        expected = str(question.correct_answer).strip()
        if submitted == expected:
            return QuestionResult(
                question_id=question.question_id,
                awarded_score=max_score,
                maximum_score=max_score,
                status="correct",
                feedback_code="mc_correct",
            )
        return QuestionResult(
            question_id=question.question_id,
            awarded_score=Decimal("0.00"),
            maximum_score=max_score,
            status="incorrect",
            feedback_code="mc_incorrect",
        )
