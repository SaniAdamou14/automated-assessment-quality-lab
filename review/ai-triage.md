# AI triage — human decisions (2026-10-08)
Reviewer: student engineer. Every AI suggestion independently verified against code, tests and static tools. No automatic acceptance.

## AI-01 High CC / extract responsibilities
- AI severity: High
- Human decision: accepted
- Reason: Confirmed by radon CC=51 rank F for grade_submission; xenon block F; inspection INS-01.
- Supporting code: app/services/grading_service.py:31 grade_submission (~250 lines)
- Supporting test: full suite 45 passed; regression GOLD1/GOLD2 golden values
- Static-tool agreement: yes (radon, xenon, ruff C901)
- Action: Refactor to validator + evaluator strategies + policies + services (improved version)
- Final status: implemented; verify radon improved <=10

## AI-02 Magic penalty numbers
- AI severity: Medium
- Human decision: accepted
- Reason: Literals 24*3600 72*3600 0.10 0.25 confirmed; matches INS-03.
- Supporting code: grading_service.py penalty block
- Supporting test: PEN-01..PEN-06
- Static-tool agreement: partial (maintainability, not a rule hit)
- Action: PenaltyPolicy with named constants + version
- Final status: implemented

## AI-03 Broad except
- AI severity: High
- Human decision: accepted
- Reason: `except Exception` + `raise Exception(f"...")` confirmed; ruff B904; semgrep broad-except-grading hit.
- Supporting code: grading_service.py try/except around loop
- Supporting test: GRD-08 invalid controlled
- Static-tool agreement: yes (ruff + semgrep custom)
- Action: Narrow try to numeric parsing only; propagate domain exceptions with `from`
- Final status: implemented

## AI-04 PII in print + audit
- AI severity: High
- Human decision: accepted
- Reason: print with answers + audit storing student_id/answers confirmed; semgrep print-student-answer hit; INS-05/INS-07.
- Supporting code: print line 44; audit_record dict
- Supporting test: GRD-09 audit created (baseline); new privacy test in improved asserts exclusion
- Static-tool agreement: yes (semgrep custom)
- Action: Remove print; AuditRepository injected; store sha256 input_hash only
- Final status: implemented

## AI-05 Nondeterministic hash()
- AI severity: Medium
- Human decision: accepted (most valuable AI-specific catch)
- Reason: Python hash() salted per process — correct. Manual inspection missed this; static tools did not flag it. Verified by reasoning + docs.
- Supporting code: input_hash str(hash(...))
- Supporting test: added deterministic-hash check in improved (same input same sha256)
- Static-tool agreement: no (complements tools)
- Action: Replace with hashlib.sha256 over canonical JSON sort_keys
- Final status: implemented

## AI-06 Concurrency on AUDIT_LOG
- AI severity: Medium
- Human decision: partially accepted
- Reason: Global mutable list is a real testability concern, but no threaded reproduction exists; CPython append atomicity means claimed race is overstated. Architectural risk for scale, not an observed defect.
- Supporting code: AUDIT_LOG global
- Supporting test: none (no concurrency harness)
- Static-tool agreement: no
- Action: Inject AuditRepository to make grading stateless/testable; defer async/threaded persistence to deployment design; document as residual risk
- Final status: partially implemented; risk documented

## AI-07 Pydantic validation
- AI severity: Low
- Human decision: rejected (deferred)
- Reason: Valid idea but adds dependency and scope creep; current explicit validator + grading checks cover negative-score case (tested). Cost/benefit unfavorable for this unit.
- Supporting code: app/models/*.py dataclasses
- Supporting test: negative max_score raises ValueError in grading (covered)
- Static-tool agreement: no
- Action: none now; noted as future option in QUALITY.md residual risks
- Final status: rejected with rationale

Summary: reviewed 7 | accepted 5 | partially accepted 1 | rejected 1 | tests added from AI: deterministic-hash + audit-privacy | code changes from AI: 5 refactorings above.
