"""In-memory audit store (baseline: grading service bypasses it)."""
from __future__ import annotations


class AuditRepository:
    def __init__(self):
        self.records = []

    def save(self, record: dict) -> None:
        if "submission_id" not in record:
            raise ValueError("audit record missing submission_id")
        self.records.append(record)

    def all(self):
        return list(self.records)

    def clear(self):
        self.records.clear()
