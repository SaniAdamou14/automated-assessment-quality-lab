"""Audit repository tests."""
import pytest

from app.repositories.audit_repository import AuditRepository


def test_save_and_list():
    repo = AuditRepository()
    repo.save({"submission_id": "S1", "final_score": "10.00"})
    assert len(repo.all()) == 1


def test_missing_id_raises():
    repo = AuditRepository()
    with pytest.raises(ValueError):
        repo.save({"final_score": "10.00"})


def test_clear():
    repo = AuditRepository()
    repo.save({"submission_id": "S1"})
    repo.clear()
    assert repo.all() == []
