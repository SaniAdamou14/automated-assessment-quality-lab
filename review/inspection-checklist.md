# Inspection checklist — Automated Assessment Engine

## Correctness
- [ ] Scores within [0, maximum]? Partial credit applied once? Penalty order deterministic?
- [ ] Missing vs incorrect distinguished? Rounding documented (ROUND_HALF_UP, 2dp)?

## Complexity
- [ ] Any function CC > 10? Nesting > 3? Long function > 60 lines?

## Maintainability
- [ ] Single responsibility per function? Policies separated from orchestration?
- [ ] No magic numbers? Names express intent? New question type without central if/elif?

## Testability
- [ ] Pure score functions? Deterministic repeat grading? Injectable dependencies?

## Scalability / Reliability
- [ ] Stateless logic where possible? No quadratic loops? Idempotent audit?

## Privacy / Security
- [ ] Full answers in logs? PII minimized? Open inputs validated? Internal errors exposed?

## Consistency / Documentation
- [ ] Status vocabulary consistent? Policy versions traced? Audit complete?
