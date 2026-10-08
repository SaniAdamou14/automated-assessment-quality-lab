# Quality Assessment — Automated Assessment Engine (Unit 6)

## Module Scope
Selected module: Automated Assessment Engine (assessment engine of an online learning platform: live classes, automated assessments, recommendations).
Analyzed files (baseline): `app/services/grading_service.py` (monolithic `grade_submission`), `app/models/*`, `app/services/submission_validator.py`, `app/services/feedback_service.py`, `app/repositories/audit_repository.py`.
Analyzed files (improved): same plus `app/evaluators/{base,multiple_choice,numeric,short_answer}.py`, `app/policies/{scoring_policy,penalty_policy}.py`, wired `submission_validator`, `feedback_service`, `audit_repository`.
Responsibilities: validate submission, evaluate multiple_choice / numeric / short_answer, partial credit, late penalty (0% / 10% <=24h / 25% <=72h / reject >72h), final score with Decimal ROUND_HALF_UP 2dp, feedback, audit traceability.

## Baseline Commit
- Baseline tag: `unit6-baseline`
- Baseline commit: `98f89163bfe6c3313c7a25d1ad9f86292fe58882`
- OS: Windows 11; Python 3.10.5 (project targets py310 in ruff; CI uses 3.12 per spec)
- Tests baseline: 45 collected, 45 passed, 0 failed, 0 skipped

## Quality Goals
- Tests: 0 failed; statement >=90%, branch >=85%
- Max critical-function CC <=10; max anywhere <=15; average rank A
- Critical-file MI >=65 (interpreted jointly with CC, duplication, tests, review; radon MI is experimental)
- Ruff: 0 unreviewed; Semgrep: 0 blocking; Bandit: 0 High; custom rules: 0 unresolved
- Inspection High/Critical: 0 open; AI suggestions: 100% triaged

## Metric Definitions
- Cyclomatic Complexity (Radon, McCabe: decisions+1): 1-5 simple, 6-10 acceptable, 11-15 refactor recommended, 16-20 high risk, >20 unacceptable for grading logic.
- Maintainability Index (Radon 0-100, combines Halstead volume, CC, LOC, comments; experimental, never interpreted alone).
- Size: LOC/LLOC/SLOC, functions, classes (radon raw).
- Quality: ruff (E,F,I,B,UP,SIM,C4,RUF,C90, max-complexity 10), semgrep community + custom, bandit.
- Testability: pytest + coverage.py branch coverage; regression GOLD cases.

## Baseline Results
- Tests: 45 passed; statement 88.22% (242/269), branch 83.33% (80/96) — below gates. Validator 0% (dead code), feedback 60%.
- Radon CC: highest 51 (`grade_submission`, rank F); average 3.19 rank A (26 blocks); functions >10: 1; >15: 1.
- Radon MI: lowest 34.76 (`app/services/grading_service.py`); grading file difficult to maintain (<40 refactor required).
- Radon raw: LOC 448, LLOC 334, SLOC 360. Halstead total volume 1240.2.
- Xenon (`--max-absolute B --max-modules B --max-average A`): FAIL — block F, module C.
- Ruff: 12 findings (F401x3, I001, C901 38>10, E501x4, B904, SIM108, SIM103); format check unformatted.
- Semgrep community (p/python + p/security-audit): 0 findings (no invented vuln).
- Semgrep custom (4 rules): 18 findings — float-for-scores 16, print-student-answer 1, broad-except 1, direct-score-mutation 1.
- Bandit: 0 High/Medium/Low.
- Evidence: `reports/baseline/radon-cc.json`, `radon-mi.json`, `radon-raw.json`, `radon-halstead.json`, `ruff.json`, `coverage.json`, `xenon.txt`, `semgrep.json`, `semgrep-custom.json`, `bandit.json`.

## Inspection Method
Roles (lightweight): moderator/author/functional/quality/security reviewer, recorder (one person may cover several roles; checklist separated from author change in professional context).
Steps: planning, scope, individual preparation, meeting, defect recording, rework, follow-up, closure. Rule: identify/classify first, no mass rewrite in meeting.
Checklist: `review/inspection-checklist.md` (correctness, complexity, maintainability, testability, scalability, reliability, privacy, consistency, documentation, auditability).

## Inspection Findings
10 findings recorded in `review/inspection-findings.csv` (2 High privacy/reliability, rest maintainability/extensibility). Most important:
- INS-01 Critical: 5 responsibilities in one 250-line function (CC 51).
- INS-04 High: broad except + `raise Exception` loses type/traceback.
- INS-05 High: audit coupled + stores student_id + full answers; bypasses AuditRepository.
- INS-07 Medium: debug print of answers.
- INS-08 Medium: float for scores.
All 10 accepted; all corrected in improved (see below).

## Open-Source Tool Evaluation
Selection factors (scalable interactive platform): Python-native, deterministic JSON output for evidence, configurable gates for CI, low false-positive cost, active maintenance, ability to write custom assessment rules.
Capabilities:
- Radon: CC/MI/raw/Halstead; found the CC 51 outlier and MI 34.76 hotspot.
- Xenon: turns Radon thresholds into gates (absolute/module/average); failed baseline as intended.
- Ruff: style+lint+complexity (C901) + format; 12 baseline hits including complexity and B904.
- Semgrep: structural + taint-aware rules + custom assessment rules; 0 community (honest) + 18 custom true positives.
- Bandit + Coverage: security screen (0) + testability (88.22%/83.33% baseline).
Workflow impact: `ruff format --check`, `ruff check`, `pytest --cov-branch`, `radon`, `xenon`, `semgrep community + custom`, `bandit` run locally and in `.github/workflows/quality.yml` (artifact `unit6-quality-evidence`). No developer friction observed beyond fixing 12 ruff + 18 custom hits once.

## AI-Assisted Review
Tool: Muse Spark; date 2026-10-08; prompt `review/ai-review-prompt.md`; raw output `review/ai-review-raw.md` (7 findings, verbatim).
Triage `review/ai-triage.md`: reviewed 7, accepted 5, partially 1, rejected 1. No auto-acceptance.
Most important accepted: AI-05 nondeterministic `hash()` for input_hash (missed by human + static tools; fixed with sha256 over canonical JSON).
Most important rejected: AI-07 switch to pydantic (valid but scope creep; deferred with rationale).
Tests added from AI: audit-privacy exclusion + deterministic-hash. Code changes: 5 refactorings.

## Human Triage
Process: AI suggestion → human code check → static-tool comparison → test/reproduction → decision → documented action. Example: AI-06 concurrency on AUDIT_LOG partially accepted (real testability concern, overstated race; fixed via injected repository, async persistence deferred as residual risk).

## Improvements Applied
- Extracted SubmissionValidator (used), MultipleChoice/Numeric/ShortAnswer evaluators (Strategy), ScoringPolicy, PenaltyPolicy (named constants, versioned), FeedbackService (wired), AuditRepository (injected, sha256, no PII).
- Replaced float with Decimal throughout; narrowed except with `from`; removed print and direct `final_score -=` outside policy (now `PenaltyPolicy.apply`).
- Fixed ruff (imports, line length, SIM, B904) and formatting; split Numeric `_partial_credit` and ShortAnswer `_full/_partial_keyword_hit` to meet Xenon B.
- Added `tests/test_privacy_audit.py` (2 tests).

## Improved Results
- Tests: 47 passed (45 preserved + 2 new), 0 failed, 0 skipped; statement 93.20% (328/345 approx), branch 86.46% (83/96) — gates met.
- Radon CC: highest 10 (`grade_submission` B and `_keyword_score` B); average 2.44 rank A (59 blocks); functions >10: 0; >15: 0.
- Radon MI: lowest 42.91 (`short_answer.py`); grading file 34.76 → 47.92 (+13.16). Still <65 — see Residual Risks (MI experimental, interpreted jointly).
- Radon raw: LOC 638, LLOC 410, SLOC 487 (more lines, simpler functions — expected modularization cost). Halstead volume 1240.2 → 914.3 (−26%).
- Xenon B/B/A: PASS (empty output).
- Ruff: 0 findings; format check passes.
- Semgrep community: 0; custom: 18 → 0.
- Bandit: 0/0/0.
- Evidence: `reports/improved/*` (same set as baseline).

## Before-and-After Comparison
| Metric | Baseline | Improved | Decision |
|---|---|---|---|
| Highest CC | 51 F (`grade_submission`) | 10 B (`grade_submission`, `_keyword_score`) | Pass gate <=10 (borderline); no function >15 |
| Average CC | 3.19 A | 2.44 A | Improved; gate A met |
| Functions >10 / >15 | 1 / 1 | 0 / 0 | Resolved |
| Lowest MI | 34.76 (grading) | 42.91 (short_answer); grading 47.92 | Improved but <65; accepted with rationale (see risks) |
| Statement coverage | 88.22% | 93.20% | Gate >=90 met |
| Branch coverage | 83.33% | 86.46% | Gate >=85 met |
| Ruff findings | 12 | 0 | Resolved |
| Semgrep community | 0 | 0 | No blocking |
| Semgrep custom | 18 | 0 | Resolved |
| Bandit High | 0 | 0 | Pass |
| Xenon B/B/A | FAIL (F/C) | PASS | Gate met |
| Inspection High/Critical open | 4 (INS-01/02/03/04/05) | 0 | All corrected, verified by tests + rescan |
| AI findings accepted | 5 accepted of 7 | all triaged, 2 new tests green | 100% triaged |
| Behavioral regression | GOLD1 25.00/100%, GOLD2 5.00/0.50/4.50 | identical | Behavior preserved |

## Quality Gates
- Tests: PASS (47/47)
- Coverage: PASS (93.20% stmt, 86.46% branch)
- Max CC: PASS (10 <=10); avg: PASS (A)
- Lowest critical MI: DEVIATION (47.92 <65) — documented, mitigation below; not a release blocker given CC/coverage/inspection/AI convergence
- Ruff: PASS; Semgrep: PASS; Bandit: PASS; Inspection: PASS (0 open); AI triage: PASS (7/7)

## Residual Risks
1. MI <65 on small evaluator files (42.91) despite CC<=10 and 93% coverage. Mitigation: MI is experimental and size-sensitive; rely on CC+coverage+review convergence; add targeted comments and monitor churn. Owner: module owner. Planned: re-evaluate after 3 sprints of change data.
2. Concurrency/idempotency at live-exam scale (AI-06 partial). Mitigation: stateless grading + injected repository; load test and async audit persistence before peak. Owner: platform team.
3. Short-answer semantics limited to normalization + keywords (no NLP). Mitigation: document limitation in feedback; human review for borderline; model_version traced if AI added later. Owner: pedagogy team.

## Reproduction Commands
```bash
pip install -r requirements-dev.txt
pytest -q --cov=app --cov-branch --cov-report=term-missing --cov-report=json:reports/improved/coverage.json
radon cc app -s -a -j > reports/improved/radon-cc.json
radon mi app -s -j > reports/improved/radon-mi.json
radon raw app -j > reports/improved/radon-raw.json
radon hal app -j > reports/improved/radon-halstead.json
xenon app --max-absolute B --max-modules B --max-average A
ruff format --check .
ruff check . --output-format json > reports/improved/ruff.json
semgrep scan --config p/python --config p/security-audit app tests --json --output reports/improved/semgrep.json
semgrep scan --config semgrep-rules/assessment-quality.yml app --json --output reports/improved/semgrep-custom.json
bandit -r app -f json -o reports/improved/bandit.json
```
