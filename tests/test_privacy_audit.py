"""Privacy + determinism tests added after refactor (AI-04, AI-05)."""

from app.repositories.audit_repository import canonical_input_hash
from app.services.grading_service import clear_audit_log, get_audit_log, grade_submission
from tests.conftest import make_submission


def setup_function(_):
    clear_audit_log()


def test_audit_excludes_pii_and_answers(assessment):
    sub = make_submission(assessment, {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"}, sid="PRIV1")
    grade_submission(assessment, sub)
    logs = get_audit_log()
    assert len(logs) == 1
    assert "answers" not in logs[0]
    assert "student_id" not in logs[0]
    assert "input_hash" in logs[0]
    assert len(logs[0]["input_hash"]) == 64


def test_input_hash_deterministic(assessment):
    answers = {"Q1": "B", "Q2": 10.0, "Q3": "photosynthesis"}
    h1 = canonical_input_hash(answers)
    h2 = canonical_input_hash(dict(reversed(list(answers.items()))))
    assert h1 == h2
    assert h1 != canonical_input_hash({"Q1": "A"})
