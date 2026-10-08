"""Improved grading orchestrator: validation, strategy evaluators, policies, audit."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.evaluators.multiple_choice import MultipleChoiceEvaluator
from app.evaluators.numeric import NumericEvaluator
from app.evaluators.short_answer import ShortAnswerEvaluator
from app.exceptions import UnknownQuestionError
from app.models.result import GradingResult, QuestionResult
from app.policies.penalty_policy import PenaltyPolicy
from app.policies.scoring_policy import ScoringPolicy
from app.repositories.audit_repository import AuditRepository, canonical_input_hash
from app.services.feedback_service import build_summary_feedback
from app.services.submission_validator import validate_submission

_EVALUATORS = {
    "multiple_choice": MultipleChoiceEvaluator(),
    "numeric": NumericEvaluator(),
    "short_answer": ShortAnswerEvaluator(),
}

_audit_repository = AuditRepository()


def get_audit_repository() -> AuditRepository:
    return _audit_repository


def _evaluator_for(question_type: str):
    evaluator = _EVALUATORS.get(question_type)
    if evaluator is None:
        raise UnknownQuestionError(f"unknown question type: {question_type}")
    return evaluator


def grade_submission(
    assessment,
    submission,
    scoring_policy: ScoringPolicy | None = None,
    penalty_policy: PenaltyPolicy | None = None,
    audit_repository: AuditRepository | None = None,
) -> GradingResult:
    validate_submission(assessment, submission)
    scoring = scoring_policy or ScoringPolicy()
    penalties = penalty_policy or PenaltyPolicy()
    audits = audit_repository or _audit_repository

    results: list[QuestionResult] = []
    for question in assessment.questions:
        answer = submission.answers.get(question.question_id)
        evaluator = _evaluator_for(question.question_type)
        results.append(evaluator.evaluate(question, answer))

    raw_score = scoring.aggregate(results)
    delay = (submission.submitted_at - submission.deadline).total_seconds()
    penalty = penalties.calculate(raw_score, delay)
    final_score = penalties.apply(raw_score, delay)
    percentage = scoring.percentage(final_score, Decimal(str(assessment.maximum_score)))
    passed = scoring.is_passing(percentage, Decimal(str(assessment.passing_score)))

    correct = sum(1 for r in results if r.status == "correct")
    partial = sum(1 for r in results if r.status == "partially_correct")
    feedback = build_summary_feedback(passed, correct, partial, len(results))

    audits.record_grading(
        submission_id=submission.submission_id,
        assessment_id=assessment.assessment_id,
        assessment_version=assessment.version,
        scoring_policy_version=assessment.scoring_policy_version,
        input_hash=canonical_input_hash(submission.answers),
        final_score=str(final_score),
        result_status="passed" if passed else "failed",
    )
    return GradingResult(
        submission_id=submission.submission_id,
        raw_score=raw_score,
        penalty=penalty,
        final_score=final_score,
        percentage=percentage,
        passed=passed,
        question_results=results,
        feedback=feedback,
        assessment_version=assessment.version,
        scoring_policy_version=assessment.scoring_policy_version,
        graded_at=datetime.utcnow(),
    )


def get_audit_log() -> list:
    return _audit_repository.all()


def clear_audit_log() -> None:
    _audit_repository.clear()
