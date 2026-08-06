"""No-call optimizer preflight, verification, inspection, and shortlist operations."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any

from bench.io import atomic_json, digest
from bench.models import TASK_ORDER
from chat_chronicle.ai_config import load_task_catalog

from .authority import verify_authority
from .budget import BudgetLedger, UsageCounters, enforce_budget
from .compat import verify_compatibility
from .execution import RunState
from .models import (
    load_optimization_config,
    optimization_config_identity,
    proposer_identity,
    resolve_config_path,
)
from .package import (
    CandidatePackage,
    CandidateResult,
    baseline_package,
    read_package,
    read_result,
    write_package,
)
from .privacy import SCANNER_VERSION
from .request_envelope import estimate_request_envelope, verify_demonstration_authority
from .trials import TrialStore


def preflight(config_path: Path, *, check_framework: bool = True) -> dict[str, Any]:
    config = load_optimization_config(config_path)
    catalog = resolve_config_path(config_path, config.paths.accepted_task_catalog)
    if hashlib.sha256(catalog.read_bytes()).hexdigest() != config.accepted_task_catalog_sha256:
        raise ValueError("accepted task catalog hash mismatch")
    baseline_package(catalog)
    authority = verify_authority(config, config_path)
    artifacts = []
    for model in config.candidate_models:
        path = resolve_config_path(config_path, model.artifact_path)
        if hashlib.sha256(path.read_bytes()).hexdigest() != model.artifact_sha256:
            raise ValueError(f"optimizer {model.id} artifact hash mismatch")
        artifacts.append({"id": model.id, "verified": True, "context_window": 8192})
    enforce_budget(config, UsageCounters(), pilot=True)
    result: dict[str, Any] = {
        "valid": True,
        "zero_holdout": (
            len(authority.inputs) == 10
            and len(authority.references) == 40
            and authority.development.role == "development"
        ),
        "development_conversations": authority.development.conversation_count,
        "development_cases": authority.development.expected_case_count,
        "tasks": list(TASK_ORDER),
        "split": [
            {
                "role": manifest.role,
                "conversations": manifest.conversation_count,
                "cases": manifest.expected_case_count,
                "provider_counts": manifest.provider_counts,
                "length_stratum_counts": manifest.length_stratum_counts,
            }
            for manifest in (authority.train, authority.validation)
        ],
        "authority_files": {
            "inputs": len(authority.inputs),
            "references": len(authority.references),
        },
        "artifacts": artifacts,
        "config_sha256": optimization_config_identity(config),
        "ceilings": {
            "pilot_candidates": config.budget.pilot_candidates,
            "total_candidates": config.budget.total_candidates,
            "task_invocations": config.budget.task_invocations,
            "proposer_calls": config.proposer.max_calls,
            "proposer_input_tokens": config.proposer.max_input_tokens,
            "proposer_output_tokens": config.proposer.max_output_tokens,
            "pilot_compute_hours": config.budget.pilot_compute_hours,
            "total_compute_hours": config.budget.total_compute_hours,
            "proposer_cost_usd": config.proposer.max_cost_usd,
            "compute_cost_usd": config.budget.compute_cost_usd,
        },
    }
    if not result["zero_holdout"]:
        raise ValueError("optimizer authority does not prove development-only scope")
    if check_framework:
        result["framework"] = verify_compatibility()
    return result


def dry_run(config_path: Path) -> dict[str, Any]:
    checked = preflight(config_path)
    config = load_optimization_config(config_path)
    catalog = resolve_config_path(config_path, config.paths.accepted_task_catalog)
    package = baseline_package(catalog)
    return {
        "valid": checked["valid"],
        "provider_calls": 0,
        "candidate_id": package.candidate_id,
        "prompt_count": len(package.prompts),
        "contract_count": len(package.contracts),
        "safe_serialization": "json",
    }


def package_baseline(config_path: Path, output: Path) -> dict[str, Any]:
    preflight(config_path)
    config = load_optimization_config(config_path)
    catalog = resolve_config_path(config_path, config.paths.accepted_task_catalog)
    package = baseline_package(catalog)
    write_package(output, package)
    return {"candidate_id": package.candidate_id, "syntax_valid": True, "provider_calls": 0}


def inspect_candidate_syntax(path: Path) -> dict[str, Any]:
    package = read_package(path)
    return {"syntax_valid": True, "candidate_id": package.candidate_id, "provider_calls": 0}


def verify_candidate(config_path: Path, path: Path) -> dict[str, Any]:
    preflight(config_path)
    config = load_optimization_config(config_path)
    root = resolve_config_path(config_path, config.paths.run_root)
    package = read_package(path)
    baseline = baseline_package(
        resolve_config_path(config_path, config.paths.accepted_task_catalog)
    )
    if package.contracts != baseline.contracts or package.context_window != 8192:
        raise ValueError("optimizer candidate differs from accepted P0 contracts")
    state = _load_run_state(root)
    result_ids = [
        value
        for value in [state.baseline_result_id, *state.bootstrap_result_ids, *state.gepa_result_ids]
        if value is not None
    ]
    results = [_read_verified_result(root, value, config) for value in result_ids]
    matches = [result for result in results if result.candidate_id == package.candidate_id]
    if len(matches) != 1:
        raise ValueError("optimizer candidate has missing or ambiguous run result authority")
    result = matches[0]
    authority = verify_authority(config, config_path)
    tasks = load_task_catalog(resolve_config_path(config_path, config.paths.accepted_task_catalog))
    verify_demonstration_authority(package, tasks, authority)
    if result.request_envelope != estimate_request_envelope(package, tasks, authority):
        raise ValueError("optimizer candidate complete request envelope is inconsistent")
    current = TrialStore(root).current(result.trial_id)
    if current is None or current.status != "complete" or current.result_id != result.result_id:
        raise ValueError("optimizer candidate trial authority is missing or inconsistent")
    return {
        "valid": True,
        "candidate_id": package.candidate_id,
        "result_id": result.result_id,
        "privacy_eligible": result.privacy.eligible,
        "terminal_invocations": result.accounting.terminal_invocations,
        "max_request_tokens": result.request_envelope.total_tokens,
        "request_fits_context": result.request_envelope.fits_context,
        "provider_calls": 0,
    }


def inspect_run(config_path: Path) -> dict[str, Any]:
    config = load_optimization_config(config_path)
    root = resolve_config_path(config_path, config.paths.run_root)
    state = _load_run_state(root)
    budget = BudgetLedger(root, config, pilot=False).load()
    records = []
    for path in sorted((root / "trials").glob("*/current.json")):
        current = TrialStore(root).current(path.parent.name)
        if current is not None:
            records.append(
                {
                    "trial_id": current.trial_id,
                    "attempt": current.attempt,
                    "status": current.status,
                    "candidate_id": current.candidate_id,
                    "result_id": current.result_id,
                }
            )
    proposal_attempts = [
        attempt
        for path in sorted((root / "trials").glob("proposal-*/current.json"))
        for attempt in TrialStore(root).attempts(path.parent.name)
    ]
    result_ids = [
        value
        for value in [state.baseline_result_id, *state.bootstrap_result_ids, *state.gepa_result_ids]
        if value is not None
    ]
    results = [_read_verified_result(root, value, config) for value in result_ids]
    return {
        "run_id": state.run_id,
        "status": state.status,
        "trials": records,
        "trial_count": len(records),
        "budget": budget.counters.model_dump(mode="json"),
        "pilot_checkpoint": (
            state.pilot_checkpoint.model_dump(mode="json") if state.pilot_checkpoint else None
        ),
        "timing": {
            "optimizer_attempts": len(proposal_attempts),
            "optimizer_wall_ms": sum(item.optimizer_wall_ms for item in proposal_attempts),
            "candidate_wall_ms": sum(item.accounting.latency_ms for item in results),
        },
        "provider_calls": 0,
    }


def export_shortlist(config_path: Path, output: Path, limit: int = 5) -> dict[str, Any]:
    if not 3 <= limit <= 5:
        raise ValueError("shortlist size must be between three and five")
    config = load_optimization_config(config_path)
    root = resolve_config_path(config_path, config.paths.run_root)
    state = _load_run_state(root)
    if (
        state.status
        not in {
            "pilot-no-improvement",
            "complete",
            "budget-limited",
            "no-improvement",
        }
        or state.baseline_result_id is None
    ):
        raise ValueError("optimizer run is not terminal for shortlist export")
    p0 = _read_verified_result(root, state.baseline_result_id, config)
    p0_package = read_package(root / "candidates" / f"{p0.candidate_id}.json")
    if p0_package.lineage.optimizer != "p0":
        raise ValueError("optimizer baseline authority is not immutable P0")
    eligible: list[tuple[CandidatePackage, CandidateResult]] = []
    for result_id in state.gepa_result_ids:
        result = _read_verified_result(root, result_id, config)
        package = read_package(root / "candidates" / f"{result.candidate_id}.json")
        _require_trial_authority(root, result)
        if _eligible(package, result, p0):
            eligible.append((package, result))
    eligible.sort(key=lambda item: item[1].validation_metric, reverse=True)
    selected = _diverse(eligible, limit)
    output.mkdir(parents=True, exist_ok=False)
    if len(selected) < 3:
        manifest = {
            "format_version": 1,
            "status": "no-improvement",
            "p0_candidate_id": p0.candidate_id,
            "gepa_candidate_ids": [],
            "count": 0,
            "reason": "fewer than three GEPA candidates satisfy every promotion guardrail",
        }
        atomic_json(output / "shortlist.json", manifest)
        return {**manifest, "provider_calls": 0}
    chosen = selected[:limit]
    all_items = [(p0_package, p0), *chosen]
    for package, result in all_items:
        shutil.copyfile(
            root / "candidates" / f"{package.candidate_id}.json",
            output / f"candidate-{package.candidate_id}.json",
        )
        shutil.copyfile(
            root / "results" / f"{result.result_id}.json",
            output / f"result-{result.result_id}.json",
        )
    manifest = {
        "format_version": 1,
        "status": "shortlist",
        "p0_candidate_id": p0.candidate_id,
        "gepa_candidate_ids": [item[0].candidate_id for item in chosen],
        "count": len(chosen),
        "ranking": "validation-metric-vector-v1",
    }
    manifest["manifest_sha256"] = digest(manifest)
    atomic_json(output / "shortlist.json", manifest)
    return {**manifest, "provider_calls": 0}


def _eligible(package: CandidatePackage, result: CandidateResult, p0: CandidateResult) -> bool:
    return all(
        (
            package.lineage.optimizer == "gepa",
            result.validation_metric.total_valid >= p0.validation_metric.total_valid,
            all(
                result.validation_model_valid[model] >= p0.validation_model_valid[model] - 1
                for model in ("qwen", "phi")
            ),
            all(
                result.validation_task_valid[task] >= p0.validation_task_valid[task] - 1
                for task in TASK_ORDER
            ),
            result.privacy.eligible,
            result.accounting.terminal_invocations == result.accounting.expected_invocations,
            result.prompt_fits_context,
        )
    )


def _diverse(
    items: list[tuple[CandidatePackage, CandidateResult]], limit: int
) -> list[tuple[CandidatePackage, CandidateResult]]:
    chosen: list[tuple[CandidatePackage, CandidateResult]] = []
    deferred: list[tuple[CandidatePackage, CandidateResult]] = []
    parents: set[str | None] = set()
    prompt_sets: set[tuple[str, ...]] = set()
    for item in items:
        package = item[0]
        prompt_key = tuple(package.prompts[task].sha256 for task in TASK_ORDER)
        if prompt_key in prompt_sets:
            continue
        prompt_sets.add(prompt_key)
        if package.lineage.parent_id in parents:
            deferred.append(item)
        else:
            chosen.append(item)
            parents.add(package.lineage.parent_id)
    return (chosen + deferred)[:limit]


def _load_run_state(root: Path) -> RunState:
    path = root / "run-state.json"
    if not path.exists():
        raise ValueError("optimizer run state is missing")
    return RunState.model_validate_json(path.read_text(encoding="utf-8"))


def _read_verified_result(root: Path, result_id: str, config) -> CandidateResult:
    result = read_result(root / "results" / f"{result_id}.json")
    if result.authority.run_id != config.run_id:
        raise ValueError("optimizer result run identity mismatch")
    if result.authority.application_commit != config.application_commit:
        raise ValueError("optimizer result application identity mismatch")
    if result.authority.config_sha256 != optimization_config_identity(config):
        raise ValueError("optimizer result configuration identity mismatch")
    if result.authority.train_manifest_sha256 != config.train_manifest.sha256:
        raise ValueError("optimizer result train split identity mismatch")
    if result.authority.validation_manifest_sha256 != config.validation_manifest.sha256:
        raise ValueError("optimizer result validation split identity mismatch")
    if result.authority.model_artifact_sha256 != {
        model.id: model.artifact_sha256 for model in config.candidate_models
    }:
        raise ValueError("optimizer result model artifact identity mismatch")
    if result.authority.proposer_identity_sha256 != proposer_identity(config.proposer):
        raise ValueError("optimizer result proposer identity mismatch")
    if result.authority.optimizer_identity_sha256 != digest(
        {
            "versions": config.versions.model_dump(mode="json"),
            "seed": config.seed,
            "bootstrap_teacher": config.bootstrap_teacher,
            "gepa_instruction_only": config.gepa_instruction_only,
        }
    ):
        raise ValueError("optimizer result framework identity mismatch")
    if result.privacy.scanner_version != SCANNER_VERSION:
        raise ValueError("optimizer result privacy scanner identity mismatch")
    return result


def _require_trial_authority(root: Path, result: CandidateResult) -> None:
    current = TrialStore(root).current(result.trial_id)
    if current is None or current.status != "complete" or current.result_id != result.result_id:
        raise ValueError("optimizer result trial authority is inconsistent")
