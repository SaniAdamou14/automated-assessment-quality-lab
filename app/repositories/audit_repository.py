"""Audit repository storing only non-sensitive traceability metadata."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime


def canonical_input_hash(answers: dict) -> str:
    payload = json.dumps(answers, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditRepository:
    def __init__(self) -> None:
        self.records: list = []

    def save(self, record: dict) -> None:
        if "submission_id" not in record:
            raise ValueError("audit record missing submission_id")
        if "answers" in record or "student_id" in record:
            raise ValueError("audit record must not contain PII or answers")
        self.records.append(record)

    def record_grading(
        self,
        *,
        submission_id: str,
        assessment_id: str,
        assessment_version: str,
        scoring_policy_version: str,
        input_hash: str,
        final_score: str,
        result_status: str,
    ) -> dict:
        record = {
            "submission_id": submission_id,
            "assessment_id": assessment_id,
            "assessment_version": assessment_version,
            "scoring_policy_version": scoring_policy_version,
            "timestamp": datetime.utcnow().isoformat(),
            "input_hash": input_hash,
            "final_score": final_score,
            "result_status": result_status,
        }
        self.save(record)
        return record

    def all(self) -> list:
        return list(self.records)

    def clear(self) -> None:
        self.records.clear()
