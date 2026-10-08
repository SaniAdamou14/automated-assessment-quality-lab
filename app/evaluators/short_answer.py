"""Short-answer evaluator with explicit normalization and keyword rules."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.models.result import QuestionResult


def normalize_text(value) -> str:
    return str(value).strip().lower()


def _quant(value: Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ShortAnswerEvaluator:
    def evaluate(self, question, answer) -> QuestionResult:
        max_score = _quant(Decimal(str(question.maximum_score)))
        if answer is None or normalize_text(answer) == "":
            return QuestionResult(
                question_id=question.question_id,
                awarded_score=Decimal("0.00"),
                maximum_score=max_score,
                status="unanswered",
                feedback_code="unanswered",
            )
        normalized = normalize_text(answer)
        accepted = [normalize_text(a) for a in (question.accepted_answers or [])]
        if normalized in accepted:
            return QuestionResult(
                question_id=question.question_id,
                awarded_score=max_score,
                maximum_score=max_score,
                status="correct",
                feedback_code="sa_correct",
            )
        return self._keyword_score(question, normalized, max_score)

    def _keyword_score(self, question, normalized: str, max_score: Decimal) -> QuestionResult:
        keywords = [normalize_text(k) for k in (question.keywords or [])]
        if not keywords:
            return self._incorrect(question, max_score)
        matched = sum(1 for kw in keywords if kw and kw in normalized)
        rules = question.partial_credit_rules or {}
        full_hit = self._full_keyword_hit(question, matched, len(keywords), max_score, rules)
        if full_hit is not None:
            return full_hit
        partial_hit = self._partial_keyword_hit(question, matched, len(keywords), max_score, rules)
        if partial_hit is not None:
            return partial_hit
        return self._incorrect(question, max_score)

    def _full_keyword_hit(
        self, question, matched: int, total: int, max_score: Decimal, rules: dict
    ) -> QuestionResult | None:
        if matched < total:
            return None
        full_fraction = Decimal(str(rules.get("full_fraction", "1.0")))
        awarded = _quant(max_score * full_fraction)
        status = "correct" if full_fraction >= Decimal("1.0") else "partially_correct"
        return QuestionResult(
            question_id=question.question_id,
            awarded_score=awarded,
            maximum_score=max_score,
            status=status,
            feedback_code="sa_keywords_full",
        )

    def _partial_keyword_hit(
        self, question, matched: int, total: int, max_score: Decimal, rules: dict
    ) -> QuestionResult | None:
        required = int(rules.get("min_keywords", total))
        partial_fraction = Decimal(str(rules.get("partial_fraction", "0.5")))
        if matched < required or required <= 0:
            return None
        awarded = _quant(max_score * partial_fraction)
        return QuestionResult(
            question_id=question.question_id,
            awarded_score=awarded,
            maximum_score=max_score,
            status="partially_correct",
            feedback_code="sa_keywords_partial",
        )

    def _incorrect(self, question, max_score: Decimal) -> QuestionResult:
        return QuestionResult(
            question_id=question.question_id,
            awarded_score=Decimal("0.00"),
            maximum_score=max_score,
            status="incorrect",
            feedback_code="sa_incorrect",
        )
