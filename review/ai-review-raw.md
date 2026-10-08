# AI review — raw output (unedited)
Tool: Muse Spark (AI-assisted review in analysis environment)
Date: 2026-10-08
Prompt file: review/ai-review-prompt.md
Scope: app/services/grading_service.py, app/services/submission_validator.py, app/services/feedback_service.py, app/repositories/audit_repository.py, app/models/*
Note: output copied verbatim without correction. Human triage in review/ai-triage.md.

---
## AI-01 — Severity: High
File: app/services/grading_service.py — function: grade_submission
Explanation: Single function handles validation, 3 question types, penalties, feedback and audit. Likely CC > 20. Hard to test branches in isolation.
Reproduction: Add a 4th question type; central if/elif must change. Run `radon cc app -s -a` to confirm.
Proposed correction: Extract SubmissionValidator, QuestionEvaluator strategies, ScoringPolicy, PenaltyPolicy, FeedbackService, AuditRepository. Keep orchestrator < 40 lines.
Verification test: Existing GRD + regression suite stays green; `radon cc` per-function <= 10.
Uncertainty: Medium confidence on exact CC value without running radon; structural observation is high confidence.

## AI-02 — Severity: Medium
File: app/services/grading_service.py — function: grade_submission
Explanation: Late-penalty thresholds (24h, 72h) and rates (0.10, 0.25) are literals. Risk of inconsistent change.
Reproduction: Search for `24 * 3600` and `0.25`; two policies in one function.
Proposed correction: Named constants or PenaltyPolicy object with versioned rules.
Verification test: PEN-01..PEN-06 unchanged behavior.
Uncertainty: Low — literal values visible.

## AI-03 — Severity: High
File: app/services/grading_service.py — function: grade_submission
Explanation: Broad `except Exception` wrapping the whole question loop, then `raise Exception(...)` loses original type/traceback. Numeric invalid input and programming errors become indistinguishable.
Reproduction: Pass invalid numeric + trigger an unrelated bug; both surface as generic Exception.
Proposed correction: Catch only expected conversion errors narrowly; let specific domain exceptions propagate with `raise ... from err`.
Verification test: GRD-08 invalid input yields status invalid; validator errors preserve type.
Uncertainty: Low — pattern visible at end of loop.

## AI-04 — Severity: High
File: app/services/grading_service.py — function: grade_submission
Explanation: `print(f"Grading submission ... answers={submission.answers}")` and audit record storing `student_id` + full `answers` expose PII in logs/storage.
Reproduction: Grade any submission; stdout contains answers; AUDIT_LOG[0] contains student answers.
Proposed correction: Remove print; log only submission_id; audit stores hash + scores + versions, no answers/PII.
Verification test: Assert audit record has no `answers`/`student_id` keys; grep no `print(` in app/.
Uncertainty: Low — lines clearly present.

## AI-05 — Severity: Medium
File: app/services/grading_service.py — function: grade_submission
Explanation: `input_hash: str(hash(str(sorted(answers.items()))))` uses Python `hash()` which is salted per process (PYTHONHASHSEED). Audit hashes are nondeterministic across restarts — breaks traceability/idempotency checks.
Reproduction: Grade same submission in two processes with different PYTHONHASHSEED; compare input_hash.
Proposed correction: Use hashlib.sha256 over canonical JSON with sort_keys.
Verification test: Deterministic hash test across runs; GRD-07 repeat grading stable.
Uncertainty: Medium — behavior depends on hash randomization being enabled (default on). Recommend verifying with two runs.

## AI-06 — Severity: Medium
File: app/services/grading_service.py — global AUDIT_LOG
Explanation: Module-global mutable list may cause race conditions under concurrent grading (live-class scale).
Reproduction: Concurrent grading from threads could interleave appends (though CPython append is atomic, ordering still nondeterministic).
Proposed correction: Inject AuditRepository instance; make grading stateless; defer async persistence.
Verification test: Threaded grading smoke test.
Uncertainty: High — no concurrency harness in repo; risk is architectural, not observed. Requires human judgment on deployment model.

## AI-07 — Severity: Low
File: app/models/*.py
Explanation: Dataclasses lack runtime validation (e.g., negative maximum_score only checked late in grading). Suggest pydantic or attrs with validators.
Reproduction: Construct Question with negative score; no error until grading.
Proposed correction: Add validation in __post_init__ or switch to pydantic.
Verification test: Unit test for negative score rejection at construction.
Uncertainty: High — design tradeoff; adds dependency; out of scope for this unit unless team agrees. Suggest defer.
---
End of raw AI output.
