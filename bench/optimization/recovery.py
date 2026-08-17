"""Network-free historical-result recovery and GEPA-readiness verification."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from bench.implementation import ImplementationIdentity, measure_implementation
from bench.io import atomic_json, digest
from bench.models import StrictModel

from .budget import BudgetLedger
from .execution import ExecutionAuthority, RunState
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
    CandidatePackage,
    CandidateResult,
    ResultAuthority,
    baseline_package,
    read_package,
)
from .privacy import SCANNER_VERSION
from .trials import TrialAttempt, TrialStore


class HistoricalResultResolution(StrictModel):
    role: Literal["p0", "bootstrap"]
    result_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    candidate_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_authority_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class RecoveryReadiness(StrictModel):
    """Stable ignored checkpoint proving the recovered no-call boundary."""

    format_version: Literal[1] = 1
    run_id: str
    canonical_state_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    immutable_experiment_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    budget_state_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    authorization_ids: list[str]
    results: list[HistoricalResultResolution]
    bootstrap_disposition: Literal["complete-non-promotable"]
    bootstrap_disposition_basis: Literal["manager-policy"]
    bootstrap_disposition_result_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    gepa_parent_result_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    gepa_attempts: Literal[0] = 0
    gepa_results: Literal[0] = 0
    proposer_calls: Literal[0] = 0
    recovery_provider_calls: Literal[0] = 0
    recovery_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def valid_hash(self) -> RecoveryReadiness:
        if digest(self.model_dump(mode="json", exclude={"recovery_sha256"})) != (
            self.recovery_sha256
        ):
            raise ValueError("optimizer recovery readiness hash mismatch")
        roles = [item.role for item in self.results]
        if roles != ["p0", "bootstrap"]:
            raise ValueError("optimizer recovery requires P0 then Bootstrap result membership")
        if self.gepa_parent_result_id != self.results[0].result_id:
            raise ValueError("optimizer recovery must select P0 as the GEPA parent")
        if self.bootstrap_disposition_result_id != self.results[1].result_id:
            raise ValueError(
                "optimizer recovery Bootstrap disposition must bind its recovered result"
            )
        return self


def recover_gepa_readiness(
    config_path: Path,
    *,
    identity_probe=measure_implementation,
) -> dict[str, object]:
    """Recover P0/Bootstrap membership without adapters, credentials, or calls."""

    config = load_optimization_config(config_path)
    measured: ImplementationIdentity = identity_probe()
    if measured.dirty_tracked or measured.commit != config.application_commit:
        raise ValueError("optimizer recovery requires the pinned clean application commit")
    root = resolve_config_path(config_path, config.paths.run_root)
    state = _load_state(root)
    if state.run_id != config.run_id:
        raise ValueError("optimizer recovery run identity mismatch")
    if state.status != "in-progress" or state.pilot_checkpoint is not None:
        raise ValueError("optimizer recovery requires the pre-GEPA in-progress state")
    if state.gepa_result_ids or _has_gepa_trial_evidence(root):
        raise ValueError("optimizer recovery is blocked by existing GEPA evidence")

    authorizations = load_consumed_authorizations(root, config)
    expected_authorization_ids = [item.authority_sha256 for item in authorizations]
    if len(state.authorization_ids) != len(set(state.authorization_ids)):
        raise ValueError("optimizer run state contains duplicate authorization references")
    if state.authorization_ids != expected_authorization_ids:
        raise ValueError("optimizer run authorization membership is missing, dangling, or stale")

    budget = BudgetLedger(root, config, pilot=False).load()
    if budget.run_id != config.run_id:
        raise ValueError("optimizer recovery budget run identity mismatch")
    if budget.counters.proposer_calls:
        raise ValueError("optimizer recovery is blocked by existing proposer usage")

    results, packages = _historical_results(root, config, state, authorizations)
    p0 = results["p0"]
    bootstrap = results["bootstrap"]
    p0_package = packages["p0"]
    bootstrap_package = packages["bootstrap"]
    _verify_candidate_contracts(config_path, config, p0_package, bootstrap_package)
    _verify_trial_authority(root, p0, bootstrap)

    if state.baseline_result_id != p0.result_id:
        raise ValueError("optimizer recovery P0 run-state membership is inconsistent")
    if state.bootstrap_result_ids not in ([], [bootstrap.result_id]):
        raise ValueError("optimizer recovery Bootstrap run-state membership is inconsistent")

    state_payload = state.model_dump(mode="json", exclude={"state_sha256"})
    state_payload["bootstrap_result_ids"] = [bootstrap.result_id]
    recovered_state = RunState(**state_payload, state_sha256=digest(state_payload))

    resolutions = [
        _resolution("p0", p0, authorizations),
        _resolution("bootstrap", bootstrap, authorizations),
    ]
    readiness_payload = {
        "format_version": 1,
        "run_id": config.run_id,
        "canonical_state_sha256": recovered_state.state_sha256,
        "immutable_experiment_sha256": immutable_experiment_identity(config),
        "budget_state_sha256": budget.state_sha256,
        "authorization_ids": expected_authorization_ids,
        "results": [item.model_dump(mode="json") for item in resolutions],
        "bootstrap_disposition": "complete-non-promotable",
        "bootstrap_disposition_basis": "manager-policy",
        "bootstrap_disposition_result_id": bootstrap.result_id,
        "gepa_parent_result_id": p0.result_id,
        "gepa_attempts": 0,
        "gepa_results": 0,
        "proposer_calls": 0,
        "recovery_provider_calls": 0,
    }
    readiness = RecoveryReadiness(**readiness_payload, recovery_sha256=digest(readiness_payload))

    atomic_json(root / "run-state.json", recovered_state.model_dump(mode="json"))
    atomic_json(
        root / "checkpoints" / "gepa-readiness.json",
        readiness.model_dump(mode="json"),
    )
    return {
        "status": "gepa-ready",
        "p0_results": 1,
        "bootstrap_results": 1,
        "gepa_results": 0,
        "gepa_attempts": 0,
        "gepa_parent": "p0",
        "bootstrap_disposition": readiness.bootstrap_disposition,
        "bootstrap_disposition_basis": readiness.bootstrap_disposition_basis,
        "historical_authorizations": len(authorizations),
        "recovery_sha256": readiness.recovery_sha256,
        "recovery_provider_calls": 0,
    }


def resolve_result_authorization(
    root: Path,
    result: CandidateResult,
    config: OptimizationConfig,
    *,
    authorization_ids: list[str] | None = None,
) -> ExecutionAuthority:
    """Resolve a historical result to one exact consumed execution authority."""

    authorizations = load_consumed_authorizations(root, config)
    if authorization_ids is not None:
        if len(authorization_ids) != len(set(authorization_ids)):
            raise ValueError("optimizer run state contains duplicate authorization references")
        known = [item.authority_sha256 for item in authorizations]
        if authorization_ids != known:
            raise ValueError(
                "optimizer run authorization membership is missing, dangling, or stale"
            )
    matches = [item for item in authorizations if _authority_matches(result.authority, item)]
    if len(matches) != 1:
        _raise_referenced_authority_mismatch(result.authority, authorizations)
        raise ValueError(
            "optimizer result must resolve to exactly one consumed execution authorization"
        )
    return matches[0]


def load_consumed_authorizations(
    root: Path, config: OptimizationConfig
) -> list[ExecutionAuthority]:
    authorization_root = root / "authorizations"
    consumed_root = root / "consumed-authorizations"
    paths = sorted(authorization_root.glob("*.json"))
    if not paths:
        raise ValueError("optimizer execution authorization history is missing")
    authorizations: list[ExecutionAuthority] = []
    for expected_ordinal, path in enumerate(paths, start=1):
        authority = ExecutionAuthority.model_validate_json(path.read_text(encoding="utf-8"))
        if path.stem != f"{expected_ordinal:04d}" or authority.authorization_ordinal != (
            expected_ordinal
        ):
            raise ValueError("optimizer execution authorization history is stale or misordered")
        _verify_authorization_compatibility(authority, config)
        authorizations.append(authority)
    hashes = [item.authority_sha256 for item in authorizations]
    if len(hashes) != len(set(hashes)):
        raise ValueError("optimizer execution authorization history is duplicated")
    consumed_paths = sorted(consumed_root.glob("*.json"))
    if {path.stem for path in consumed_paths} != set(hashes):
        raise ValueError("optimizer consumed authorization history is missing or dangling")
    for path in consumed_paths:
        value = _read_consumed(path)
        if value != {"authority_sha256": path.stem, "run_id": config.run_id}:
            raise ValueError("optimizer consumed authorization record is stale or foreign")
    return authorizations


def immutable_experiment_identity(config: OptimizationConfig) -> str:
    value = config.model_dump(mode="json", exclude={"application_commit"})
    return digest(value)


def _verify_authorization_compatibility(
    authority: ExecutionAuthority, config: OptimizationConfig
) -> None:
    if authority.run_id != config.run_id:
        raise ValueError("optimizer execution authorization belongs to a foreign run")
    historical = config.model_copy(update={"application_commit": authority.application_commit})
    if authority.config_sha256 != optimization_config_identity(historical):
        raise ValueError(
            "optimizer execution authorization differs from immutable experiment configuration"
        )
    expected = {
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
    for field, value in expected.items():
        if getattr(authority, field) != value:
            raise ValueError(f"optimizer execution authorization immutable {field} mismatch")


def _historical_results(
    root: Path,
    config: OptimizationConfig,
    state: RunState,
    authorizations: list[ExecutionAuthority],
) -> tuple[dict[str, CandidateResult], dict[str, CandidatePackage]]:
    result_paths = sorted((root / "results").glob("*.json"))
    if not result_paths:
        raise ValueError("optimizer recovery result evidence is missing")
    results: dict[str, CandidateResult] = {}
    packages: dict[str, CandidatePackage] = {}
    for path in result_paths:
        result = CandidateResult.model_validate_json(path.read_text(encoding="utf-8"))
        if path.stem != result.result_id:
            raise ValueError("optimizer result filename identity mismatch")
        package_path = root / "candidates" / f"{result.candidate_id}.json"
        if not package_path.exists():
            raise ValueError("optimizer result candidate package is missing")
        package = read_package(package_path)
        if package.candidate_id != result.candidate_id:
            raise ValueError("optimizer result candidate identity mismatch")
        if package.lineage.optimizer == "gepa":
            raise ValueError("optimizer recovery is blocked by existing GEPA evidence")
        role = package.lineage.optimizer
        if role not in {"p0", "bootstrap-few-shot"}:
            raise ValueError("optimizer recovery encountered foreign result lineage")
        key = "p0" if role == "p0" else "bootstrap"
        if key in results:
            raise ValueError(f"optimizer recovery has ambiguous {key} result evidence")
        if result.privacy.scanner_version != SCANNER_VERSION:
            raise ValueError("optimizer result privacy scanner identity mismatch")
        matches = [item for item in authorizations if _authority_matches(result.authority, item)]
        if len(matches) != 1:
            raise ValueError(
                "optimizer result must resolve to exactly one consumed execution authorization"
            )
        if matches[0].authority_sha256 not in state.authorization_ids:
            raise ValueError("optimizer result authorization is outside run-state membership")
        results[key] = result
        packages[key] = package
    if set(results) != {"p0", "bootstrap"}:
        raise ValueError("optimizer recovery requires exactly one P0 and one Bootstrap result")
    for path in sorted((root / "candidates").glob("*.json")):
        package = read_package(path)
        if package.lineage.optimizer == "gepa":
            raise ValueError("optimizer recovery is blocked by existing GEPA evidence")
    return results, packages


def _verify_candidate_contracts(
    config_path: Path,
    config: OptimizationConfig,
    p0: CandidatePackage,
    bootstrap: CandidatePackage,
) -> None:
    expected = baseline_package(
        resolve_config_path(config_path, config.paths.accepted_task_catalog)
    )
    if p0 != expected:
        raise ValueError("optimizer recovery P0 candidate identity or contract mismatch")
    if (
        bootstrap.contracts != p0.contracts
        or bootstrap.context_window != p0.context_window
        or bootstrap.lineage.parent_id != p0.candidate_id
        or bootstrap.lineage.optimizer != "bootstrap-few-shot"
    ):
        raise ValueError("optimizer recovery Bootstrap candidate contract or lineage mismatch")


def _verify_trial_authority(root: Path, p0: CandidateResult, bootstrap: CandidateResult) -> None:
    store = TrialStore(root)
    for result in (p0, bootstrap):
        current = store.current(result.trial_id)
        if (
            current is None
            or current.status != "complete"
            or current.candidate_id != result.candidate_id
            or current.result_id != result.result_id
        ):
            raise ValueError("optimizer result terminal trial authority is inconsistent")
    matching: list[TrialAttempt] = []
    for directory in sorted((root / "trials").glob("proposal-bootstrap-few-shot-*")):
        attempts = store.attempts(directory.name)
        current = attempts[-1] if attempts else None
        if (
            current is not None
            and current.status == "complete"
            and current.candidate_id == bootstrap.candidate_id
            and current.result_id == bootstrap.result_id
        ):
            matching.append(current)
    if len(matching) != 1:
        raise ValueError("optimizer Bootstrap result must resolve to one complete proposal trial")


def _resolution(
    role: Literal["p0", "bootstrap"],
    result: CandidateResult,
    authorizations: list[ExecutionAuthority],
) -> HistoricalResultResolution:
    matches = [item for item in authorizations if _authority_matches(result.authority, item)]
    if len(matches) != 1:
        raise ValueError(
            "optimizer result must resolve to exactly one consumed execution authorization"
        )
    return HistoricalResultResolution(
        role=role,
        result_id=result.result_id,
        candidate_id=result.candidate_id,
        execution_authority_sha256=matches[0].authority_sha256,
    )


def _result_authority(authority: ExecutionAuthority) -> ResultAuthority:
    return ResultAuthority(
        run_id=authority.run_id,
        application_commit=authority.application_commit,
        config_sha256=authority.config_sha256,
        train_manifest_sha256=authority.train_manifest_sha256,
        validation_manifest_sha256=authority.validation_manifest_sha256,
        model_artifact_sha256=authority.model_artifact_sha256,
        proposer_identity_sha256=authority.proposer_identity_sha256,
        optimizer_identity_sha256=authority.optimizer_identity_sha256,
        execution_authority_sha256=authority.authority_sha256,
    )


def _authority_matches(result: ResultAuthority, authority: ExecutionAuthority) -> bool:
    expected = _result_authority(authority)
    if result.execution_authority_sha256 is not None:
        return result == expected
    return result.model_dump(exclude={"execution_authority_sha256"}) == expected.model_dump(
        exclude={"execution_authority_sha256"}
    )


def _raise_referenced_authority_mismatch(
    result: ResultAuthority, authorizations: list[ExecutionAuthority]
) -> None:
    if result.execution_authority_sha256 is None:
        return
    referenced = [
        item
        for item in authorizations
        if item.authority_sha256 == result.execution_authority_sha256
    ]
    if len(referenced) != 1:
        raise ValueError("optimizer result execution authorization reference is missing")
    expected = _result_authority(referenced[0])
    labels = {
        "run_id": "run identity",
        "application_commit": "application identity",
        "config_sha256": "configuration identity",
        "train_manifest_sha256": "train split identity",
        "validation_manifest_sha256": "validation split identity",
        "model_artifact_sha256": "model artifact identity",
        "proposer_identity_sha256": "proposer identity",
        "optimizer_identity_sha256": "framework identity",
    }
    for field, label in labels.items():
        if getattr(result, field) != getattr(expected, field):
            raise ValueError(f"optimizer result {label} mismatch")


def _read_consumed(path: Path) -> dict[str, object]:
    import json

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("optimizer consumed authorization record is malformed")
    return value


def _has_gepa_trial_evidence(root: Path) -> bool:
    trials = root / "trials"
    return trials.exists() and any(trials.glob("proposal-gepa-*"))


def _load_state(root: Path) -> RunState:
    path = root / "run-state.json"
    if not path.exists():
        raise ValueError("optimizer run state is missing for recovery")
    return RunState.model_validate_json(path.read_text(encoding="utf-8"))
