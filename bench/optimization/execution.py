"""Tracked, resumable optimizer orchestration with injected provider adapters."""

from __future__ import annotations

import hashlib
import json
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from pydantic import Field, StrictInt, model_validator

from bench.implementation import ImplementationIdentity, measure_implementation
from bench.io import atomic_json, digest
from bench.models import TASK_ORDER, StrictModel

from .authority import VerifiedAuthority, verify_authority
from .budget import BudgetLedger, UsageCounters
from .compat import verify_compatibility
from .feedback import Diagnostic, render_feedback
from .metrics import MetricVector
from .models import (
    OptimizationConfig,
    candidate_model_identity,
    load_optimization_config,
    optimization_config_identity,
    optimizer_framework_identity,
    proposer_identity,
    resolve_config_path,
)
from .package import (
    CandidateAccounting,
    CandidateDemonstration,
    CandidatePackage,
    CandidateResult,
    PrivacyEvidence,
    ResultAuthority,
    baseline_package,
    mutate_package,
    read_result,
    result_identity,
    write_package,
    write_result,
)
from .privacy import scan_package
from .trials import TrialStore


class AdapterReservation(StrictModel):
    task_calls: StrictInt = Field(default=0, ge=0)
    proposer_calls: StrictInt = Field(default=0, ge=0)
    input_tokens: StrictInt = Field(default=0, ge=0)
    output_tokens: StrictInt = Field(default=0, ge=0)
    compute_hours: float = Field(default=0, ge=0)
    compute_cost_usd: float = Field(default=0, ge=0)
    retries: StrictInt = Field(default=0, ge=0, le=3000)
    reasoning_tokens: StrictInt = Field(default=0, ge=0, exclude_if=lambda value: value == 0)
    provider_cost_usd: float = Field(default=0, ge=0, exclude_if=lambda value: value == 0)


class AdapterUsage(AdapterReservation):
    latency_ms: StrictInt = Field(default=0, ge=0)


class OptimizerOperationError(RuntimeError):
    """Optimizer failure carrying measured usage across adaptation boundaries."""

    def __init__(
        self,
        message: str,
        *,
        usage: AdapterUsage | None,
        failure_category: str,
        usage_complete: bool = True,
    ) -> None:
        self.usage = usage
        self.failure_category = failure_category
        self.usage_complete = usage_complete
        super().__init__(message)

    def __reduce__(self):
        return (
            _restore_optimizer_operation_error,
            (str(self), self.usage, self.failure_category, self.usage_complete),
        )


def _restore_optimizer_operation_error(
    message: str,
    usage: AdapterUsage | None,
    failure_category: str,
    usage_complete: bool,
) -> OptimizerOperationError:
    return OptimizerOperationError(
        message,
        usage=usage,
        failure_category=failure_category,
        usage_complete=usage_complete,
    )


class CaseOutcome(StrictModel):
    alias: str
    task: str
    model_id: str = Field(min_length=1)
    terminal: bool
    valid: bool
    semantic_agreement: float = Field(ge=0, le=1)
    diagnostics: list[Diagnostic]


class EvaluationBatch(StrictModel):
    scope: Literal["train", "validation"]
    model_id: str = Field(min_length=1)
    outcomes: list[CaseOutcome]
    usage: AdapterUsage


class Proposal(StrictModel):
    prompts: dict[str, str]
    demonstrations: dict[str, list[CandidateDemonstration]] = Field(
        default_factory=lambda: {task: [] for task in TASK_ORDER}
    )
    strategy: str
    usage: AdapterUsage
    search_exhausted: bool = False

    @model_validator(mode="after")
    def complete(self) -> Proposal:
        if tuple(self.prompts) != TASK_ORDER:
            raise ValueError("optimizer proposal must contain four prompts in fixed order")
        if tuple(self.demonstrations) != TASK_ORDER:
            raise ValueError("optimizer proposal must account for demonstrations for four tasks")
        return self


class CandidateAdapter(Protocol):
    def reservation(
        self, scope: Literal["train", "validation"], model_id: str
    ) -> AdapterReservation: ...

    def evaluate(
        self,
        candidate: CandidatePackage,
        scope: Literal["train", "validation"],
        model_id: str,
        authority: VerifiedAuthority,
    ) -> EvaluationBatch: ...


class OptimizerAdapter(Protocol):
    def reservation(
        self, optimizer: Literal["bootstrap-few-shot", "gepa"]
    ) -> AdapterReservation: ...

    def bootstrap(self, parent: CandidatePackage, authority: VerifiedAuthority) -> Proposal: ...

    def gepa(
        self,
        parent: CandidatePackage,
        authority: VerifiedAuthority,
        feedback: str,
        ordinal: int,
    ) -> Proposal: ...


@dataclass(frozen=True)
class ExecutionAdapters:
    candidate: CandidateAdapter
    optimizer: OptimizerAdapter


class ExecutionAuthority(StrictModel):
    format_version: Literal[1] = 1
    mode: Literal["optimize", "resume"]
    authorization_ordinal: StrictInt = Field(gt=0)
    run_id: str
    application_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    config_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    development_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    train_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_artifact_sha256: dict[str, str]
    proposer_identity_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    optimizer_identity_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    budget_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    authority_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def valid_hash(self) -> ExecutionAuthority:
        calculated = digest(self.model_dump(mode="json", exclude={"authority_sha256"}))
        if calculated != self.authority_sha256:
            raise ValueError("optimizer execution authority hash mismatch")
        return self


class PilotCheckpoint(StrictModel):
    format_version: Literal[1] = 1
    pilot_gepa_result_ids: list[str]
    safety_privacy_accounting_resume: bool
    validation_no_worse_than_p0: bool
    distinct_privacy_eligible: bool
    projected_costs_within_total_ceilings: bool
    decision: Literal["continue", "stop"]
    achievable_additional_candidates: StrictInt = Field(ge=0)
    budget_state_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    checkpoint_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def consistent(self) -> PilotCheckpoint:
        criteria = (
            self.safety_privacy_accounting_resume,
            self.validation_no_worse_than_p0,
            self.distinct_privacy_eligible,
            self.projected_costs_within_total_ceilings,
        )
        if self.decision != ("continue" if all(criteria) else "stop"):
            raise ValueError("pilot continuation decision does not match declared criteria")
        if (
            digest(self.model_dump(mode="json", exclude={"checkpoint_sha256"}))
            != self.checkpoint_sha256
        ):
            raise ValueError("pilot checkpoint hash mismatch")
        return self


class RunState(StrictModel):
    format_version: Literal[2] = 2
    run_id: str
    status: Literal[
        "in-progress",
        "pilot-complete",
        "pilot-no-improvement",
        "continuing",
        "complete",
        "budget-limited",
        "no-improvement",
    ]
    baseline_result_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    bootstrap_result_ids: list[str]
    gepa_result_ids: list[str]
    authorization_ids: list[str]
    pilot_checkpoint: PilotCheckpoint | None = None
    stop_reason: str | None = None
    state_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def valid_hash(self) -> RunState:
        if digest(self.model_dump(mode="json", exclude={"state_sha256"})) != self.state_sha256:
            raise ValueError("optimizer run state hash mismatch")
        return self


@dataclass(frozen=True)
class ProposedCandidate:
    candidate: CandidatePackage | None
    optimizer_latency_ms: int
    search_exhausted: bool
    optimizer_usage: AdapterUsage


def run_optimization(
    config_path: Path,
    adapters: ExecutionAdapters | None = None,
    *,
    resume: bool,
    identity_probe=measure_implementation,
    monotonic_ns=time.monotonic_ns,
) -> dict[str, object]:
    config = load_optimization_config(config_path)
    _verify_execution_inputs(config, config_path)
    authority = verify_authority(config, config_path)
    root = resolve_config_path(config_path, config.paths.run_root)
    root.mkdir(parents=True, exist_ok=True)
    measured: ImplementationIdentity = identity_probe()
    state = _load_state(root) if resume else None
    if resume:
        if state is None:
            raise ValueError("optimizer run state is missing for resume")
    else:
        if state is not None:
            raise ValueError("optimizer run already exists; use resume")
        ledger = BudgetLedger(root, config, pilot=True)
        ledger.initialize()
        state = _write_state(root, config.run_id, "in-progress", None, [], [], [])
    if state.status in {
        "pilot-no-improvement",
        "complete",
        "budget-limited",
        "no-improvement",
    }:
        return _run_summary(state, BudgetLedger(root, config, pilot=False).load(), None)
    continuation = state.status == "pilot-complete"
    ledger = BudgetLedger(root, config, pilot=not continuation)
    ledger.load()
    authorization = _authorize(root, config, measured, resume=resume)
    if adapters is None:
        from .production import build_production_adapters

        adapters = build_production_adapters(config, config_path, authority)
    state = _write_state(
        root,
        config.run_id,
        "continuing" if continuation else "in-progress",
        state.baseline_result_id,
        state.bootstrap_result_ids,
        state.gepa_result_ids,
        [*state.authorization_ids, authorization.authority_sha256],
        state.pilot_checkpoint,
    )
    catalog = resolve_config_path(config_path, config.paths.accepted_task_catalog)
    baseline = baseline_package(catalog)
    if state.baseline_result_id is None:
        baseline_result = _evaluate(
            baseline,
            config,
            config_path,
            authority,
            authorization,
            adapters.candidate,
            ledger,
            root,
        )
        state = _write_state(
            root,
            config.run_id,
            "continuing" if state.pilot_checkpoint else "in-progress",
            baseline_result.result_id,
            state.bootstrap_result_ids,
            state.gepa_result_ids,
            state.authorization_ids,
            state.pilot_checkpoint,
        )
    else:
        baseline_result = _result_by_id(root, state.baseline_result_id)

    if config.bootstrap_enabled and not state.bootstrap_result_ids:
        proposed = _propose(
            baseline,
            "bootstrap-few-shot",
            1,
            "",
            config,
            authority,
            authorization,
            adapters,
            ledger,
            root,
            monotonic_ns,
        )
        if proposed.candidate is None:
            raise ValueError("BootstrapFewShot cannot exhaust without a candidate")
        bootstrap_result = _evaluate(
            proposed.candidate,
            config,
            config_path,
            authority,
            authorization,
            adapters.candidate,
            ledger,
            root,
            optimizer_latency_ms=proposed.optimizer_latency_ms,
        )
        _complete_proposal_trial(
            root,
            "bootstrap-few-shot",
            1,
            bootstrap_result,
            ledger,
            proposed.optimizer_latency_ms,
            proposed.optimizer_usage,
        )
        state = _write_state(
            root,
            config.run_id,
            "in-progress",
            state.baseline_result_id,
            [bootstrap_result.result_id],
            state.gepa_result_ids,
            state.authorization_ids,
            state.pilot_checkpoint,
        )

    if not continuation:
        state = _run_gepa_phase(
            state,
            config,
            config_path,
            authority,
            authorization,
            adapters,
            ledger,
            root,
            baseline_result,
            config.budget.pilot_candidates,
            monotonic_ns,
        )
        checkpoint = _pilot_checkpoint(state, config, adapters, ledger, root, baseline_result)
        status = "pilot-complete" if checkpoint.decision == "continue" else "pilot-no-improvement"
        state = _write_state(
            root,
            config.run_id,
            status,
            state.baseline_result_id,
            state.bootstrap_result_ids,
            state.gepa_result_ids,
            state.authorization_ids,
            checkpoint,
            None if checkpoint.decision == "continue" else "pilot-continuation-criteria-failed",
        )
        return _run_summary(state, ledger.load(), authorization)

    total_ledger = BudgetLedger(root, config, pilot=False)
    state = _run_gepa_phase(
        state,
        config,
        config_path,
        authority,
        authorization,
        adapters,
        total_ledger,
        root,
        baseline_result,
        config.budget.total_candidates,
        monotonic_ns,
    )
    next_operation = _next_gepa_operation(config, adapters)
    if len(state.gepa_result_ids) >= config.budget.total_candidates:
        status, reason = "complete", "candidate-ceiling-reached"
    elif not total_ledger.can_fit(next_operation):
        status, reason = "budget-limited", "next-operation-exceeds-total-ceiling"
    else:
        status, reason = "complete", "optimizer-search-exhausted"
    state = _write_state(
        root,
        config.run_id,
        status,
        state.baseline_result_id,
        state.bootstrap_result_ids,
        state.gepa_result_ids,
        state.authorization_ids,
        state.pilot_checkpoint,
        reason,
    )
    return _run_summary(state, total_ledger.load(), authorization)


def _run_gepa_phase(
    state: RunState,
    config: OptimizationConfig,
    config_path: Path,
    authority: VerifiedAuthority,
    authorization: ExecutionAuthority,
    adapters: ExecutionAdapters,
    ledger: BudgetLedger,
    root: Path,
    baseline_result: CandidateResult,
    candidate_limit: int,
    monotonic_ns,
) -> RunState:
    while len(state.gepa_result_ids) < candidate_limit:
        if not ledger.can_fit(_next_gepa_operation(config, adapters)):
            break
        existing = [
            baseline_result,
            *[_result_by_id(root, value) for value in state.gepa_result_ids],
        ]
        parent_result = max(existing, key=lambda item: item.validation_metric)
        parent = _package_by_id(root, parent_result.candidate_id)
        feedback = _aggregate_feedback(root, existing)
        ordinal = len(state.gepa_result_ids) + 1
        proposed = _propose(
            parent,
            "gepa",
            ordinal,
            feedback,
            config,
            authority,
            authorization,
            adapters,
            ledger,
            root,
            monotonic_ns,
        )
        if proposed.search_exhausted or proposed.candidate is None:
            break
        result = _evaluate(
            proposed.candidate,
            config,
            config_path,
            authority,
            authorization,
            adapters.candidate,
            ledger,
            root,
            optimizer_latency_ms=proposed.optimizer_latency_ms,
        )
        _complete_proposal_trial(
            root,
            "gepa",
            ordinal,
            result,
            ledger,
            proposed.optimizer_latency_ms,
            proposed.optimizer_usage,
        )
        state = _write_state(
            root,
            config.run_id,
            "continuing" if state.pilot_checkpoint else "in-progress",
            state.baseline_result_id,
            state.bootstrap_result_ids,
            [*state.gepa_result_ids, result.result_id],
            state.authorization_ids,
            state.pilot_checkpoint,
        )
    return state


def _authorize(
    root: Path,
    config: OptimizationConfig,
    measured: ImplementationIdentity,
    *,
    resume: bool,
) -> ExecutionAuthority:
    if measured.dirty_tracked or measured.commit != config.application_commit:
        raise ValueError("optimizer execution requires the pinned clean application commit")
    destination = root / "authorizations"
    ordinal = len(list(destination.glob("*.json"))) + 1 if destination.exists() else 1
    payload = {
        "format_version": 1,
        "mode": "resume" if resume else "optimize",
        "authorization_ordinal": ordinal,
        "run_id": config.run_id,
        "application_commit": measured.commit,
        "config_sha256": optimization_config_identity(config),
        "development_manifest_sha256": config.development_manifest_sha256,
        "train_manifest_sha256": config.train_manifest.sha256,
        "validation_manifest_sha256": config.validation_manifest.sha256,
        "model_artifact_sha256": {
            model.id: candidate_model_identity(model) for model in config.candidate_models
        },
        "proposer_identity_sha256": proposer_identity(config.proposer),
        "optimizer_identity_sha256": optimizer_framework_identity(config),
        "budget_sha256": digest(config.budget.model_dump(mode="json")),
    }
    authority = ExecutionAuthority(**payload, authority_sha256=digest(payload))
    path = destination / f"{ordinal:04d}.json"
    atomic_json(path, authority.model_dump(mode="json"))
    consumed = root / "consumed-authorizations" / f"{authority.authority_sha256}.json"
    if consumed.exists():
        raise ValueError("optimizer execution authority was already consumed")
    atomic_json(
        consumed,
        {"authority_sha256": authority.authority_sha256, "run_id": config.run_id},
    )
    return authority


def _next_gepa_operation(config: OptimizationConfig, adapters: ExecutionAdapters) -> UsageCounters:
    values = [UsageCounters(candidates=1), _usage_counters(adapters.optimizer.reservation("gepa"))]
    for scope in ("train", "validation"):
        for model_id in _model_ids(config):
            values.append(_usage_counters(adapters.candidate.reservation(scope, model_id)))
    result = UsageCounters()
    for value in values:
        result = UsageCounters(
            **{
                name: getattr(result, name) + getattr(value, name)
                for name in UsageCounters.model_fields
            }
        )
    return result


def _pilot_checkpoint(
    state: RunState,
    config: OptimizationConfig,
    adapters: ExecutionAdapters,
    ledger: BudgetLedger,
    root: Path,
    baseline: CandidateResult,
) -> PilotCheckpoint:
    results = [_result_by_id(root, value) for value in state.gepa_result_ids]
    baseline_package = _package_by_id(root, baseline.candidate_id)
    baseline_prompt_set = tuple(baseline_package.prompts[task].sha256 for task in TASK_ORDER)
    safety = True
    prompt_sets: list[tuple[str, ...]] = []
    for result in results:
        package = _package_by_id(root, result.candidate_id)
        current = TrialStore(root).current(result.trial_id)
        safety = safety and bool(
            current is not None
            and current.status == "complete"
            and current.result_id == result.result_id
            and result.accounting.terminal_invocations == result.accounting.expected_invocations
            and result.request_envelope.fits_context
        )
        prompt_sets.append(tuple(package.prompts[task].sha256 for task in TASK_ORDER))
    no_worse = any(
        result.validation_metric.total_valid >= baseline.validation_metric.total_valid
        and result.validation_metric.worst_model_valid
        >= baseline.validation_metric.worst_model_valid
        and result.validation_metric.minimum_task_valid
        >= baseline.validation_metric.minimum_task_valid
        for result in results
    )
    distinct_private = (
        bool(results)
        and all(prompt_set != baseline_prompt_set for prompt_set in prompt_sets)
        and len(prompt_sets) == len(set(prompt_sets))
        and all(result.privacy.eligible for result in results)
    )
    total_ledger = BudgetLedger(root, config, pilot=False)
    next_operation = _next_gepa_operation(config, adapters)
    capacity = min(
        total_ledger.achievable_operations(next_operation),
        config.budget.total_candidates - len(results),
    )
    projected = capacity > 0 and total_ledger.can_fit(next_operation)
    budget_state = ledger.load()
    payload = {
        "format_version": 1,
        "pilot_gepa_result_ids": list(state.gepa_result_ids),
        "safety_privacy_accounting_resume": safety,
        "validation_no_worse_than_p0": no_worse,
        "distinct_privacy_eligible": distinct_private,
        "projected_costs_within_total_ceilings": projected,
        "decision": "continue" if all((safety, no_worse, distinct_private, projected)) else "stop",
        "achievable_additional_candidates": capacity,
        "budget_state_sha256": budget_state.state_sha256,
    }
    return PilotCheckpoint(**payload, checkpoint_sha256=digest(payload))


def _run_summary(
    state: RunState,
    budget_state,
    authorization: ExecutionAuthority | None,
) -> dict[str, object]:
    return {
        "run_id": state.run_id,
        "status": state.status,
        "baseline_results": 1 if state.baseline_result_id else 0,
        "bootstrap_results": len(state.bootstrap_result_ids),
        "gepa_results": len(state.gepa_result_ids),
        "pilot_checkpoint": (
            state.pilot_checkpoint.model_dump(mode="json") if state.pilot_checkpoint else None
        ),
        "stop_reason": state.stop_reason,
        "authorization_sha256": authorization.authority_sha256 if authorization else None,
        "budget": budget_state.counters.model_dump(mode="json"),
    }


def _propose(
    parent: CandidatePackage,
    optimizer: Literal["bootstrap-few-shot", "gepa"],
    ordinal: int,
    feedback: str,
    config: OptimizationConfig,
    authority: VerifiedAuthority,
    execution_authority: ExecutionAuthority,
    adapters: ExecutionAdapters,
    ledger: BudgetLedger,
    root: Path,
    monotonic_ns,
) -> ProposedCandidate:
    candidate_reservation = None
    if optimizer == "gepa":
        candidate_reservation = ledger.reserve("candidate", candidate_count=1)
    requested = adapters.optimizer.reservation(optimizer)
    reservation = ledger.reserve(
        "proposer" if requested.proposer_calls else "task",
        task_calls=requested.task_calls,
        proposer_calls=requested.proposer_calls,
        input_tokens=requested.input_tokens,
        output_tokens=requested.output_tokens,
        compute_hours=requested.compute_hours,
        compute_cost_usd=requested.compute_cost_usd,
        retries=requested.retries,
    )
    started = monotonic_ns()
    try:
        proposal = (
            adapters.optimizer.bootstrap(parent, authority)
            if optimizer == "bootstrap-few-shot"
            else adapters.optimizer.gepa(parent, authority, feedback, ordinal)
        )
    except Exception as exc:
        elapsed_ms = max(0, (monotonic_ns() - started) // 1_000_000)
        if candidate_reservation is not None:
            ledger.reconcile(candidate_reservation.reservation_id, UsageCounters())
        measured_usage = None
        failure_category = type(exc).__name__
        if isinstance(exc, OptimizerOperationError):
            if exc.usage is not None:
                measured_usage = _with_optimizer_timing(exc.usage, requested, config, elapsed_ms)
            if exc.usage_complete and measured_usage is not None:
                ledger.reconcile(
                    reservation.reservation_id,
                    _usage_counters(measured_usage),
                    interrupted=True,
                )
            elif measured_usage is not None:
                ledger.retain_interrupted(reservation.reservation_id)
            failure_category = exc.failure_category
        TrialStore(root).append(
            f"proposal-{optimizer}-{ordinal:04d}",
            "interrupted",
            _proposal_accounting(ledger, measured_usage),
            candidate_id=parent.candidate_id,
            failure_category=failure_category,
            optimizer_wall_ms=elapsed_ms,
        )
        if measured_usage is None:
            ledger.retain_interrupted(reservation.reservation_id)
        raise
    elapsed_ms = max(0, (monotonic_ns() - started) // 1_000_000)
    measured_usage = _with_optimizer_timing(proposal.usage, requested, config, elapsed_ms)
    ledger.reconcile(reservation.reservation_id, _usage_counters(measured_usage))
    if proposal.search_exhausted:
        if candidate_reservation is not None:
            ledger.reconcile(candidate_reservation.reservation_id, UsageCounters())
        TrialStore(root).append(
            f"proposal-{optimizer}-{ordinal:04d}",
            "failed",
            _proposal_accounting(ledger, measured_usage),
            candidate_id=parent.candidate_id,
            failure_category="search-exhausted",
            optimizer_wall_ms=elapsed_ms,
        )
        return ProposedCandidate(None, elapsed_ms, True, measured_usage)
    candidate = mutate_package(
        parent,
        proposal.prompts,
        optimizer=optimizer,
        proposer_id=config.proposer.id if proposal.usage.proposer_calls else None,
        mutation_ordinal=ordinal,
        strategy=proposal.strategy,
        demonstrations=proposal.demonstrations,
    )
    if optimizer == "gepa" and all(
        candidate.prompts[task].sha256 == parent.prompts[task].sha256 for task in TASK_ORDER
    ):
        if candidate_reservation is not None:
            ledger.reconcile(candidate_reservation.reservation_id, UsageCounters())
        TrialStore(root).append(
            f"proposal-{optimizer}-{ordinal:04d}",
            "failed",
            _proposal_accounting(ledger, measured_usage),
            candidate_id=parent.candidate_id,
            failure_category="no-distinct-prompt-package",
            optimizer_wall_ms=elapsed_ms,
        )
        return ProposedCandidate(None, elapsed_ms, True, measured_usage)
    if candidate_reservation is not None:
        ledger.reconcile(candidate_reservation.reservation_id, candidate_reservation.reserved)
    write_package(root / "candidates" / f"{candidate.candidate_id}.json", candidate)
    return ProposedCandidate(candidate, elapsed_ms, False, measured_usage)


def _with_optimizer_timing(
    usage: AdapterUsage,
    requested: AdapterReservation,
    config: OptimizationConfig,
    elapsed_ms: int,
) -> AdapterUsage:
    timing_update: dict[str, int | float] = {"latency_ms": elapsed_ms}
    if requested.compute_hours:
        elapsed_hours = elapsed_ms / 3_600_000
        timing_update.update(
            compute_hours=elapsed_hours,
            compute_cost_usd=elapsed_hours
            * (config.budget.compute_cost_usd / config.budget.total_compute_hours),
        )
    return usage.model_copy(update=timing_update)


def _proposal_accounting(ledger: BudgetLedger, usage: AdapterUsage | None) -> dict[str, object]:
    accounting: dict[str, object] = ledger.load().counters.model_dump(mode="json")
    if usage is not None:
        accounting["optimizer_usage"] = usage.model_dump(mode="json")
    return accounting


def _evaluate(
    candidate: CandidatePackage,
    config: OptimizationConfig,
    config_path: Path,
    authority: VerifiedAuthority,
    execution_authority: ExecutionAuthority,
    adapter: CandidateAdapter,
    ledger: BudgetLedger,
    root: Path,
    optimizer_latency_ms: int = 0,
) -> CandidateResult:
    write_package(root / "candidates" / f"{candidate.candidate_id}.json", candidate)
    trial_id = f"candidate-{candidate.candidate_id[:16]}"
    batches: list[EvaluationBatch] = []
    try:
        for scope in ("train", "validation"):
            for model_id in _model_ids(config):
                requested = adapter.reservation(scope, model_id)
                reservation = ledger.reserve(
                    "task",
                    task_calls=requested.task_calls,
                    proposer_calls=requested.proposer_calls,
                    input_tokens=requested.input_tokens,
                    output_tokens=requested.output_tokens,
                    compute_hours=requested.compute_hours,
                    compute_cost_usd=requested.compute_cost_usd,
                    retries=requested.retries,
                )
                try:
                    batch = adapter.evaluate(candidate, scope, model_id, authority)
                except Exception:
                    ledger.reconcile(reservation.reservation_id, None, interrupted=True)
                    raise
                _validate_batch(batch, scope, model_id, authority, config)
                ledger.reconcile(reservation.reservation_id, _usage_counters(batch.usage))
                batches.append(batch)
    except Exception as exc:
        TrialStore(root).append(
            trial_id,
            "interrupted",
            ledger.load().counters.model_dump(mode="json"),
            candidate_id=candidate.candidate_id,
            failure_category=type(exc).__name__,
        )
        raise
    try:
        result = _build_result(
            candidate,
            config,
            config_path,
            authority,
            execution_authority,
            batches,
            trial_id,
            root,
            optimizer_latency_ms,
        )
    except Exception as exc:
        TrialStore(root).append(
            trial_id,
            "interrupted",
            ledger.load().counters.model_dump(mode="json"),
            candidate_id=candidate.candidate_id,
            failure_category=type(exc).__name__,
        )
        raise
    write_result(root / "results" / f"{result.result_id}.json", result)
    TrialStore(root).append(
        trial_id,
        "complete",
        result.accounting.model_dump(mode="json"),
        candidate_id=candidate.candidate_id,
        result_id=result.result_id,
    )
    return result


def _validate_batch(
    batch: EvaluationBatch,
    scope: str,
    model_id: str,
    authority: VerifiedAuthority,
    config: OptimizationConfig,
) -> None:
    manifest = authority.train if scope == "train" else authority.validation
    limit = (
        config.evaluation_train_conversation_limit
        if scope == "train"
        else config.evaluation_validation_conversation_limit
    )
    expected_aliases = {
        f"c{entry.authority_index:03d}--{task}"
        for entry in manifest.ordered_conversations[:limit]
        for task in TASK_ORDER
    }
    aliases = [item.alias for item in batch.outcomes]
    if batch.scope != scope or batch.model_id != model_id:
        raise ValueError("candidate adapter batch identity mismatch")
    if len(aliases) != len(set(aliases)) or set(aliases) != expected_aliases:
        raise ValueError("candidate adapter batch case accounting mismatch")
    if any(item.model_id != model_id or not item.terminal for item in batch.outcomes):
        raise ValueError("candidate adapter returned non-terminal or foreign outcomes")
    if (
        batch.usage.retries > len(expected_aliases)
        or batch.usage.task_calls != len(expected_aliases) + batch.usage.retries
    ):
        raise ValueError("candidate adapter usage does not match terminal cases")


def _build_result(
    candidate: CandidatePackage,
    config: OptimizationConfig,
    config_path: Path,
    authority: VerifiedAuthority,
    execution_authority: ExecutionAuthority,
    batches: list[EvaluationBatch],
    trial_id: str,
    root: Path,
    optimizer_latency_ms: int,
) -> CandidateResult:
    train = [item for batch in batches if batch.scope == "train" for item in batch.outcomes]
    validation = [
        item for batch in batches if batch.scope == "validation" for item in batch.outcomes
    ]
    model_ids = _model_ids(config)
    train_metric = _metric(candidate, train, model_ids)
    validation_metric = _metric(candidate, validation, model_ids)
    model_valid = {
        model: sum(item.valid for item in validation if item.model_id == model)
        for model in model_ids
    }
    task_valid = {
        task: sum(item.valid for item in validation if item.task == task) for task in TASK_ORDER
    }
    private_texts = []
    exact_values = []
    for source in authority.inputs:
        private_texts.extend((source.overview.transcript, source.recent.transcript))
        exact_values.append(source.source_title)
        exact_values.extend(str(value) for value in source.overview.selected_message_ids)
        exact_values.extend(str(value) for value in source.recent.selected_message_ids)
    for reference in authority.references.values():
        private_texts.append(json.dumps(reference.output, sort_keys=True))
    privacy = scan_package(candidate, private_texts, exact_values=exact_values)
    privacy_payload = privacy.model_dump(mode="json", exclude={"findings"})
    privacy_evidence = PrivacyEvidence(
        **privacy_payload,
        evidence_sha256=digest(privacy.model_dump(mode="json")),
    )
    prompt_max = max(item.token_estimate for item in candidate.prompts.values())
    from chat_chronicle.ai_config import load_task_catalog

    from .request_envelope import estimate_request_envelope

    tasks = load_task_catalog(resolve_config_path(config_path, config.paths.accepted_task_catalog))
    request_envelope = estimate_request_envelope(candidate, tasks, authority)
    expected = len(train) + len(validation)
    usage = [batch.usage for batch in batches]
    accounting = CandidateAccounting(
        task_invocations=sum(item.task_calls for item in usage),
        proposer_calls=0,
        infrastructure_retries=sum(item.retries for item in usage),
        terminal_invocations=sum(item.terminal for item in train + validation),
        expected_invocations=expected,
        failures=dict(
            Counter(
                diagnostic.category
                for outcome in train + validation
                for diagnostic in outcome.diagnostics
            )
        ),
        latency_ms=sum(item.latency_ms for item in usage),
        optimizer_latency_ms=optimizer_latency_ms,
        usage={
            "input_tokens": sum(item.input_tokens for item in usage),
            "output_tokens": sum(item.output_tokens for item in usage),
            "reasoning_tokens": sum(item.reasoning_tokens for item in usage),
            "provider_cost_usd": sum(item.provider_cost_usd for item in usage),
        },
    )
    result_authority = ResultAuthority(
        run_id=config.run_id,
        application_commit=execution_authority.application_commit,
        config_sha256=execution_authority.config_sha256,
        train_manifest_sha256=execution_authority.train_manifest_sha256,
        validation_manifest_sha256=execution_authority.validation_manifest_sha256,
        model_artifact_sha256=execution_authority.model_artifact_sha256,
        proposer_identity_sha256=execution_authority.proposer_identity_sha256,
        optimizer_identity_sha256=execution_authority.optimizer_identity_sha256,
        execution_authority_sha256=execution_authority.authority_sha256,
    )
    payload = {
        "format_version": 1,
        "candidate_id": candidate.candidate_id,
        "authority": result_authority.model_dump(mode="json"),
        "train_metric": train_metric.model_dump(mode="json"),
        "validation_metric": validation_metric.model_dump(mode="json"),
        "validation_model_valid": model_valid,
        "validation_task_valid": task_valid,
        "prompt_token_max": prompt_max,
        "request_envelope": request_envelope.model_dump(mode="json"),
        "prompt_fits_context": request_envelope.fits_context,
        "privacy": privacy_evidence.model_dump(mode="json"),
        "accounting": accounting.model_dump(mode="json"),
        "trial_id": trial_id,
    }
    return CandidateResult(result_id=result_identity(payload), **payload)


def _metric(
    candidate: CandidatePackage, outcomes: list[CaseOutcome], model_ids: list[str]
) -> MetricVector:
    model_counts = Counter(item.model_id for item in outcomes if item.valid)
    task_counts = Counter(item.task for item in outcomes if item.valid)
    semantic = sum(item.semantic_agreement for item in outcomes) / len(outcomes) if outcomes else 0
    return MetricVector(
        total_valid=sum(item.valid for item in outcomes),
        worst_model_valid=min(model_counts.get(model_id, 0) for model_id in model_ids),
        minimum_task_valid=min(task_counts.get(task, 0) for task in TASK_ORDER),
        semantic_agreement=semantic,
        complete_package_uts=None,
        prompt_tokens=sum(item.token_estimate for item in candidate.prompts.values()),
        candidate_id=candidate.candidate_id,
    )


def _usage_counters(value: AdapterUsage | AdapterReservation) -> UsageCounters:
    return UsageCounters(
        task_invocations=value.task_calls,
        proposer_calls=value.proposer_calls,
        infrastructure_retries=getattr(value, "retries", 0),
        proposer_input_tokens=value.input_tokens if value.proposer_calls else 0,
        proposer_output_tokens=value.output_tokens if value.proposer_calls else 0,
        compute_hours=value.compute_hours,
        proposer_cost_usd=0,
        compute_cost_usd=value.compute_cost_usd,
    )


def _aggregate_feedback(root: Path, results: list[CandidateResult]) -> str:
    # Persisted results contain only aggregate failure counts, never raw private outputs.
    latest = max(results, key=lambda item: item.validation_metric)
    diagnostics = [
        Diagnostic.model_validate(
            {"category": category, "schema_path": "$", "observed": f"count:{count}"}
        )
        for category, count in latest.accounting.failures.items()
    ]
    return render_feedback(diagnostics)


def _complete_proposal_trial(
    root: Path,
    optimizer: Literal["bootstrap-few-shot", "gepa"],
    ordinal: int,
    result: CandidateResult,
    ledger: BudgetLedger,
    optimizer_wall_ms: int,
    optimizer_usage: AdapterUsage,
) -> None:
    """Close the append-only proposal trace after its evaluated result is durable."""
    TrialStore(root).append(
        f"proposal-{optimizer}-{ordinal:04d}",
        "complete",
        _proposal_accounting(ledger, optimizer_usage),
        candidate_id=result.candidate_id,
        result_id=result.result_id,
        optimizer_wall_ms=optimizer_wall_ms,
    )


def _write_state(
    root: Path,
    run_id: str,
    status: Literal[
        "in-progress",
        "pilot-complete",
        "pilot-no-improvement",
        "continuing",
        "complete",
        "budget-limited",
        "no-improvement",
    ],
    baseline_result_id: str | None,
    bootstrap_result_ids: list[str],
    gepa_result_ids: list[str],
    authorization_ids: list[str],
    pilot_checkpoint: PilotCheckpoint | None = None,
    stop_reason: str | None = None,
) -> RunState:
    payload = {
        "format_version": 2,
        "run_id": run_id,
        "status": status,
        "baseline_result_id": baseline_result_id,
        "bootstrap_result_ids": bootstrap_result_ids,
        "gepa_result_ids": gepa_result_ids,
        "authorization_ids": authorization_ids,
        "pilot_checkpoint": (
            pilot_checkpoint.model_dump(mode="json") if pilot_checkpoint else None
        ),
        "stop_reason": stop_reason,
    }
    state = RunState(**payload, state_sha256=digest(payload))
    atomic_json(root / "run-state.json", state.model_dump(mode="json"))
    return state


def _load_state(root: Path) -> RunState | None:
    path = root / "run-state.json"
    return RunState.model_validate_json(path.read_text(encoding="utf-8")) if path.exists() else None


def _result_by_id(root: Path, result_id: str) -> CandidateResult:
    return read_result(root / "results" / f"{result_id}.json")


def _package_by_id(root: Path, candidate_id: str) -> CandidatePackage:
    from .package import read_package

    return read_package(root / "candidates" / f"{candidate_id}.json")


def _verify_execution_inputs(config: OptimizationConfig, config_path: Path) -> None:
    catalog = resolve_config_path(config_path, config.paths.accepted_task_catalog)
    if hashlib.sha256(catalog.read_bytes()).hexdigest() != config.accepted_task_catalog_sha256:
        raise ValueError("accepted task catalog hash mismatch")
    for model in config.candidate_models:
        if model.credential_mode == "local-endpoint":
            assert model.artifact_path is not None and model.artifact_sha256 is not None
            artifact = resolve_config_path(config_path, model.artifact_path)
            if hashlib.sha256(artifact.read_bytes()).hexdigest() != model.artifact_sha256:
                raise ValueError(f"optimizer {model.id} artifact hash mismatch")
    verify_compatibility()


def _model_ids(config: OptimizationConfig) -> list[str]:
    return [model.id for model in config.candidate_models]
