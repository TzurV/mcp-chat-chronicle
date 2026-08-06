"""Append-only optimizer attempt and explicit current-authority storage."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, StrictInt, model_validator

from bench.io import atomic_json, digest
from bench.models import StrictModel


class TrialAttempt(StrictModel):
    format_version: Literal[1] = 1
    trial_id: str
    attempt: StrictInt = Field(gt=0)
    status: Literal["complete", "failed", "interrupted"]
    candidate_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    result_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    failure_category: str | None = None
    accounting: dict[str, Any]
    optimizer_wall_ms: StrictInt = Field(default=0, ge=0)
    created_at_utc: str
    record_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def valid_hash(self) -> TrialAttempt:
        if digest(self.model_dump(mode="json", exclude={"record_sha256"})) != self.record_sha256:
            raise ValueError("optimizer attempt record hash mismatch")
        if self.status == "complete" and (self.candidate_id is None or self.result_id is None):
            raise ValueError("complete optimizer attempt requires candidate and result identities")
        return self


class CurrentAuthority(StrictModel):
    format_version: Literal[1] = 1
    trial_id: str
    current_attempt: StrictInt = Field(gt=0)
    attempt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class TrialStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def append(
        self,
        trial_id: str,
        status: Literal["complete", "failed", "interrupted"],
        accounting: dict[str, Any],
        *,
        candidate_id: str | None = None,
        result_id: str | None = None,
        failure_category: str | None = None,
        optimizer_wall_ms: int = 0,
    ) -> TrialAttempt:
        trial = self.root / "trials" / trial_id
        attempts = trial / "attempts"
        existing = sorted(attempts.glob("*.json")) if attempts.exists() else []
        if existing:
            self.current(trial_id)
        ordinal = len(existing) + 1
        payload = {
            "format_version": 1,
            "trial_id": trial_id,
            "attempt": ordinal,
            "status": status,
            "candidate_id": candidate_id,
            "result_id": result_id,
            "failure_category": failure_category,
            "accounting": accounting,
            "optimizer_wall_ms": optimizer_wall_ms,
            "created_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        record = TrialAttempt(**payload, record_sha256=digest(payload))
        path = attempts / f"{ordinal:04d}.json"
        if path.exists():
            raise ValueError("optimizer attempt path already exists")
        atomic_json(path, record.model_dump(mode="json"))
        authority = CurrentAuthority(
            trial_id=trial_id, current_attempt=ordinal, attempt_sha256=record.record_sha256
        )
        atomic_json(trial / "current.json", authority.model_dump(mode="json"))
        return record

    def attempts(self, trial_id: str) -> list[TrialAttempt]:
        """Return every validated append-only attempt after checking latest authority."""
        current = self.current(trial_id)
        if current is None:
            return []
        paths = sorted((self.root / "trials" / trial_id / "attempts").glob("*.json"))
        attempts = [
            TrialAttempt.model_validate_json(path.read_text(encoding="utf-8")) for path in paths
        ]
        if attempts[-1] != current:
            raise ValueError("optimizer attempt history does not end at current authority")
        return attempts

    def current(self, trial_id: str) -> TrialAttempt | None:
        trial = self.root / "trials" / trial_id
        path = trial / "current.json"
        if not path.exists():
            if list((trial / "attempts").glob("*.json")):
                raise ValueError("optimizer current-attempt authority is missing")
            return None
        authority = CurrentAuthority.model_validate_json(path.read_text(encoding="utf-8"))
        attempts = sorted((trial / "attempts").glob("*.json"))
        if not attempts:
            raise ValueError("optimizer current-attempt authority is dangling")
        expected_latest = int(attempts[-1].stem)
        if authority.current_attempt != expected_latest:
            raise ValueError("optimizer current-attempt authority is stale")
        attempt_path = path.parent / "attempts" / f"{authority.current_attempt:04d}.json"
        if not attempt_path.exists():
            raise ValueError("optimizer current-attempt authority is dangling")
        attempt = TrialAttempt.model_validate_json(attempt_path.read_text(encoding="utf-8"))
        if attempt.trial_id != trial_id or attempt.attempt != authority.current_attempt:
            raise ValueError("optimizer current-attempt record identity mismatch")
        if attempt.record_sha256 != authority.attempt_sha256:
            raise ValueError("optimizer current-attempt authority mismatch")
        return attempt
