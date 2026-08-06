"""Persistent pre-call budget reservations with fail-closed reconciliation."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import Field, StrictInt, model_validator

from bench.io import atomic_json, digest
from bench.models import StrictModel

from .models import OptimizationConfig


class UsageCounters(StrictModel):
    candidates: StrictInt = Field(default=0, ge=0)
    task_invocations: StrictInt = Field(default=0, ge=0)
    proposer_calls: StrictInt = Field(default=0, ge=0)
    infrastructure_retries: StrictInt = Field(default=0, ge=0)
    proposer_input_tokens: StrictInt = Field(default=0, ge=0)
    proposer_output_tokens: StrictInt = Field(default=0, ge=0)
    compute_hours: float = Field(default=0, ge=0)
    proposer_cost_usd: float = Field(default=0, ge=0)
    compute_cost_usd: float = Field(default=0, ge=0)


class Reservation(StrictModel):
    reservation_id: str
    ordinal: StrictInt = Field(gt=0)
    kind: Literal["candidate", "task", "proposer", "retry", "compute"]
    status: Literal["pending", "complete", "interrupted"]
    reserved: UsageCounters
    actual: UsageCounters | None = None
    created_at_utc: str


class BudgetState(StrictModel):
    format_version: Literal[1] = 1
    run_id: str
    counters: UsageCounters
    reservations: list[Reservation]
    state_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def valid_hash(self) -> BudgetState:
        value = self.model_dump(mode="json", exclude={"state_sha256"})
        if digest(value) != self.state_sha256:
            raise ValueError("optimizer budget state hash mismatch")
        if [item.ordinal for item in self.reservations] != list(
            range(1, len(self.reservations) + 1)
        ):
            raise ValueError("optimizer budget reservation history is inconsistent")
        return self


def enforce_budget(config: OptimizationConfig, usage: UsageCounters, *, pilot: bool) -> None:
    limits = {
        "candidates": config.budget.pilot_candidates if pilot else config.budget.total_candidates,
        "task_invocations": config.budget.task_invocations,
        "proposer_calls": config.proposer.max_calls,
        "proposer_input_tokens": config.proposer.max_input_tokens,
        "proposer_output_tokens": config.proposer.max_output_tokens,
        "compute_hours": (
            config.budget.pilot_compute_hours if pilot else config.budget.total_compute_hours
        ),
        "proposer_cost_usd": config.proposer.max_cost_usd,
        "compute_cost_usd": config.budget.compute_cost_usd,
    }
    for name, ceiling in limits.items():
        if getattr(usage, name) > ceiling:
            raise ValueError(f"optimizer {name.replace('_', ' ')} ceiling exceeded")
    if usage.infrastructure_retries > usage.task_invocations:
        raise ValueError("optimizer infrastructure retry accounting is invalid")


class BudgetLedger:
    def __init__(self, root: Path, config: OptimizationConfig, *, pilot: bool = True) -> None:
        self.path = root / "budget.json"
        self.config = config
        self.pilot = pilot

    def initialize(self) -> BudgetState:
        if self.path.exists():
            raise ValueError("optimizer budget state already exists; use resume")
        return self._write(UsageCounters(), [])

    def load(self) -> BudgetState:
        if not self.path.exists():
            raise ValueError("optimizer budget state is missing")
        return BudgetState.model_validate_json(self.path.read_text(encoding="utf-8"))

    def can_fit(self, additional: UsageCounters) -> bool:
        additional = self._with_proposer_cost(additional)
        try:
            enforce_budget(self.config, _add(self.load().counters, additional), pilot=self.pilot)
        except ValueError:
            return False
        return True

    def achievable_operations(self, per_operation: UsageCounters) -> int:
        """Return the exact number of identical next operations fitting every active ceiling."""
        per_operation = self._with_proposer_cost(per_operation)
        state = self.load()
        limits = _limits(self.config, pilot=self.pilot)
        capacities: list[int] = []
        for name, ceiling in limits.items():
            amount = getattr(per_operation, name)
            if amount > 0:
                remaining = max(0.0, ceiling - getattr(state.counters, name))
                capacities.append(int((remaining + 1e-12) // amount))
        return min(capacities) if capacities else 0

    def _with_proposer_cost(self, usage: UsageCounters) -> UsageCounters:
        cost = (
            usage.proposer_input_tokens * self.config.proposer.input_usd_per_million
            + usage.proposer_output_tokens * self.config.proposer.output_usd_per_million
        ) / 1_000_000
        return usage.model_copy(update={"proposer_cost_usd": cost})

    def reserve(
        self,
        kind: Literal["candidate", "task", "proposer", "retry", "compute"],
        *,
        candidate_count: int = 0,
        task_calls: int = 0,
        proposer_calls: int = 0,
        retries: int = 0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        compute_hours: float = 0,
        compute_cost_usd: float = 0,
    ) -> Reservation:
        state = self.load()
        cost = (
            input_tokens * self.config.proposer.input_usd_per_million
            + output_tokens * self.config.proposer.output_usd_per_million
        ) / 1_000_000
        reserved = UsageCounters(
            candidates=candidate_count,
            task_invocations=task_calls,
            proposer_calls=proposer_calls,
            infrastructure_retries=retries,
            proposer_input_tokens=input_tokens,
            proposer_output_tokens=output_tokens,
            compute_hours=compute_hours,
            proposer_cost_usd=cost,
            compute_cost_usd=compute_cost_usd,
        )
        prospective = _add(state.counters, reserved)
        enforce_budget(self.config, prospective, pilot=self.pilot)
        ordinal = len(state.reservations) + 1
        reservation = Reservation(
            reservation_id=digest({"run_id": self.config.run_id, "ordinal": ordinal, "kind": kind}),
            ordinal=ordinal,
            kind=kind,
            status="pending",
            reserved=reserved,
            created_at_utc=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        )
        self._write(prospective, [*state.reservations, reservation])
        return reservation

    def reconcile(
        self,
        reservation_id: str,
        actual: UsageCounters | None,
        *,
        interrupted: bool = False,
    ) -> BudgetState:
        state = self.load()
        matches = [item for item in state.reservations if item.reservation_id == reservation_id]
        if len(matches) != 1:
            raise ValueError("optimizer budget reservation is missing or duplicated")
        current = matches[0]
        if current.status != "pending":
            raise ValueError("optimizer budget reservation is already reconciled")
        if actual is None:
            updated = current.model_copy(update={"status": "interrupted"})
            reservations = [updated if item == current else item for item in state.reservations]
            self._write(state.counters, reservations)
            raise ValueError("optimizer provider usage is missing; reservation retained")
        actual_cost = (
            actual.proposer_input_tokens * self.config.proposer.input_usd_per_million
            + actual.proposer_output_tokens * self.config.proposer.output_usd_per_million
        ) / 1_000_000
        actual = actual.model_copy(update={"proposer_cost_usd": actual_cost})
        if not _within(actual, current.reserved):
            updated = current.model_copy(update={"status": "interrupted", "actual": actual})
            reservations = [updated if item == current else item for item in state.reservations]
            self._write(state.counters, reservations)
            raise ValueError("optimizer actual usage exceeds its pre-call reservation")
        counters = _add(_subtract(state.counters, current.reserved), actual)
        enforce_budget(self.config, counters, pilot=self.pilot)
        updated = current.model_copy(
            update={"status": "interrupted" if interrupted else "complete", "actual": actual}
        )
        reservations = [updated if item == current else item for item in state.reservations]
        return self._write(counters, reservations)

    def _write(self, counters: UsageCounters, reservations: list[Reservation]) -> BudgetState:
        payload = {
            "format_version": 1,
            "run_id": self.config.run_id,
            "counters": counters.model_dump(mode="json"),
            "reservations": [item.model_dump(mode="json") for item in reservations],
        }
        state = BudgetState(**payload, state_sha256=digest(payload))
        atomic_json(self.path, state.model_dump(mode="json"))
        return state


def _add(left: UsageCounters, right: UsageCounters) -> UsageCounters:
    return UsageCounters(
        **{name: getattr(left, name) + getattr(right, name) for name in UsageCounters.model_fields}
    )


def _subtract(left: UsageCounters, right: UsageCounters) -> UsageCounters:
    values = {
        name: getattr(left, name) - getattr(right, name) for name in UsageCounters.model_fields
    }
    if any(value < 0 for value in values.values()):
        raise ValueError("optimizer budget counters cannot reconcile below zero")
    return UsageCounters(**values)


def _within(actual: UsageCounters, reserved: UsageCounters) -> bool:
    return all(
        getattr(actual, name) <= getattr(reserved, name) for name in UsageCounters.model_fields
    )


def _limits(config: OptimizationConfig, *, pilot: bool) -> dict[str, float | int]:
    return {
        "candidates": config.budget.pilot_candidates if pilot else config.budget.total_candidates,
        "task_invocations": config.budget.task_invocations,
        "proposer_calls": config.proposer.max_calls,
        "proposer_input_tokens": config.proposer.max_input_tokens,
        "proposer_output_tokens": config.proposer.max_output_tokens,
        "compute_hours": (
            config.budget.pilot_compute_hours if pilot else config.budget.total_compute_hours
        ),
        "proposer_cost_usd": config.proposer.max_cost_usd,
        "compute_cost_usd": config.budget.compute_cost_usd,
    }
