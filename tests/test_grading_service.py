"""GRD-01..GRD-10 complete grading + regression tests."""

from decimal import Decimal

from app.services.grading_service import clear_audit_log, get_audit_log, grade_submission
from tests.conftest import make_submission


def setup_function(_):
    clear_audit_log()


def test_grd01_mixed_raw_score(assessment):
    # Q1 correct 5 + Q2 incorrect 0 + Q3 correct 10 = 15
    sub = make_submission(assessment, {"Q1": "B", "Q2": 999, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    assert result.raw_score == Decimal("15.00")


def test_grd02_final_respects_penalty(assessment):
    sub = make_submission(
        assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"}, late_hours=10
    )
    result = grade_submission(assessment, sub)
    assert result.final_score == result.raw_score - result.penalty


def test_grd03_threshold(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    assert result.percentage == Decimal("100.00")
    assert result.passed is True


def test_grd04_version_stored(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    assert result.assessment_version == "1.0"


def test_grd05_policy_version_stored(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    assert result.scoring_policy_version == "v1"


def test_grd06_every_question_has_result(assessment):
    sub = make_submission(assessment, {"Q1": "B"})
    result = grade_submission(assessment, sub)
    assert len(result.question_results) == 3
    ids = {r.question_id for r in result.question_results}
    assert ids == {"Q1", "Q2", "Q3"}


def test_grd07_deterministic(assessment):
    answers = {"Q1": "B", "Q2": 10.4, "Q3": "plants are green"}
    sub1 = make_submission(assessment, answers, sid="DET")
    sub2 = make_submission(assessment, answers, sid="DET")
    r1 = grade_submission(assessment, sub1)
    r2 = grade_submission(assessment, sub2)
    assert r1.final_score == r2.final_score
    assert r1.percentage == r2.percentage


def test_grd08_evaluator_failure_controlled(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": "bad-input", "Q3": "photosynthesis"})
    result = grade_submission(assessment, sub)
    q2 = next(r for r in result.question_results if r.question_id == "Q2")
    assert q2.status == "invalid"


def test_grd09_audit_created(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"}, sid="AUD1")
    grade_submission(assessment, sub)
    logs = get_audit_log()
    assert len(logs) == 1
    assert logs[0]["submission_id"] == "AUD1"
    assert "final_score" in logs[0]


def test_grd10_audit_has_traceability(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"}, sid="AUD2")
    grade_submission(assessment, sub)
    logs = get_audit_log()
    assert logs[0]["assessment_version"] == "1.0"
    assert logs[0]["scoring_policy_version"] == "v1"
