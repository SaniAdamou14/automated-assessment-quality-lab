"""Baseline automated assessment grading service (monolithic, intentionally hard to maintain).

This version is functionally correct but concentrates validation, evaluation
for three question types, partial credit, late penalties, feedback and audit
in a single function. It is used to demonstrate cyclomatic complexity,
maintainability and inspection findings before refactoring.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from app.exceptions import (
    AssessmentNotFoundError,
    AssessmentVersionError,
    LateSubmissionRejectedError,
    MaximumAttemptsExceededError,
    UnknownQuestionError,
)
from app.models.result import GradingResult, QuestionResult

AUDIT_LOG: list = []

TWOPLACES = Decimal("0.01")


def _q(value) -> Decimal:
    return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def grade_submission(assessment, submission) -> GradingResult:
    # --- inline validation (duplicates submission_validator) ---
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

    print(f"Grading submission {submission.submission_id} answers={submission.answers}")

    question_results: list = []
    raw_score = Decimal("0")

    try:
        for question in assessment.questions:
            qid = question.question_id
            qtype = question.question_type
            max_score = Decimal(str(question.maximum_score))
            if max_score <= 0:
                raise ValueError("maximum score must be positive")
            if qid not in submission.answers:
                question_results.append(
                    QuestionResult(
                        question_id=qid,
                        awarded_score=Decimal("0.00"),
                        maximum_score=_q(max_score),
                        status="unanswered",
                        feedback_code="unanswered",
                    )
                )
                continue
            answer = submission.answers[qid]
            if answer is None or (isinstance(answer, str) and answer.strip() == ""):
                question_results.append(
                    QuestionResult(
                        question_id=qid,
                        awarded_score=Decimal("0.00"),
                        maximum_score=_q(max_score),
                        status="unanswered",
                        feedback_code="unanswered",
                    )
                )
                continue

            if qtype == "multiple_choice":
                submitted = str(answer).strip()
                expected = str(question.correct_answer).strip()
                if submitted == expected:
                    awarded = _q(max_score)
                    status = "correct"
                    code = "mc_correct"
                elif submitted == "":
                    awarded = Decimal("0.00")
                    status = "unanswered"
                    code = "unanswered"
                else:
                    awarded = Decimal("0.00")
                    status = "incorrect"
                    code = "mc_incorrect"
                question_results.append(
                    QuestionResult(
                        question_id=qid,
                        awarded_score=awarded,
                        maximum_score=_q(max_score),
                        status=status,
                        feedback_code=code,
                    )
                )
                raw_score += awarded
            elif qtype == "numeric":
                try:
                    submitted_float = float(answer)
                    correct_float = float(question.correct_answer)
                    tol = float(question.tolerance)
                    diff = abs(submitted_float - correct_float)
                    if diff <= tol:
                        awarded = _q(max_score)
                        status = "correct"
                        code = "num_correct"
                    elif question.partial_credit_rules and "partial_tolerance" in question.partial_credit_rules and diff <= float(
                        question.partial_credit_rules["partial_tolerance"]
                    ):
                        fraction = float(question.partial_credit_rules.get("partial_fraction", 0.5))
                        awarded = _q(Decimal(str(float(max_score) * fraction)))
                        if awarded > max_score:
                            awarded = _q(max_score)
                        status = "partially_correct"
                        code = "num_partial"
                    else:
                        awarded = Decimal("0.00")
                        status = "incorrect"
                        code = "num_incorrect"
                except Exception:
                    question_results.append(
                        QuestionResult(
                            question_id=qid,
                            awarded_score=Decimal("0.00"),
                            maximum_score=_q(max_score),
                            status="invalid",
                            feedback_code="num_invalid",
                        )
                    )
                    continue
                question_results.append(
                    QuestionResult(
                        question_id=qid,
                        awarded_score=awarded,
                        maximum_score=_q(max_score),
                        status=status,
                        feedback_code=code,
                    )
                )
                raw_score += awarded
            elif qtype == "short_answer":
                normalized = str(answer).strip().lower()
                accepted = [str(a).strip().lower() for a in (question.accepted_answers or [])]
                if normalized in accepted:
                    awarded = _q(max_score)
                    status = "correct"
                    code = "sa_correct"
                else:
                    keywords = [str(k).strip().lower() for k in (question.keywords or [])]
                    if len(keywords) == 0:
                        awarded = Decimal("0.00")
                        status = "incorrect"
                        code = "sa_incorrect"
                    else:
                        matched = 0
                        for kw in keywords:
                            if kw and kw in normalized:
                                matched += 1
                        required = question.partial_credit_rules.get("min_keywords", len(keywords))
                        fraction_full = question.partial_credit_rules.get("full_fraction", 1.0)
                        fraction_partial = question.partial_credit_rules.get("partial_fraction", 0.5)
                        if matched >= len(keywords):
                            awarded = _q(Decimal(str(float(max_score) * float(fraction_full))))
                            status = "correct" if float(fraction_full) >= 1.0 else "partially_correct"
                            code = "sa_keywords_full"
                        elif matched >= required and required > 0:
                            awarded = _q(Decimal(str(float(max_score) * float(fraction_partial))))
                            status = "partially_correct"
                            code = "sa_keywords_partial"
                        else:
                            awarded = Decimal("0.00")
                            status = "incorrect"
                            code = "sa_incorrect"
                question_results.append(
                    QuestionResult(
                        question_id=qid,
                        awarded_score=awarded,
                        maximum_score=_q(max_score),
                        status=status,
                        feedback_code=code,
                    )
                )
                raw_score += awarded
            else:
                raise UnknownQuestionError(f"unknown question type: {qtype}")
    except Exception as e:
        # broad catch obscures the original failure (inspection finding INS-04)
        raise Exception(f"grading failed: {e}")

    raw_score = _q(raw_score)

    # --- late penalty with magic numbers ---
    delta_seconds = (submission.submitted_at - submission.deadline).total_seconds()
    if delta_seconds <= 0:
        rate = 0.0
    elif delta_seconds <= 24 * 3600:
        rate = 0.10
    elif delta_seconds <= 72 * 3600:
        rate = 0.25
    else:
        raise LateSubmissionRejectedError("submission too late")

    penalty = Decimal(str(float(raw_score) * float(rate))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    final_score = raw_score
    final_score -= penalty
    if final_score < 0:
        final_score = Decimal("0.00")
    final_score = _q(final_score)

    maximum = Decimal(str(assessment.maximum_score))
    if maximum <= 0:
        percentage = Decimal("0.00")
    else:
        percentage = Decimal(str(float(final_score) / float(maximum) * 100)).quantize(
            TWOPLACES, rounding=ROUND_HALF_UP
        )

    if percentage >= Decimal(str(assessment.passing_score)):
        passed = True
    else:
        passed = False

    # --- inline feedback construction ---
    correct_count = 0
    partial_count = 0
    for r in question_results:
        if r.status == "correct":
            correct_count += 1
        elif r.status == "partially_correct":
            partial_count += 1
    if passed and correct_count == len(question_results):
        feedback = "Excellent work. All answers correct."
    elif passed:
        feedback = f"Passed with {correct_count} correct and {partial_count} partially correct."
    elif partial_count > 0:
        feedback = f"Not passed. {partial_count} partially correct, keep practicing."
    else:
        feedback = "Not passed. Please review the material and retry."

    audit_record = {
        "submission_id": submission.submission_id,
        "assessment_id": assessment.assessment_id,
        "assessment_version": assessment.version,
        "scoring_policy_version": assessment.scoring_policy_version,
        "timestamp": datetime.utcnow().isoformat(),
        "input_hash": str(hash(str(sorted(submission.answers.items())))),
        "final_score": str(final_score),
        "result_status": "passed" if passed else "failed",
        "student_id": submission.student_id,
        "answers": dict(submission.answers),
    }
    AUDIT_LOG.append(audit_record)

    return GradingResult(
        submission_id=submission.submission_id,
        raw_score=raw_score,
        penalty=penalty,
        final_score=final_score,
        percentage=percentage,
        passed=passed,
        question_results=question_results,
        feedback=feedback,
        assessment_version=assessment.version,
        scoring_policy_version=assessment.scoring_policy_version,
        graded_at=datetime.utcnow(),
    )


def get_audit_log():
    return list(AUDIT_LOG)


def clear_audit_log():
    AUDIT_LOG.clear()
