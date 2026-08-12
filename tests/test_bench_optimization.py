from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest
import yaml
from bench import __main__ as bench_cli
from bench.core import _conversation_identity, _manifest_payload
from bench.implementation import ImplementationIdentity
from bench.io import digest
from bench.models import TASK_ORDER
from bench.optimization.authority import verify_authority
from bench.optimization.budget import BudgetLedger, UsageCounters
from bench.optimization.compat import EXPECTED_RESULT_FIELDS, verify_compatibility
from bench.optimization.diagnostics import (
    application_stack_frames,
    failure_boundary,
    sanitized_exception_message,
)
from bench.optimization.dspy_bridge import (
    DemoAuthority,
    bootstrap_metric_acceptance,
    build_program,
    compile_bootstrap,
    demonstrations_from_program,
    load_state_only,
    prompts_from_program,
)
from bench.optimization.execution import (
    AdapterReservation,
    AdapterUsage,
    CaseOutcome,
    EvaluationBatch,
    ExecutionAdapters,
    OptimizerOperationError,
    Proposal,
    run_optimization,
)
from bench.optimization.feedback import Diagnostic, render_feedback
from bench.optimization.metrics import MetricVector
from bench.optimization.models import (
    OptimizationConfig,
    load_optimization_config,
    optimization_config_identity,
    proposer_cache_identity,
    proposer_identity,
)
from bench.optimization.operations import (
    _eligible,
    export_shortlist,
    inspect_run,
    preflight,
    verify_candidate,
)
from bench.optimization.package import (
    CandidateAccounting,
    CandidatePackage,
    CandidateResult,
    PrivacyEvidence,
    RequestEnvelopeEvidence,
    ResultAuthority,
    baseline_package,
    candidate_identity,
    demonstration_value,
    mutate_package,
    read_package,
    result_identity,
    write_package,
)
from bench.optimization.privacy import scan_package
from bench.optimization.production import (
    DspyOptimizerAdapter,
    LiteLLMCandidateAdapter,
    _history_usage,
    build_proposer_client,
)
from bench.optimization.recovery import (
    RecoveryReadiness,
    recover_gepa_readiness,
    resolve_result_authorization,
)
from bench.optimization.request_envelope import (
    estimate_request_envelope,
    verify_demonstration_authority,
)
from bench.optimization.split import OptimizationSplitManifest, freeze_split
from bench.optimization.trials import TrialStore
from pydantic import ValidationError
from typer.testing import CliRunner

from chat_chronicle.ai import CompletionResponse, canonical_hash
from chat_chronicle.ai_config import load_task_catalog

APPLICATION_COMMIT = "a" * 40
SECOND_APPLICATION_COMMIT = "b" * 40
THIRD_APPLICATION_COMMIT = "c" * 40
PROVIDERS = ["chatgpt"] * 3 + ["openai_codex"] * 3 + ["claude"] * 2 + ["claude_code"] * 2
LENGTHS = ["short", "medium", "long", "short", "medium", "long", "short", "medium", "long", "short"]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def synthetic_outputs(index: int) -> dict[str, dict[str, object]]:
    evidence = [index * 10]
    return {
        "conversation-summary": {
            "summary": "Synthetic work began. Synthetic work completed.",
            "start_date": "2026-01-01",
            "last_active_date": "2026-01-02",
            "evidence_message_ids": evidence,
        },
        "work-mode-classification": {
            "mode": "executor",
            "confidence": 1,
            "reason": "Concrete implementation work dominated.",
            "evidence_message_ids": evidence,
        },
        "last-activity": {
            "recent_work": "Synthetic work completed.",
            "status": "completed",
            "blockers": [],
            "next_action": None,
            "next_action_basis": "unknown",
            "evidence_message_ids": evidence,
        },
        "title-assessment": {
            "title_fits": True,
            "confidence": 1,
            "reason": "The title is specific and accurate.",
            "suggested_title": None,
            "evidence_message_ids": evidence,
        },
    }


def synthetic_workspace(
    tmp_path: Path,
    *,
    pilot_candidates: int = 3,
    total_candidates: int = 40,
    task_invocations: int = 3000,
) -> Path:
    repository = Path(__file__).parents[1]
    task_catalog = tmp_path / "tasks.yaml"
    shutil.copyfile(repository / "ai-tasks.default.yaml", task_catalog)
    task_hash = hashlib.sha256(task_catalog.read_bytes()).hexdigest()
    inputs = tmp_path / "private" / "inputs"
    references = tmp_path / "private" / "references"
    input_values = []
    contracts = {
        "conversation-summary": ("conversation-summary-v1", "conversation-overview-v1", "2"),
        "work-mode-classification": (
            "work-mode-classification-v1",
            "conversation-overview-v1",
            "1",
        ),
        "last-activity": ("last-activity-v1", "recent-meaningful-v1", "2"),
        "title-assessment": ("title-assessment-v1", "conversation-overview-v1", "1"),
    }
    for index in range(1, 11):
        envelope = {
            "format_version": 1,
            "corpus_version": "synthetic-v1",
            "case_group_id": f"group-{index}",
            "selection_index": index,
            "source_conversation_id": index,
            "provider": PROVIDERS[index - 1],
            "source_content_hash": hashlib.sha256(f"source-{index}".encode()).hexdigest(),
            "source_title": f"Synthetic title {index}",
            "start_date": "2026-01-01",
            "last_active_date": "2026-01-02",
            "created_at_utc": "2026-01-03T00:00:00Z",
            "snapshot_hash_reference": "snapshot",
            "task_catalog_hash_reference": task_hash,
        }
        for key, selector in (
            ("overview", "conversation-overview-v1"),
            ("recent", "recent-meaningful-v1"),
        ):
            transcript = f"Synthetic selected content {index} {key}."
            selected = [index * 10]
            hash_value = {
                "selector": selector,
                "selector_version": "1",
                "selected_message_ids": selected,
                "transcript": transcript,
            }
            if key == "overview":
                hash_value.update(
                    source_title=f"Synthetic title {index}",
                    start_date="2026-01-01",
                    last_active_date="2026-01-02",
                )
            envelope[key] = {
                "selector": selector,
                "selector_version": "1",
                "canonical_input_hash": canonical_hash(hash_value),
                "transcript": transcript,
                "selected_message_ids": selected,
                "selection_metadata": {"synthetic": True},
            }
        write_json(inputs / f"c{index:03d}.json", envelope)
        input_values.append(envelope)
        outputs = synthetic_outputs(index)
        for task, (schema, selector, finalizer) in contracts.items():
            selector_key = "recent" if task == "last-activity" else "overview"
            write_json(
                references / task / f"c{index:03d}.json",
                {
                    "format_version": 1,
                    "corpus_version": "synthetic-v1",
                    "run_id": "synthetic",
                    "case_id": f"case-{index}-{task}",
                    "case_group_id": f"group-{index}",
                    "source_conversation_id": index,
                    "provider": PROVIDERS[index - 1],
                    "task_name": task,
                    "task_version": "1",
                    "output_schema": schema,
                    "provider_schema_version": "1",
                    "finalizer_version": finalizer,
                    "input_selector": selector,
                    "selector_version": "1",
                    "input_hash": envelope[selector_key]["canonical_input_hash"],
                    "task_catalog_hash": task_hash,
                    "teacher_alias": "teacher",
                    "teacher_model": "teacher-model",
                    "teacher_session_id": "session",
                    "status": "success",
                    "output": outputs[task],
                    "failure": None,
                    "created_at_utc": "2026-01-03T00:00:00Z",
                    "validated_at_utc": "2026-01-03T00:00:00Z",
                },
            )
    from bench.models import InputEnvelope, SelectionManifest

    parsed_inputs = [InputEnvelope.model_validate(value) for value in input_values]
    entries = [
        {
            "authority_index": index,
            "conversation_identity": _conversation_identity(parsed_inputs[index - 1]),
            "provider": PROVIDERS[index - 1],
            "length_stratum": LENGTHS[index - 1],
            "date_bin": "synthetic",
        }
        for index in range(1, 11)
    ]
    development_payload = {
        "format_version": 1,
        "algorithm_version": "synthetic-development-v1",
        "role": "development",
        "source_selection_identity": "9" * 64,
        "ordered_conversations": entries,
        "conversation_count": 10,
        "expected_case_count": 40,
        "provider_counts": dict(Counter(PROVIDERS)),
        "length_stratum_counts": dict(Counter(LENGTHS)),
        "date_bin_counts": {"synthetic": 10},
        "created_at_utc": "2026-08-06T00:00:00Z",
        "manifest_sha256": "0" * 64,
    }
    provisional = SelectionManifest.model_validate(development_payload)
    development_payload["manifest_sha256"] = digest(_manifest_payload(provisional))
    development = tmp_path / "private" / "development.json"
    write_json(development, development_payload)
    train_path, validation_path = freeze_split(development, tmp_path / "private" / "split")
    train = OptimizationSplitManifest.model_validate_json(train_path.read_text(encoding="utf-8"))
    validation = OptimizationSplitManifest.model_validate_json(
        validation_path.read_text(encoding="utf-8")
    )
    artifacts = []
    for name in ("qwen.gguf", "phi.gguf"):
        path = tmp_path / "private" / name
        path.write_bytes(name.encode())
        artifacts.append(hashlib.sha256(path.read_bytes()).hexdigest())
    config = {
        "version": 1,
        "optimizer_id": "synthetic-run",
        "run_id": "synthetic-run",
        "application_commit": APPLICATION_COMMIT,
        "seed": 7,
        "split_seed": "wp-5.2b3b.1-optimizer-split-v1",
        "versions": {
            "dspy": "3.3.0",
            "gepa": "0.1.1",
            "gepa_result_schema": "dspy-gepa-result-v0.1.1",
        },
        "tasks": list(TASK_ORDER),
        "mutable_fields": [f"tasks.{task}.system_prompt" for task in TASK_ORDER],
        "context_window": 8192,
        "accepted_task_catalog_sha256": task_hash,
        "development_manifest_sha256": development_payload["manifest_sha256"],
        "train_manifest": {
            "path": "private/split/optimizer-train.json",
            "sha256": train.manifest_sha256,
            "role": "optimizer-train",
            "conversations": 6,
            "cases": 24,
        },
        "validation_manifest": {
            "path": "private/split/optimizer-validation.json",
            "sha256": validation.manifest_sha256,
            "role": "optimizer-validation",
            "conversations": 4,
            "cases": 16,
        },
        "candidate_models": [
            {
                "id": model,
                "profile": model,
                "artifact_sha256": artifacts[ordinal],
                "artifact_path": f"private/{model}.gguf",
                "expected_provider": "synthetic",
                "expected_model": model,
                "litellm_model": f"lm_studio/{model}",
                "api_base": "http://127.0.0.1:1234/v1",
                "api_key_env": None,
                "timeout_seconds": 5,
                "estimated_seconds_per_task": 1,
                "reasoning_effort": "none",
                "context_window": 8192,
                "concurrency": 1,
                "infrastructure_retries": 1,
                "semantic_retries": 0,
            }
            for ordinal, model in enumerate(("qwen", "phi"))
        ],
        "proposer": {
            "id": "synthetic-proposer",
            "litellm_model": "anthropic/synthetic",
            "provider": "Anthropic",
            "region": "global",
            "credential_mode": "api-key-environment",
            "api_key_env": "SYNTHETIC_KEY",
            "timeout_seconds": 5,
            "concurrency": 1,
            "temperature": 0,
            "reasoning_effort": "none",
            "cache_namespace": "synthetic-run",
            "max_calls": 250,
            "per_call_input_tokens": 50000,
            "per_call_output_tokens": 8000,
            "max_input_tokens": 12500000,
            "max_output_tokens": 2000000,
            "input_usd_per_million": 2,
            "output_usd_per_million": 10,
            "max_cost_usd": 50,
            "disclosure": "Synthetic development prompts only.",
        },
        "budget": {
            "pilot_candidates": pilot_candidates,
            "total_candidates": total_candidates,
            "task_invocations": task_invocations,
            "pilot_compute_hours": 4,
            "total_compute_hours": 12,
            "compute_cost_usd": 12.05,
            "prompt_token_ceiling": 7000,
        },
        "paths": {
            "development_manifest": "private/development.json",
            "inputs": "private/inputs",
            "references": "private/references",
            "accepted_task_catalog": "tasks.yaml",
            "run_root": "private/run",
        },
        "bootstrap_max_labeled_demos": 1,
        "bootstrap_max_bootstrapped_demos": 1,
        "bootstrap_max_rounds": 1,
        "bootstrap_teacher": "candidate-model",
        "gepa_track_stats": True,
        "gepa_instruction_only": True,
    }
    config_path = tmp_path / "optimization.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return config_path


class FakeCandidateAdapter:
    def __init__(
        self,
        *,
        gepa_valid: bool = True,
        reliability_tradeoff: str | None = None,
    ) -> None:
        self.calls = 0
        self.gepa_valid = gepa_valid
        self.reliability_tradeoff = reliability_tradeoff

    def reservation(self, scope: str, model_id: str) -> AdapterReservation:
        del model_id
        return AdapterReservation(task_calls=24 if scope == "train" else 16, compute_hours=0.01)

    def evaluate(
        self, candidate: CandidatePackage, scope: str, model_id: str, authority
    ) -> EvaluationBatch:
        self.calls += 1
        manifest = authority.train if scope == "train" else authority.validation
        outcomes = []
        for entry in manifest.ordered_conversations:
            for task in TASK_ORDER:
                valid = self._valid(candidate, scope, model_id, manifest, entry, task)
                outcomes.append(
                    CaseOutcome(
                        alias=f"c{entry.authority_index:03d}--{task}",
                        task=task,
                        model_id=model_id,
                        terminal=True,
                        valid=valid,
                        semantic_agreement=1 if valid else 0,
                        diagnostics=[] if valid else [Diagnostic(category="schema")],
                    )
                )
        return EvaluationBatch(
            scope=scope,
            model_id=model_id,
            outcomes=outcomes,
            usage=AdapterUsage(task_calls=len(outcomes), compute_hours=0.001, latency_ms=10),
        )

    def _valid(self, candidate, scope, model_id, manifest, entry, task) -> bool:
        if self.reliability_tradeoff is None or scope != "validation":
            return (
                self.gepa_valid
                if candidate.lineage.optimizer == "gepa"
                else not (entry == manifest.ordered_conversations[0] and task == TASK_ORDER[0])
            )
        entry_index = manifest.ordered_conversations.index(entry)
        if candidate.lineage.optimizer != "gepa":
            return not (entry_index == 0 and task in TASK_ORDER[:2])
        if self.reliability_tradeoff == "worst-model":
            return not (model_id == "qwen" and entry_index == 0 and task in TASK_ORDER[:3])
        if self.reliability_tradeoff == "minimum-task":
            return not (
                task == TASK_ORDER[0]
                and (
                    (model_id == "qwen" and entry_index < 2)
                    or (model_id == "phi" and entry_index == 0)
                )
            )
        raise AssertionError("unknown synthetic reliability tradeoff")


class FakeOptimizerAdapter:
    def __init__(
        self,
        *,
        fail_gepa_once: int | None = None,
        max_gepa: int | None = 3,
        prompt_padding: int = 0,
    ) -> None:
        self.fail_gepa_once = fail_gepa_once
        self.failed = False
        self.calls: list[str] = []
        self.max_gepa = max_gepa
        self.prompt_padding = prompt_padding

    def reservation(self, optimizer: str) -> AdapterReservation:
        if optimizer == "bootstrap-few-shot":
            return AdapterReservation(task_calls=1)
        return AdapterReservation(proposer_calls=1, input_tokens=50, output_tokens=20)

    def bootstrap(self, parent: CandidatePackage, authority) -> Proposal:
        del authority
        self.calls.append("bootstrap")
        return Proposal(
            prompts={
                task: parent.prompts[task].text + "\nSynthetic bootstrap." for task in TASK_ORDER
            },
            strategy="synthetic-bootstrap",
            usage=AdapterUsage(task_calls=1),
        )

    def gepa(self, parent: CandidatePackage, authority, feedback: str, ordinal: int) -> Proposal:
        del authority, feedback
        self.calls.append(f"gepa-{ordinal}")
        if self.max_gepa is not None and ordinal > self.max_gepa:
            return Proposal(
                prompts={task: parent.prompts[task].text for task in TASK_ORDER},
                strategy="synthetic-search-exhausted",
                usage=AdapterUsage(proposer_calls=1, input_tokens=10, output_tokens=5),
                search_exhausted=True,
            )
        if self.fail_gepa_once == ordinal and not self.failed:
            self.failed = True
            raise RuntimeError("synthetic interruption")
        return Proposal(
            prompts={
                task: parent.prompts[task].text
                + f"\nSynthetic GEPA strategy {ordinal}."
                + ("x" * self.prompt_padding if task == TASK_ORDER[0] else "")
                for task in TASK_ORDER
            },
            strategy=f"synthetic-gepa-{ordinal}",
            usage=AdapterUsage(proposer_calls=1, input_tokens=40, output_tokens=10),
        )


class MeasuredBootstrapFailureAdapter(FakeOptimizerAdapter):
    def reservation(self, optimizer: str) -> AdapterReservation:
        if optimizer == "bootstrap-few-shot":
            return AdapterReservation(
                task_calls=3,
                retries=1,
                compute_hours=0.01,
                compute_cost_usd=0.01,
            )
        return super().reservation(optimizer)

    def bootstrap(self, parent: CandidatePackage, authority) -> Proposal:
        del parent, authority
        raise OptimizerOperationError(
            "synthetic post-compile adaptation failure",
            usage=AdapterUsage(
                task_calls=2,
                retries=1,
                input_tokens=17,
                output_tokens=9,
            ),
            failure_category="ValueError",
        )


class FakeLiteLLMClient:
    def __init__(self, *, provider: str = "synthetic", model: str = "qwen") -> None:
        self.provider = provider
        self.model = model
        self.requests = []

    async def complete(self, request) -> CompletionResponse:
        self.requests.append(request)
        properties = request.response_schema["properties"]
        evidence = properties["evidence_message_ids"]["items"]["enum"]
        if "summary" in properties:
            output = synthetic_outputs(evidence[0] // 10)["conversation-summary"]
        elif "mode" in properties:
            output = synthetic_outputs(evidence[0] // 10)["work-mode-classification"]
        elif "recent_work" in properties:
            output = synthetic_outputs(evidence[0] // 10)["last-activity"]
        else:
            output = synthetic_outputs(evidence[0] // 10)["title-assessment"]
        return CompletionResponse(
            json.dumps(output),
            self.provider,
            self.model,
            {"prompt_tokens": 12, "completion_tokens": 5},
        )


class StepClock:
    def __init__(self, step_ms: int = 7) -> None:
        self.value = -step_ms * 1_000_000
        self.step = step_ms * 1_000_000

    def __call__(self) -> int:
        self.value += self.step
        return self.value


def clean_identity() -> ImplementationIdentity:
    return ImplementationIdentity(APPLICATION_COMMIT, False, None)


def recovery_identity() -> ImplementationIdentity:
    return ImplementationIdentity(THIRD_APPLICATION_COMMIT, False, None)


def recover_synthetic(config_path: Path) -> dict[str, object]:
    return recover_gepa_readiness(config_path, identity_probe=recovery_identity)


def finish_synthetic_run(
    config_path: Path,
    adapters: ExecutionAdapters,
    *,
    monotonic_ns=None,
) -> dict[str, object]:
    kwargs = {"identity_probe": clean_identity}
    if monotonic_ns is not None:
        kwargs["monotonic_ns"] = monotonic_ns
    result = run_optimization(config_path, adapters, resume=False, **kwargs)
    if result["status"] == "pilot-complete":
        result = run_optimization(config_path, adapters, resume=True, **kwargs)
    return result


class FailingBootstrapAdapter(FakeOptimizerAdapter):
    def bootstrap(self, parent: CandidatePackage, authority) -> Proposal:
        del parent, authority
        raise RuntimeError("synthetic bootstrap interruption")


def historical_recovery_workspace(tmp_path: Path) -> Path:
    """Create three append-only Bootstrap attempts across three clean commits."""

    config_path = synthetic_workspace(
        tmp_path, pilot_candidates=1, total_candidates=1, task_invocations=170
    )
    candidate = FakeCandidateAdapter()

    def identity(commit: str):
        return lambda: ImplementationIdentity(commit, False, None)

    with pytest.raises(ValueError, match="usage is missing"):
        run_optimization(
            config_path,
            ExecutionAdapters(candidate, FailingBootstrapAdapter()),
            resume=False,
            identity_probe=identity(APPLICATION_COMMIT),
        )
    for commit in (SECOND_APPLICATION_COMMIT, THIRD_APPLICATION_COMMIT):
        value = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        value["application_commit"] = commit
        config_path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
        if commit == SECOND_APPLICATION_COMMIT:
            with pytest.raises(ValueError, match="usage is missing"):
                run_optimization(
                    config_path,
                    ExecutionAdapters(candidate, FailingBootstrapAdapter()),
                    resume=True,
                    identity_probe=identity(commit),
                )
        else:
            finished = run_optimization(
                config_path,
                ExecutionAdapters(candidate, FakeOptimizerAdapter(max_gepa=0)),
                resume=True,
                identity_probe=identity(commit),
            )
            assert finished["status"] == "pilot-no-improvement"

    root = tmp_path / "private" / "run"
    state_path = root / "run-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert len(state["bootstrap_result_ids"]) == 1
    state.update(
        status="in-progress",
        bootstrap_result_ids=[],
        pilot_checkpoint=None,
        stop_reason=None,
    )
    state["state_sha256"] = digest(
        {key: item for key, item in state.items() if key != "state_sha256"}
    )
    write_json(state_path, state)
    return config_path


def recovery_artifacts(
    config_path: Path,
) -> tuple[Path, CandidateResult, CandidateResult, CandidatePackage, CandidatePackage]:
    root = config_path.parent / "private" / "run"
    by_role = {}
    for path in (root / "results").glob("*.json"):
        result = CandidateResult.model_validate_json(path.read_text(encoding="utf-8"))
        package = read_package(root / "candidates" / f"{result.candidate_id}.json")
        by_role[package.lineage.optimizer] = (result, package)
    p0, p0_package = by_role["p0"]
    bootstrap, bootstrap_package = by_role["bootstrap-few-shot"]
    return root, p0, bootstrap, p0_package, bootstrap_package


def rewrite_state(root: Path, update: dict[str, object]) -> None:
    path = root / "run-state.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.update(update)
    value["state_sha256"] = digest(
        {key: item for key, item in value.items() if key != "state_sha256"}
    )
    write_json(path, value)


def test_recovery_accepts_historical_commits_registers_bootstrap_and_selects_p0(
    tmp_path: Path,
) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    root, p0, bootstrap, _p0_package, bootstrap_package = recovery_artifacts(config_path)
    preserved_paths = sorted(
        path
        for directory in (
            "authorizations",
            "consumed-authorizations",
            "candidates",
            "results",
            "trials",
        )
        for path in (root / directory).rglob("*.json")
    ) + [root / "budget.json"]
    preserved = {path: path.read_bytes() for path in preserved_paths}

    recovered = recover_synthetic(config_path)

    assert recovered == {
        "status": "gepa-ready",
        "p0_results": 1,
        "bootstrap_results": 1,
        "gepa_results": 0,
        "gepa_attempts": 0,
        "gepa_parent": "p0",
        "bootstrap_disposition": "complete-non-promotable",
        "bootstrap_disposition_basis": "manager-policy",
        "historical_authorizations": 3,
        "recovery_sha256": recovered["recovery_sha256"],
        "recovery_provider_calls": 0,
    }
    state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    assert state["baseline_result_id"] == p0.result_id
    assert state["bootstrap_result_ids"] == [bootstrap.result_id]
    readiness = RecoveryReadiness.model_validate_json(
        (root / "checkpoints" / "gepa-readiness.json").read_text(encoding="utf-8")
    )
    assert readiness.gepa_parent_result_id == p0.result_id
    assert readiness.bootstrap_disposition_basis == "manager-policy"
    assert readiness.bootstrap_disposition_result_id == bootstrap.result_id
    assert readiness.results[0].execution_authority_sha256 != (
        readiness.results[1].execution_authority_sha256
    )
    assert p0.authority.application_commit == APPLICATION_COMMIT
    assert bootstrap.authority.application_commit == THIRD_APPLICATION_COMMIT
    legacy_payload = p0.model_dump(mode="json", exclude={"result_id"})
    legacy_payload["authority"].pop("execution_authority_sha256")
    legacy = CandidateResult(result_id=result_identity(legacy_payload), **legacy_payload)
    assert (
        resolve_result_authorization(
            root, legacy, load_optimization_config(config_path)
        ).application_commit
        == APPLICATION_COMMIT
    )
    assert all(path.read_bytes() == value for path, value in preserved.items())

    verified = verify_candidate(
        config_path, root / "candidates" / f"{bootstrap_package.candidate_id}.json"
    )
    assert verified["valid"] is True
    assert inspect_run(config_path)["provider_calls"] == 0


def test_recovery_is_idempotent_and_preserves_attempts_and_current_pointer(
    tmp_path: Path,
) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    root, *_ = recovery_artifacts(config_path)
    attempts = root / "trials" / "proposal-bootstrap-few-shot-0001"
    before = {path: path.read_bytes() for path in sorted(attempts.rglob("*.json"))}

    first = recover_synthetic(config_path)
    first_state = (root / "run-state.json").read_bytes()
    first_readiness = (root / "checkpoints" / "gepa-readiness.json").read_bytes()
    second = recover_synthetic(config_path)

    assert first == second
    assert (root / "run-state.json").read_bytes() == first_state
    assert (root / "checkpoints" / "gepa-readiness.json").read_bytes() == first_readiness
    assert {path: path.read_bytes() for path in sorted(attempts.rglob("*.json"))} == before
    assert [item.status for item in TrialStore(root).attempts(attempts.name)] == [
        "interrupted",
        "interrupted",
        "complete",
    ]


def test_recovery_requires_exact_clean_pinned_commit(tmp_path: Path) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    assert (
        recover_gepa_readiness(config_path, identity_probe=recovery_identity)["status"]
        == "gepa-ready"
    )


@pytest.mark.parametrize(
    ("identity", "description"),
    [
        (ImplementationIdentity(THIRD_APPLICATION_COMMIT, True, "dirty"), "dirty"),
        (ImplementationIdentity("d" * 40, False, None), "wrong-commit"),
    ],
)
def test_recovery_rejects_unpinned_checkout_before_run_state_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    identity: ImplementationIdentity,
    description: str,
) -> None:
    del description
    config_path = historical_recovery_workspace(tmp_path)
    root, *_ = recovery_artifacts(config_path)
    state_before = (root / "run-state.json").read_bytes()
    monkeypatch.setattr(
        "bench.optimization.recovery._load_state",
        lambda _root: pytest.fail("run state was accessed before implementation verification"),
    )
    with pytest.raises(ValueError, match="pinned clean application commit"):
        recover_gepa_readiness(config_path, identity_probe=lambda: identity)
    assert (root / "run-state.json").read_bytes() == state_before
    assert not (root / "checkpoints" / "gepa-readiness.json").exists()


def test_recovery_does_not_relax_current_clean_commit_for_new_execution(
    tmp_path: Path,
) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    recover_synthetic(config_path)
    with pytest.raises(ValueError, match="pinned clean application commit"):
        run_optimization(
            config_path,
            ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter()),
            resume=True,
            identity_probe=lambda: ImplementationIdentity("d" * 40, False, None),
        )


@pytest.mark.parametrize(
    "mode", ["missing", "dangling", "duplicate", "stale", "foreign-run", "hash-invalid"]
)
def test_recovery_rejects_invalid_authorization_history(tmp_path: Path, mode: str) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    root, *_ = recovery_artifacts(config_path)
    authorization_paths = sorted((root / "authorizations").glob("*.json"))
    consumed_paths = sorted((root / "consumed-authorizations").glob("*.json"))
    if mode == "missing":
        consumed_paths[0].unlink()
    elif mode == "dangling":
        write_json(
            root / "consumed-authorizations" / f"{'f' * 64}.json",
            {"authority_sha256": "f" * 64, "run_id": "synthetic-run"},
        )
    elif mode == "duplicate":
        state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
        rewrite_state(
            root,
            {
                "authorization_ids": [
                    *state["authorization_ids"],
                    state["authorization_ids"][0],
                ]
            },
        )
    elif mode == "stale":
        state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
        rewrite_state(root, {"authorization_ids": list(reversed(state["authorization_ids"]))})
    elif mode == "foreign-run":
        value = json.loads(consumed_paths[0].read_text(encoding="utf-8"))
        value["run_id"] = "foreign-run"
        write_json(consumed_paths[0], value)
    else:
        value = json.loads(authorization_paths[0].read_text(encoding="utf-8"))
        value["authority_sha256"] = "0" * 64
        write_json(authorization_paths[0], value)
    with pytest.raises((ValueError, ValidationError), match="authorization|hash"):
        recover_synthetic(config_path)


def test_recovery_rejects_immutable_experiment_change(tmp_path: Path) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    value = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    value["seed"] += 1
    config_path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="immutable experiment"):
        recover_synthetic(config_path)


def test_application_commit_change_without_consumed_authorization_fails(
    tmp_path: Path,
) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    root, p0, *_ = recovery_artifacts(config_path)
    config = load_optimization_config(config_path)
    payload = p0.model_dump(mode="json", exclude={"result_id"})
    payload["authority"]["application_commit"] = "d" * 40
    payload["authority"]["config_sha256"] = optimization_config_identity(
        config.model_copy(update={"application_commit": "d" * 40})
    )
    changed = CandidateResult(result_id=result_identity(payload), **payload)
    with pytest.raises(ValueError, match="application identity"):
        resolve_result_authorization(root, changed, config)


@pytest.mark.parametrize("kind", ["candidate", "result", "trial", "authorization"])
def test_recovery_identity_mismatches_fail_with_actionable_diagnostics(
    tmp_path: Path, kind: str
) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    root, _p0, bootstrap, _p0_package, bootstrap_package = recovery_artifacts(config_path)
    if kind == "candidate":
        path = root / "candidates" / f"{bootstrap_package.candidate_id}.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["candidate_id"] = "0" * 64
        write_json(path, value)
    elif kind == "result":
        path = root / "results" / f"{bootstrap.result_id}.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["result_id"] = "0" * 64
        write_json(path, value)
    elif kind == "trial":
        path = root / "trials" / "proposal-bootstrap-few-shot-0001" / "current.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["attempt_sha256"] = "0" * 64
        write_json(path, value)
    else:
        path = sorted((root / "authorizations").glob("*.json"))[0]
        value = json.loads(path.read_text(encoding="utf-8"))
        value["authority_sha256"] = "0" * 64
        write_json(path, value)
    with pytest.raises((ValueError, ValidationError), match="identity|authority|hash|mismatch"):
        recover_synthetic(config_path)


@pytest.mark.parametrize(
    "kind",
    [
        "attempt",
        "state-result",
        "current-only",
        "empty-directory",
        "candidate-only",
        "malformed-pointer",
    ],
)
def test_existing_gepa_evidence_blocks_recovery(tmp_path: Path, kind: str) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    root, _p0, _bootstrap, p0_package, _bootstrap_package = recovery_artifacts(config_path)
    if kind == "attempt":
        TrialStore(root).append("proposal-gepa-0001", "failed", {"provider_calls": 0})
    elif kind == "state-result":
        rewrite_state(root, {"gepa_result_ids": ["f" * 64]})
    elif kind == "candidate-only":
        candidate = mutate_package(
            p0_package,
            {task: p0_package.prompts[task].text + "\nSynthetic GEPA." for task in TASK_ORDER},
            optimizer="gepa",
            proposer_id="synthetic",
            mutation_ordinal=1,
        )
        write_package(root / "candidates" / f"{candidate.candidate_id}.json", candidate)
    else:
        trial = root / "trials" / "proposal-gepa-0001"
        trial.mkdir(parents=True)
        if kind == "current-only":
            write_json(
                trial / "current.json",
                {
                    "format_version": 1,
                    "trial_id": "proposal-gepa-0001",
                    "current_attempt": 1,
                    "attempt_sha256": "f" * 64,
                },
            )
        elif kind == "malformed-pointer":
            write_json(trial / "current.json", {"malformed": True})
    with pytest.raises(ValueError, match="existing GEPA evidence"):
        recover_synthetic(config_path)


def test_recovery_atomic_writes_retry_windows_sharing_violation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    import os

    real_replace = os.replace
    calls = 0
    retried: set[str] = set()

    def sharing_violation_once(source: str, destination: Path) -> None:
        nonlocal calls
        calls += 1
        name = Path(destination).name
        if name in {"run-state.json", "gepa-readiness.json"} and name not in retried:
            retried.add(name)
            error = PermissionError("synthetic sharing violation")
            error.winerror = 32  # type: ignore[attr-defined]
            raise error
        real_replace(source, destination)

    monkeypatch.setattr("bench.io.os.replace", sharing_violation_once)
    monkeypatch.setattr("bench.io.time.sleep", lambda _seconds: None)
    assert recover_synthetic(config_path)["status"] == "gepa-ready"
    assert retried == {"run-state.json", "gepa-readiness.json"}
    assert calls >= 4


def test_recovery_rerun_repairs_failure_between_atomic_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = historical_recovery_workspace(tmp_path)
    root, *_ = recovery_artifacts(config_path)
    state_before = (root / "run-state.json").read_bytes()
    from bench.io import atomic_json as real_atomic_json

    failed = False

    def fail_readiness_once(path: Path, value: object) -> None:
        nonlocal failed
        if path.name == "gepa-readiness.json" and not failed:
            failed = True
            raise OSError("synthetic interruption between recovery writes")
        real_atomic_json(path, value)

    with monkeypatch.context() as context:
        context.setattr("bench.optimization.recovery.atomic_json", fail_readiness_once)
        with pytest.raises(OSError, match="between recovery writes"):
            recover_synthetic(config_path)

    recovered_state = (root / "run-state.json").read_bytes()
    assert recovered_state != state_before
    assert not (root / "checkpoints" / "gepa-readiness.json").exists()
    first_complete = recover_synthetic(config_path)
    state_after = (root / "run-state.json").read_bytes()
    readiness_after = (root / "checkpoints" / "gepa-readiness.json").read_bytes()
    second_complete = recover_synthetic(config_path)
    assert first_complete == second_complete
    assert state_after == recovered_state == (root / "run-state.json").read_bytes()
    assert readiness_after == (root / "checkpoints" / "gepa-readiness.json").read_bytes()


def test_recovery_imports_no_provider_or_credential_clients() -> None:
    code = """
import sys
from bench.optimization import recovery
forbidden = (
    'bench.optimization.production',
    'dspy',
    'litellm',
    'google.auth',
    'google.cloud.aiplatform',
)
loaded = [name for name in forbidden if name in sys.modules]
if loaded:
    raise SystemExit('forbidden imports: ' + ','.join(loaded))
print(recovery.__name__)
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).parents[1],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "bench.optimization.recovery"


def metric(**updates: object) -> MetricVector:
    value = {
        "total_valid": 30,
        "worst_model_valid": 15,
        "minimum_task_valid": 7,
        "semantic_agreement": 0.5,
        "complete_package_uts": 0.5,
        "prompt_tokens": 1000,
        "candidate_id": "b",
    }
    value.update(updates)
    return MetricVector.model_validate(value)


def test_config_is_strict_and_models_operational_proposer_policy(tmp_path: Path) -> None:
    config_path = synthetic_workspace(tmp_path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert OptimizationConfig.model_validate(data).bootstrap_teacher == "candidate-model"
    with pytest.raises(ValidationError):
        OptimizationConfig.model_validate({**data, "unknown": True})
    data["paths"]["run_root"] = "private/holdout/run"
    with pytest.raises(ValidationError, match="holdout"):
        OptimizationConfig.model_validate(data)


def test_public_template_declares_the_single_operational_proposer() -> None:
    template = yaml.safe_load(
        (Path(__file__).parents[1] / "bench" / "optimization.default.yaml").read_text(
            encoding="utf-8"
        )
    )
    config = OptimizationConfig.model_validate(template)
    assert (
        config.proposer.provider,
        config.proposer.region,
        config.proposer.litellm_model,
    ) == ("Google Vertex AI", "global", "vertex_ai/gemini-3.1-pro-preview")
    assert config.proposer.credential_mode == "vertex-adc"
    assert config.proposer.api_key_env is None
    assert config.proposer.resolved_location == "global"
    assert (
        config.proposer.google_cloud_project_env,
        config.proposer.google_cloud_location_env,
        config.proposer.vertex_project_env,
        config.proposer.vertex_location_env,
        config.proposer.vertex_enable_env,
    ) == (
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
        "VERTEXAI_PROJECT",
        "VERTEXAI_LOCATION",
        "GOOGLE_GENAI_USE_VERTEXAI",
    )


def _vertex_template() -> dict[str, object]:
    return yaml.safe_load(
        (Path(__file__).parents[1] / "bench" / "optimization.default.yaml").read_text(
            encoding="utf-8"
        )
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("api_key_env", "GEMINI_API_KEY", "cannot require an API key"),
        ("google_cloud_project_env", None, "requires project and location"),
        ("google_cloud_location_env", None, "requires project and location"),
        ("google_cloud_project_env", "owner-project-123", "string_pattern_mismatch"),
        ("resolved_location", None, "must resolve to global"),
        ("project_id", "owner-project-123", "extra_forbidden"),
        ("credential_file", "C:/private/adc.json", "extra_forbidden"),
    ],
)
def test_vertex_adc_profile_validation_is_strict(field: str, value: object, message: str) -> None:
    template = _vertex_template()
    template["proposer"][field] = value
    with pytest.raises(ValidationError, match=message):
        OptimizationConfig.model_validate(template)


def test_vertex_adc_runtime_reaches_injected_client_without_api_key() -> None:
    profile = OptimizationConfig.model_validate(_vertex_template()).proposer
    project_marker = "synthetic-project-value-never-persist"
    environment = {
        "GOOGLE_CLOUD_PROJECT": project_marker,
        "GOOGLE_CLOUD_LOCATION": "global",
        "VERTEXAI_PROJECT": project_marker,
        "VERTEXAI_LOCATION": "global",
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
    }
    captured: dict[str, object] = {}
    sentinel = object()

    def fake_lm(model: str, **kwargs: object) -> object:
        captured.update(model=model, **kwargs)
        return sentinel

    assert (
        build_proposer_client(
            profile, lm_factory=fake_lm, environment=environment, adc_probe=lambda: True
        )
        is sentinel
    )
    assert captured == {
        "model": "vertex_ai/gemini-3.1-pro-preview",
        "credential_mode": "vertex-adc",
        "concurrency": 1,
        "budget_contract": {
            "max_calls": 250,
            "max_input_tokens": 12_500_000,
            "max_output_tokens": 2_000_000,
            "input_usd_per_million": 2.0,
            "output_usd_per_million": 12.0,
            "max_cost_usd": 50.0,
        },
        "temperature": 0.0,
        "timeout": 120.0,
        "num_retries": 1,
        "cache": False,
        "reasoning_effort": "none",
        "max_tokens": 8000,
        "vertex_project": project_marker,
        "vertex_location": "global",
    }
    assert "api_key" not in captured


def test_vertex_route_crosses_real_dspy_bridge_with_injected_lm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import dspy

    profile = OptimizationConfig.model_validate(_vertex_template()).proposer
    captured: dict[str, object] = {}

    def fake_dspy_lm(model: str, **kwargs: object) -> object:
        captured.update(model=model, **kwargs)
        return object()

    monkeypatch.setattr(dspy, "LM", fake_dspy_lm)
    build_proposer_client(
        profile,
        environment={
            "GOOGLE_CLOUD_PROJECT": "synthetic-project",
            "GOOGLE_CLOUD_LOCATION": "global",
            "VERTEXAI_PROJECT": "synthetic-project",
            "VERTEXAI_LOCATION": "global",
            "GOOGLE_GENAI_USE_VERTEXAI": "true",
        },
        adc_probe=lambda: True,
    )
    assert captured == {
        "model": "vertex_ai/gemini-3.1-pro-preview",
        "vertex_project": "synthetic-project",
        "vertex_location": "global",
        "temperature": 0.0,
        "timeout": 120.0,
        "num_retries": 1,
        "cache": False,
        "reasoning_effort": "none",
        "max_tokens": 8000,
    }


@pytest.mark.parametrize(
    "missing",
    [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
        "VERTEXAI_PROJECT",
        "VERTEXAI_LOCATION",
    ],
)
def test_vertex_adc_runtime_fails_clearly_for_missing_project_or_location(
    missing: str,
) -> None:
    profile = OptimizationConfig.model_validate(_vertex_template()).proposer
    environment = {
        "GOOGLE_CLOUD_PROJECT": "synthetic-project",
        "GOOGLE_CLOUD_LOCATION": "global",
        "VERTEXAI_PROJECT": "synthetic-project",
        "VERTEXAI_LOCATION": "global",
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
    }
    del environment[missing]
    with pytest.raises(RuntimeError, match=missing):
        build_proposer_client(
            profile, lm_factory=lambda *_args, **_kwargs: object(), environment=environment
        )


def test_vertex_adc_runtime_fails_closed_for_adc_and_location() -> None:
    profile = OptimizationConfig.model_validate(_vertex_template()).proposer
    environment = {
        "GOOGLE_CLOUD_PROJECT": "synthetic-project",
        "GOOGLE_CLOUD_LOCATION": "global",
        "VERTEXAI_PROJECT": "synthetic-project",
        "VERTEXAI_LOCATION": "global",
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
    }
    with pytest.raises(RuntimeError, match="Credentials are unavailable"):
        build_proposer_client(
            profile,
            lm_factory=lambda *_args, **_kwargs: object(),
            environment=environment,
            adc_probe=lambda: False,
        )
    environment["VERTEXAI_LOCATION"] = "not-global"
    with pytest.raises(RuntimeError, match="must resolve to global"):
        build_proposer_client(
            profile,
            lm_factory=lambda *_args, **_kwargs: object(),
            environment=environment,
            adc_probe=lambda: True,
        )


def test_anthropic_api_key_environment_remains_compatible(tmp_path: Path) -> None:
    profile = load_optimization_config(synthetic_workspace(tmp_path)).proposer
    captured: dict[str, object] = {}

    def fake_lm(model: str, **kwargs: object) -> object:
        captured.update(model=model, **kwargs)
        return object()

    build_proposer_client(
        profile,
        lm_factory=fake_lm,
        environment={"SYNTHETIC_KEY": "synthetic-secret"},
    )
    assert captured["api_key"] == "synthetic-secret"
    assert "vertex_project" not in captured


def test_proposer_authorization_and_cache_identities_bind_non_secret_route(
    tmp_path: Path,
) -> None:
    first = OptimizationConfig.model_validate(_vertex_template())
    changed_data = _vertex_template()
    changed_data["proposer"]["vertex_location_env"] = "ALTERNATE_VERTEX_LOCATION"
    changed = OptimizationConfig.model_validate(changed_data)
    assert optimization_config_identity(first) != optimization_config_identity(changed)
    changed_model_data = _vertex_template()
    changed_model_data["proposer"]["litellm_model"] = "vertex_ai/synthetic-alternate"
    changed_model = OptimizationConfig.model_validate(changed_model_data).proposer
    changed_provider_and_mode = load_optimization_config(synthetic_workspace(tmp_path)).proposer
    for alternate in (changed.proposer, changed_model, changed_provider_and_mode):
        assert proposer_identity(first.proposer) != proposer_identity(alternate)
        assert proposer_cache_identity(first.proposer) != proposer_cache_identity(alternate)


def test_vertex_runtime_values_never_enter_serialized_identity_artifacts() -> None:
    config = OptimizationConfig.model_validate(_vertex_template())
    project_marker = "runtime-only-project-marker"
    credential_marker = "runtime-only-adc-marker"

    def fake_lm(_model: str, **_kwargs: object) -> object:
        return object()

    build_proposer_client(
        config.proposer,
        lm_factory=fake_lm,
        environment={
            "GOOGLE_CLOUD_PROJECT": project_marker,
            "GOOGLE_CLOUD_LOCATION": "global",
            "VERTEXAI_PROJECT": project_marker,
            "VERTEXAI_LOCATION": "global",
            "GOOGLE_GENAI_USE_VERTEXAI": "true",
        },
        adc_probe=lambda: bool(credential_marker),
    )
    serialized = json.dumps(
        {
            "config": config.model_dump(mode="json"),
            "config_sha256": optimization_config_identity(config),
            "proposer_identity_sha256": proposer_identity(config.proposer),
            "cache_identity_sha256": proposer_cache_identity(config.proposer),
        },
        sort_keys=True,
    )
    assert project_marker not in serialized
    assert credential_marker not in serialized


def test_vertex_budget_arithmetic_reasoning_and_pre_call_rejection(tmp_path: Path) -> None:
    config = OptimizationConfig.model_validate(_vertex_template())
    expected_cost = (
        config.proposer.max_input_tokens * config.proposer.input_usd_per_million
        + config.proposer.max_output_tokens * config.proposer.output_usd_per_million
    ) / 1_000_000
    assert expected_cost == 49
    assert config.proposer.max_cost_usd == 50
    usage = _history_usage(
        [
            type(
                "LM",
                (),
                {
                    "history": [
                        {
                            "usage": {
                                "prompt_tokens": 10,
                                "completion_tokens": 20,
                                "completion_tokens_details": {"reasoning_tokens": 7},
                            }
                        }
                    ]
                },
            )()
        ],
        [0],
        proposer_index=0,
    )
    assert usage.output_tokens == 27

    from dspy.core.types import (
        LMHistoryEntry,
        LMMessage,
        LMOutput,
        LMRequest,
        LMResponse,
        LMTextPart,
        LMUsage,
    )

    typed_entry = LMHistoryEntry(
        request=LMRequest(
            model="synthetic-model",
            messages=[LMMessage(role="user", parts=[LMTextPart(text="synthetic")])],
        ),
        response=LMResponse(
            model="synthetic-model",
            outputs=[LMOutput(parts=[LMTextPart(text="synthetic-result")])],
            usage=LMUsage(prompt_tokens=10, completion_tokens=20, reasoning_tokens=7),
        ),
        timestamp="2026-08-09T00:00:00+00:00",
        uuid="synthetic-history-entry",
    )
    typed_usage = _history_usage(
        [type("TypedLM", (), {"history": [typed_entry]})()],
        [0],
        proposer_index=0,
    )
    assert typed_usage.proposer_calls == 1
    assert typed_usage.input_tokens == 10
    assert typed_usage.output_tokens == 27

    ledger = BudgetLedger(tmp_path, config, pilot=False)
    ledger.initialize()
    ledger.reserve(
        "proposer",
        task_calls=250,
        proposer_calls=250,
        retries=250,
        input_tokens=12_500_000,
        output_tokens=2_000_000,
    )
    assert ledger.load().counters.proposer_cost_usd == 49
    assert not ledger.can_fit(
        UsageCounters(
            task_invocations=1,
            proposer_calls=1,
            infrastructure_retries=1,
            proposer_input_tokens=1,
            proposer_output_tokens=1,
        )
    )


@pytest.mark.parametrize("top_level_reasoning", [None, 7])
def test_complete_dspy_typed_post_response_usage_adaptation_path(
    top_level_reasoning: int | None,
) -> None:
    from dspy.core.types import (
        LMHistoryEntry,
        LMMessage,
        LMOutput,
        LMRequest,
        LMResponse,
        LMTextPart,
        LMUsage,
    )
    from litellm.types.utils import CompletionTokensDetailsWrapper

    details = CompletionTokensDetailsWrapper(reasoning_tokens=7)
    typed_usage = LMUsage(
        input_tokens=10,
        output_tokens=20,
        reasoning_tokens=top_level_reasoning,
        completion_tokens_details=details,
    )
    assert isinstance(typed_usage.completion_tokens_details, CompletionTokensDetailsWrapper)
    entry = LMHistoryEntry(
        request=LMRequest(
            model="synthetic-model",
            messages=[LMMessage(role="user", parts=[LMTextPart(text="synthetic")])],
        ),
        response=LMResponse(
            model="synthetic-model",
            outputs=[LMOutput(parts=[LMTextPart(text="synthetic-result")])],
            usage=typed_usage,
        ),
        timestamp="2026-08-09T00:00:00+00:00",
        uuid="synthetic-nested-history-entry",
    )

    usage = _history_usage(
        [type("TypedLM", (), {"history": [entry]})()],
        [0],
        proposer_index=0,
    )

    assert usage.proposer_calls == 1
    assert usage.input_tokens == 10
    assert usage.output_tokens == 27


@pytest.mark.parametrize(
    ("reported_usage", "expected_input", "expected_output"),
    [
        ({"prompt_tokens": 10, "completion_tokens": 20}, 10, 20),
        (
            {
                "prompt_tokens": 10,
                "input_tokens": 11,
                "completion_tokens": 20,
                "output_tokens": 21,
                "completion_tokens_details": None,
            },
            11,
            21,
        ),
        ({"prompt_tokens": 10, "completion_tokens": 20, "reasoning_tokens": 7}, 10, 27),
        (
            {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "completion_tokens_details": {"reasoning_tokens": 7},
            },
            10,
            27,
        ),
        (
            {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "reasoning_tokens": 7,
                "completion_tokens_details": {"reasoning_tokens": 7},
            },
            10,
            27,
        ),
        (
            {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "reasoning_tokens": 5,
                "completion_tokens_details": {"reasoning_tokens": 7},
            },
            10,
            27,
        ),
    ],
)
def test_legacy_usage_shapes_and_reasoning_aliases_are_accounted_once(
    reported_usage: dict[str, object], expected_input: int, expected_output: int
) -> None:
    usage = _history_usage(
        [type("LegacyLM", (), {"history": [{"usage": reported_usage}]})()],
        [0],
        proposer_index=0,
    )

    assert usage.input_tokens == expected_input
    assert usage.output_tokens == expected_output


def test_model_dump_only_usage_shape_is_supported() -> None:
    class DumpOnlyUsage:
        def model_dump(self, **_kwargs: object) -> dict[str, object]:
            return {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "completion_tokens_details": {"reasoning_tokens": 7},
            }

    usage = _history_usage(
        [type("DumpLM", (), {"history": [{"usage": DumpOnlyUsage()}]})()],
        [0],
        proposer_index=0,
    )

    assert usage.input_tokens == 10
    assert usage.output_tokens == 27


@pytest.mark.parametrize(
    "reported_usage",
    [
        {"unknown_populated_usage": 1},
        {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "completion_tokens_details": object(),
        },
    ],
)
def test_unsupported_populated_usage_structure_fails_closed(
    reported_usage: dict[str, object],
) -> None:
    with pytest.raises(TypeError, match="unsupported populated DSPy usage structure"):
        _history_usage(
            [type("UnsupportedLM", (), {"history": [{"usage": reported_usage}]})()],
            [0],
            proposer_index=0,
        )


def test_synthetic_gate_diagnostics_are_boundary_aware_and_privacy_safe() -> None:
    class LMHistoryEntry:
        pass

    try:
        LMHistoryEntry().get("usage")  # type: ignore[attr-defined]
    except AttributeError as exc:
        message = sanitized_exception_message(exc)
        frames = application_stack_frames(exc, Path(__file__).parents[1])
    else:
        raise AssertionError("synthetic typed-history reproduction did not fail")

    assert message == "'LMHistoryEntry' object has no attribute 'get'"
    assert frames
    assert frames[-1]["file"] == "tests/test_bench_optimization.py"
    assert frames[-1]["function"] == (
        "test_synthetic_gate_diagnostics_are_boundary_aware_and_privacy_safe"
    )
    assert failure_boundary(request_started=False, response_finished=False) == (
        "before-request-submission"
    )
    assert failure_boundary(request_started=True, response_finished=False) == "during-provider-call"
    assert failure_boundary(request_started=True, response_finished=True) == (
        "adapting-provider-response"
    )
    assert sanitized_exception_message(ValueError("secret-bearing provider detail")) == (
        "external or value-bearing exception details redacted"
    )
    private_filename = Path(__file__).parents[1] / ".chronicle" / "private" / "gate.py"
    try:
        exec(
            compile(
                "raise AttributeError(\"'LMHistoryEntry' object has no attribute 'get'\")",
                str(private_filename),
                "exec",
            )
        )
    except AttributeError as exc:
        private_frames = application_stack_frames(exc, Path(__file__).parents[1])
    else:
        raise AssertionError("synthetic private-path traceback did not fail")
    assert private_frames[-1]["file"] == "<private-artifact>/gate.py"


def test_optional_import_boundary_does_not_import_dspy() -> None:
    before = set(sys.modules)
    __import__("bench.optimization.models")
    assert not ({"dspy", "gepa"} & (set(sys.modules) - before))


def test_ordinary_and_optimization_extra_imports_in_fresh_processes() -> None:
    ordinary = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys, bench.__main__; assert 'dspy' not in sys.modules; "
            "assert 'gepa' not in sys.modules",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert ordinary.returncode == 0, ordinary.stderr
    extra = subprocess.run(
        [
            sys.executable,
            "-c",
            "import dspy, gepa; from bench.optimization.compat import verify_compatibility; "
            "verify_compatibility()",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert extra.returncode == 0, extra.stderr


def test_exact_pinned_optimizer_api_and_result_schema() -> None:
    result = verify_compatibility()
    assert result["versions"] == {"dspy": "3.3.0", "gepa": "0.1.1"}
    assert set(result["gepa_result_fields"]) == EXPECTED_RESULT_FIELDS


def test_production_candidate_adapter_is_networkless_injected_and_identity_bound(
    tmp_path: Path,
) -> None:
    config_path = synthetic_workspace(tmp_path)
    config = load_optimization_config(config_path)
    authority = verify_authority(config, config_path)
    candidate = baseline_package(tmp_path / "tasks.yaml")
    client = FakeLiteLLMClient()
    adapter = LiteLLMCandidateAdapter(config, config_path, client=client)
    batch = adapter.evaluate(candidate, "validation", "qwen", authority)
    assert len(batch.outcomes) == 16
    assert batch.usage.task_calls == 16
    assert batch.usage.input_tokens == 16 * 12
    assert all(outcome.valid and outcome.terminal for outcome in batch.outcomes)
    assert all(request.retries == 0 for request in client.requests)

    mismatched = LiteLLMCandidateAdapter(
        config,
        config_path,
        client=FakeLiteLLMClient(provider="unexpected"),
    )
    with pytest.raises(ValueError, match="response identity mismatch"):
        mismatched.evaluate(candidate, "validation", "qwen", authority)


def test_bootstrap_post_compile_failure_carries_measured_history_usage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import dspy
    from bench.optimization import production

    config_path = synthetic_workspace(tmp_path)
    config = load_optimization_config(config_path)
    authority = verify_authority(config, config_path)
    baseline = baseline_package(tmp_path / "tasks.yaml")
    optimizer = object.__new__(DspyOptimizerAdapter)
    optimizer.config = config
    optimizer.config_path = config_path
    optimizer.authority = authority
    optimizer.tasks = load_task_catalog(tmp_path / "tasks.yaml")
    optimizer.candidate_lms = {
        "qwen": dspy.utils.DummyLM([{"response_json": "{}"}] * 20),
        "phi": dspy.utils.DummyLM([{"response_json": "{}"}] * 20),
    }
    optimizer._metric = lambda *args, **kwargs: True

    def fail_extraction(*args, **kwargs):
        del args, kwargs
        raise ValueError("synthetic post-compile extraction failure")

    def measured_history(lms, before, proposer_index=None):
        assert proposer_index is None
        assert sum(len(lm.history) - start for lm, start in zip(lms, before, strict=True)) > 0
        return AdapterUsage(task_calls=2, retries=1, input_tokens=17, output_tokens=9)

    monkeypatch.setattr(production, "demonstrations_from_program", fail_extraction)
    monkeypatch.setattr(production, "_history_usage", measured_history)
    with pytest.raises(OptimizerOperationError) as captured:
        optimizer.bootstrap(baseline, authority)
    assert captured.value.failure_category == "ValueError"
    assert captured.value.usage == AdapterUsage(
        task_calls=2,
        retries=1,
        input_tokens=17,
        output_tokens=9,
    )


@pytest.mark.parametrize(
    ("score", "accepted"),
    [
        (False, False),
        (0, False),
        (0.998999999, False),
        (0.999, True),
        (1, True),
        (True, True),
    ],
)
def test_bootstrap_metric_acceptance_returns_literal_boolean(score, accepted: bool) -> None:
    result = bootstrap_metric_acceptance(score)
    assert result is accepted


def test_bootstrap_metric_acceptance_reads_rich_prediction_without_mutating_it() -> None:
    import dspy

    prediction = dspy.Prediction(score=0.999, feedback="Synthetic deterministic feedback.")
    assert bootstrap_metric_acceptance(prediction) is True
    assert prediction.score == 0.999
    assert prediction.feedback == "Synthetic deterministic feedback."


@pytest.mark.parametrize(
    "value",
    [None, "0.999", object(), complex(0.999, 0), float("nan"), float("inf")],
)
def test_bootstrap_metric_acceptance_fails_closed_for_unsupported_scores(value) -> None:
    with pytest.raises((TypeError, ValueError), match="metric score"):
        bootstrap_metric_acceptance(value)


def test_real_dspy_rejects_invalid_rich_metric_demo_without_retry_or_repair() -> None:
    import dspy

    task = TASK_ORDER[0]
    selected_input = "Synthetic Bootstrap input."
    response_json = json.dumps(synthetic_outputs(1)[task], sort_keys=True)
    example = dspy.Example(
        task=task,
        model_id="qwen",
        selected_input=selected_input,
        response_json=response_json,
    ).with_inputs("task", "model_id", "selected_input")
    observed_lms = []
    program = build_program(
        baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml"),
        {"qwen": dspy.utils.DummyLM([{"response_json": "{malformed"}])},
    )

    compiled = compile_bootstrap(
        program,
        [example],
        lambda *args, **kwargs: dspy.Prediction(score=0.0, feedback="invalid"),
        task=task,
        history_sink=observed_lms.extend,
    )

    demos = compiled.task_0.demos
    assert len(demos) == 1
    assert demos[0].get("augmented") is not True
    assert len(compiled._chronicle_demo_authority) == 1
    assert next(iter(compiled._chronicle_demo_authority.values())).response_json_sha256 == (
        hashlib.sha256(response_json.encode()).hexdigest()
    )
    assert sum(len(lm.history) for lm in observed_lms) == 1


def test_real_dspy_accepts_valid_rich_metric_demo_and_binds_provenance() -> None:
    import dspy

    task = TASK_ORDER[0]
    selected_input = "Synthetic accepted Bootstrap input."
    response_json = json.dumps(synthetic_outputs(1)[task], sort_keys=True)
    example = dspy.Example(
        task=task,
        model_id="qwen",
        selected_input=selected_input,
        response_json=response_json,
    ).with_inputs("task", "model_id", "selected_input")
    program = build_program(
        baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml"),
        {"qwen": dspy.utils.DummyLM([{"response_json": response_json}])},
    )

    compiled = compile_bootstrap(
        program,
        [example],
        lambda *args, **kwargs: dspy.Prediction(score=0.999, feedback="valid"),
        task=task,
    )

    augmented = [demo for demo in compiled.task_0.demos if demo.get("augmented") is True]
    assert len(augmented) == 1
    assert id(augmented[0]) in compiled._chronicle_demo_authority


def test_bootstrap_compiled_provenance_failure_carries_measured_history_usage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from bench.optimization import production

    config_path = synthetic_workspace(tmp_path)
    config = load_optimization_config(config_path)
    authority = verify_authority(config, config_path)
    baseline = baseline_package(tmp_path / "tasks.yaml")
    optimizer = object.__new__(DspyOptimizerAdapter)
    optimizer.config = config
    optimizer.config_path = config_path
    optimizer.authority = authority
    optimizer.tasks = load_task_catalog(tmp_path / "tasks.yaml")
    optimizer.candidate_lms = {}

    def fail_provenance(*args, history_sink, **kwargs):
        del args, kwargs
        history_sink(
            [
                type(
                    "CopiedTeacherLM",
                    (),
                    {"history": [{"usage": {"prompt_tokens": 17, "completion_tokens": 9}}]},
                )()
            ]
        )
        raise ValueError("synthetic compiled provenance extraction failure")

    monkeypatch.setattr(production, "compile_bootstrap", fail_provenance)
    with pytest.raises(OptimizerOperationError, match="post-inference") as captured:
        optimizer.bootstrap(baseline, authority)
    assert captured.value.failure_category == "ValueError"
    assert captured.value.usage == AdapterUsage(task_calls=1, input_tokens=17, output_tokens=9)


def test_bootstrap_final_authority_failure_carries_measured_history_usage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from bench.optimization import production

    config_path = synthetic_workspace(tmp_path)
    config = load_optimization_config(config_path)
    authority = verify_authority(config, config_path)
    baseline = baseline_package(tmp_path / "tasks.yaml")
    optimizer = object.__new__(DspyOptimizerAdapter)
    optimizer.config = config
    optimizer.config_path = config_path
    optimizer.authority = authority
    optimizer.tasks = load_task_catalog(tmp_path / "tasks.yaml")
    optimizer.candidate_lms = {}

    def compile_with_history(program, *args, history_sink, **kwargs):
        del args, kwargs
        history_sink(
            [
                type(
                    "CopiedTeacherLM",
                    (),
                    {"history": [{"usage": {"prompt_tokens": 5, "completion_tokens": 3}}]},
                )()
            ]
        )
        return program

    monkeypatch.setattr(production, "compile_bootstrap", compile_with_history)
    monkeypatch.setattr(
        production,
        "verify_demonstration_authority",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ValueError("synthetic final authority failure")
        ),
    )
    with pytest.raises(OptimizerOperationError, match="authority validation") as captured:
        optimizer.bootstrap(baseline, authority)
    assert captured.value.failure_category == "ValueError"
    assert captured.value.usage == AdapterUsage(task_calls=4, input_tokens=20, output_tokens=12)


def test_real_dspy_bootstrap_demos_are_packaged_and_replayed_without_network(
    tmp_path: Path,
) -> None:
    import dspy

    config_path = synthetic_workspace(tmp_path)
    config = load_optimization_config(config_path)
    authority = verify_authority(config, config_path)
    baseline = baseline_package(tmp_path / "tasks.yaml")
    dummy_answers = [{"response_json": "{}"}] * 200
    optimizer = object.__new__(DspyOptimizerAdapter)
    optimizer.config = config
    optimizer.config_path = config_path
    optimizer.authority = authority
    optimizer.tasks = load_task_catalog(tmp_path / "tasks.yaml")
    optimizer.candidate_lms = {
        "qwen": dspy.utils.DummyLM(list(dummy_answers)),
        "phi": dspy.utils.DummyLM(list(dummy_answers)),
    }
    optimizer._metric = lambda *args, **kwargs: False

    proposal = optimizer.bootstrap(baseline, authority)
    assert all(len(proposal.demonstrations[task]) == 1 for task in TASK_ORDER)
    candidate = mutate_package(
        baseline,
        proposal.prompts,
        optimizer="bootstrap-few-shot",
        proposer_id=None,
        mutation_ordinal=1,
        strategy=proposal.strategy,
        demonstrations=proposal.demonstrations,
    )
    assert candidate.candidate_id != baseline.candidate_id
    duplicated = {task: list(values) for task, values in proposal.demonstrations.items()}
    duplicated[TASK_ORDER[0]] = duplicated[TASK_ORDER[0]] * 2
    with pytest.raises(ValidationError, match="one labeled/bootstrapped"):
        mutate_package(
            baseline,
            proposal.prompts,
            optimizer="bootstrap-few-shot",
            proposer_id=None,
            mutation_ordinal=2,
            demonstrations=duplicated,
        )
    demo_text = proposal.demonstrations[TASK_ORDER[0]][0].selected_input
    assert not scan_package(candidate, [demo_text], environment={}).eligible
    path = tmp_path / "bootstrap-candidate.json"
    write_package(path, candidate)
    assert read_package(path) == candidate
    verify_demonstration_authority(candidate, optimizer.tasks, authority)

    client = FakeLiteLLMClient()
    batch = LiteLLMCandidateAdapter(config, config_path, client=client).evaluate(
        candidate, "validation", "qwen", authority
    )
    assert len(batch.outcomes) == 16
    for request in client.requests:
        assert [message["role"] for message in request.messages] == [
            "system",
            "user",
            "assistant",
            "user",
        ]


@pytest.mark.parametrize("trusted_model", ["qwen", "phi"])
def test_real_dspy_omits_metadata_but_compile_provenance_binds_duplicate_inputs(
    trusted_model: str,
) -> None:
    import dspy

    task = TASK_ORDER[0]
    duplicate_input = "Synthetic duplicate input shared by both candidate models."
    response_json = json.dumps(synthetic_outputs(1)[task], sort_keys=True)
    model_order = [trusted_model, "phi" if trusted_model == "qwen" else "qwen"]
    examples = [
        dspy.Example(
            task=task,
            model_id=model_id,
            selected_input=duplicate_input,
            response_json=response_json,
        ).with_inputs("task", "model_id", "selected_input")
        for model_id in model_order
    ]
    answer = {"response_json": response_json}
    program = build_program(
        baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml"),
        {
            "qwen": dspy.utils.DummyLM([answer] * 4),
            "phi": dspy.utils.DummyLM([answer] * 4),
        },
    )
    compiled = compile_bootstrap(program, examples, lambda *args, **kwargs: True, task=task)
    raw_demo = compiled.task_0.demos[0]
    raw = raw_demo.toDict()
    assert set(raw) == {"selected_input", "response_json", "augmented"}
    assert "task" not in raw and "model_id" not in raw

    authorized = {
        (task, "qwen", duplicate_input): f"c001--{task}",
        (task, "phi", duplicate_input): f"c002--{task}",
    }
    demonstrations = demonstrations_from_program(compiled, task, authorized)
    assert len(demonstrations) == 1
    assert demonstrations[0].model_id == trusted_model
    assert demonstrations[0].case_alias == authorized[(task, trusted_model, duplicate_input)]


def test_bootstrap_demo_provenance_fails_closed_for_missing_ambiguous_or_foreign() -> None:
    import dspy

    task = TASK_ORDER[0]
    selected_input = "Synthetic trusted input."
    response_json = json.dumps(synthetic_outputs(1)[task], sort_keys=True)
    example = dspy.Example(
        task=task,
        model_id="qwen",
        selected_input=selected_input,
        response_json=response_json,
    ).with_inputs("task", "model_id", "selected_input")
    program = build_program(
        baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml"),
        {
            "qwen": dspy.utils.DummyLM([{"response_json": response_json}] * 2),
            "phi": dspy.utils.DummyLM([{"response_json": response_json}] * 2),
        },
    )
    compiled = compile_bootstrap(program, [example], lambda *args, **kwargs: True, task=task)
    demo = compiled.task_0.demos[0]
    authorized = {(task, "qwen", selected_input): f"c001--{task}"}
    trusted = compiled._chronicle_demo_authority[id(demo)]

    compiled._chronicle_demo_authority[id(demo)] = [trusted, trusted]
    with pytest.raises(ValueError, match="missing or ambiguous"):
        demonstrations_from_program(compiled, task, authorized)
    compiled._chronicle_demo_authority[id(demo)] = DemoAuthority(
        task=task,
        model_id="foreign",
        selected_input_sha256=trusted.selected_input_sha256,
        response_json_sha256=trusted.response_json_sha256,
    )
    with pytest.raises(ValueError, match="task/model"):
        demonstrations_from_program(compiled, task, authorized)
    compiled._chronicle_demo_authority[id(demo)] = DemoAuthority(
        task=TASK_ORDER[1],
        model_id="qwen",
        selected_input_sha256=trusted.selected_input_sha256,
        response_json_sha256=trusted.response_json_sha256,
    )
    with pytest.raises(ValueError, match="task/model"):
        demonstrations_from_program(compiled, task, authorized)


@pytest.mark.parametrize("field", ["selected_input", "response_json"])
def test_bootstrap_demo_content_is_bound_to_compile_and_train_authority(field: str) -> None:
    import dspy

    task = TASK_ORDER[0]
    selected_input = "Synthetic trusted input."
    response_json = json.dumps(synthetic_outputs(1)[task], sort_keys=True)
    example = dspy.Example(
        task=task,
        model_id="qwen",
        selected_input=selected_input,
        response_json=response_json,
    ).with_inputs("task", "model_id", "selected_input")
    program = build_program(
        baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml"),
        {
            "qwen": dspy.utils.DummyLM([{"response_json": response_json}] * 2),
            "phi": dspy.utils.DummyLM([{"response_json": response_json}] * 2),
        },
    )
    compiled = compile_bootstrap(program, [example], lambda *args, **kwargs: True, task=task)
    predictor = compiled.task_0
    original = predictor.demos[0]
    trusted = compiled._chronicle_demo_authority[id(original)]
    values = original.toDict()
    values[field] = "foreign"
    replacement = dspy.Example(**values)
    predictor.demos = [replacement]
    compiled._chronicle_demo_authority[id(replacement)] = trusted
    with pytest.raises(ValueError, match="compile provenance"):
        demonstrations_from_program(
            compiled,
            task,
            {(task, "qwen", selected_input): f"c001--{task}"},
        )

    predictor.demos = [original]
    with pytest.raises(ValueError, match="outside train authority"):
        demonstrations_from_program(compiled, task, {})


def test_bootstrap_demonstrations_round_trip_and_change_candidate_identity(
    tmp_path: Path,
) -> None:
    task = TASK_ORDER[0]
    baseline = baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml")
    first_demo = demonstration_value(
        kind="bootstrapped",
        case_alias=f"c001--{task}",
        model_id="qwen",
        selected_input="Synthetic selected input.",
        response_json='{"value": 1}',
    )
    second_demo = demonstration_value(
        kind="bootstrapped",
        case_alias=f"c001--{task}",
        model_id="qwen",
        selected_input="Synthetic selected input.",
        response_json='{"value": 2}',
    )

    def candidate_with(demo):
        return mutate_package(
            baseline,
            {name: baseline.prompts[name].text for name in TASK_ORDER},
            optimizer="bootstrap-few-shot",
            proposer_id=None,
            mutation_ordinal=1,
            strategy="synthetic-authority-test",
            demonstrations={name: [demo] if name == task else [] for name in TASK_ORDER},
        )

    first = candidate_with(first_demo)
    second = candidate_with(second_demo)
    assert first.candidate_id != second.candidate_id
    path = tmp_path / "bootstrap-round-trip.json"
    write_package(path, first)
    assert read_package(path) == first


def test_four_component_program_and_safe_state_boundary() -> None:
    package = baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml")
    program = build_program(package)
    assert prompts_from_program(program) == {
        task: package.prompts[task].text for task in TASK_ORDER
    }
    assert len(program.named_predictors()) == 4
    with pytest.raises(ValueError, match="unsafe"):
        load_state_only(object(), Path("program.pkl"))


def test_candidate_identity_is_stable_across_result_evidence(tmp_path: Path) -> None:
    package = baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml")
    original = package.candidate_id
    authority = ResultAuthority(
        run_id="synthetic",
        application_commit=APPLICATION_COMMIT,
        config_sha256="1" * 64,
        train_manifest_sha256="2" * 64,
        validation_manifest_sha256="3" * 64,
        model_artifact_sha256={"qwen": "4" * 64, "phi": "5" * 64},
        proposer_identity_sha256="6" * 64,
        optimizer_identity_sha256="7" * 64,
    )
    payload = {
        "format_version": 1,
        "candidate_id": original,
        "authority": authority.model_dump(mode="json"),
        "train_metric": metric(candidate_id=original).model_dump(mode="json"),
        "validation_metric": metric(candidate_id=original).model_dump(mode="json"),
        "validation_model_valid": {"qwen": 15, "phi": 15},
        "validation_task_valid": {task: 7 for task in TASK_ORDER},
        "prompt_token_max": 1000,
        "request_envelope": RequestEnvelopeEvidence(
            estimator_version="complete-request-envelope-v1",
            context_window=8192,
            max_case_alias="c001--conversation-summary",
            max_task="conversation-summary",
            input_tokens=7000,
            output_allowance_tokens=1000,
            total_tokens=8000,
            fits_context=True,
        ).model_dump(mode="json"),
        "prompt_fits_context": True,
        "privacy": PrivacyEvidence(
            scanner_version="optimizer-prompt-privacy-v1",
            ngram_words=8,
            eligible=True,
            finding_count=0,
            counts={},
            evidence_sha256="8" * 64,
        ).model_dump(mode="json"),
        "accounting": CandidateAccounting(
            task_invocations=80,
            proposer_calls=0,
            infrastructure_retries=0,
            terminal_invocations=80,
            expected_invocations=80,
            failures={},
            latency_ms=1,
            usage={},
        ).model_dump(mode="json"),
        "trial_id": "trial",
    }
    result = CandidateResult(result_id=result_identity(payload), **payload)
    assert result.candidate_id == package.candidate_id == original
    changed = result.model_copy(update={"prompt_token_max": 1001})
    changed_payload = changed.model_dump(mode="json", exclude={"result_id"})
    changed = CandidateResult(result_id=result_identity(changed_payload), **changed_payload)
    assert changed.candidate_id == original
    assert changed.result_id != result.result_id


@pytest.mark.parametrize(
    ("better", "worse"),
    [
        (
            metric(total_valid=31, semantic_agreement=0),
            metric(total_valid=30, semantic_agreement=1),
        ),
        (metric(worst_model_valid=16, semantic_agreement=0), metric(semantic_agreement=1)),
        (metric(minimum_task_valid=8, semantic_agreement=0), metric(semantic_agreement=1)),
        (metric(semantic_agreement=0.6), metric(semantic_agreement=0.5, prompt_tokens=0)),
        (metric(candidate_id="a"), metric(candidate_id="b")),
    ],
)
def test_metric_order_and_scalar_dominance(better: MetricVector, worse: MetricVector) -> None:
    assert better > worse
    if better.ordering_key()[:3] != worse.ordering_key()[:3]:
        assert better.scalar() > worse.scalar()


def test_feedback_and_privacy_never_retain_source_text() -> None:
    assert render_feedback([Diagnostic(category="invalid-enum", expected="completed")])
    with pytest.raises(ValidationError, match="forbidden"):
        Diagnostic(category="schema", observed="API_KEY=private-value")
    baseline = baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml")
    leaked = mutate_package(
        baseline,
        {
            **{task: baseline.prompts[task].text for task in TASK_ORDER},
            TASK_ORDER[0]: "Special Alpha 4817",
        },
        optimizer="gepa",
        proposer_id="synthetic",
        mutation_ordinal=1,
    )
    result = scan_package(leaked, [], exact_values=["Special Alpha", "4817"], environment={})
    assert not result.eligible
    assert "Special Alpha" not in result.model_dump_json()


def test_budget_reserves_before_boundary_and_persists_resume(tmp_path: Path) -> None:
    config = load_optimization_config(synthetic_workspace(tmp_path))
    root = tmp_path / "budget"
    ledger = BudgetLedger(root, config)
    ledger.initialize()
    exact = ledger.reserve(
        "proposer", proposer_calls=250, input_tokens=12500000, output_tokens=2000000
    )
    with pytest.raises(ValueError, match="ceiling"):
        ledger.reserve("proposer", proposer_calls=1)
    actual = exact.reserved.model_copy(update={"proposer_calls": 249})
    state = ledger.reconcile(exact.reservation_id, actual)
    assert state.counters.proposer_calls == 249
    resumed = BudgetLedger(root, config).load()
    assert resumed.state_sha256 == state.state_sha256


def test_achievable_next_operation_uses_every_total_ceiling(tmp_path: Path) -> None:
    config = load_optimization_config(synthetic_workspace(tmp_path))
    ledger = BudgetLedger(tmp_path / "capacity", config, pilot=False)
    ledger.initialize()
    operation = UsageCounters(
        candidates=1,
        task_invocations=1,
        proposer_calls=1,
        proposer_input_tokens=50000,
        proposer_output_tokens=8000,
        compute_hours=1,
        compute_cost_usd=1,
    )
    assert ledger.can_fit(operation)
    assert ledger.achievable_operations(operation) == 12


def test_budget_retains_interrupted_and_missing_usage_reservation(tmp_path: Path) -> None:
    config = load_optimization_config(synthetic_workspace(tmp_path))
    ledger = BudgetLedger(tmp_path / "budget", config)
    ledger.initialize()
    reservation = ledger.reserve("task", task_calls=1, retries=1)
    with pytest.raises(ValueError, match="usage is missing"):
        ledger.reconcile(reservation.reservation_id, None, interrupted=True)
    state = ledger.load()
    assert state.counters.task_invocations == 1
    assert state.reservations[-1].status == "interrupted"


def test_measured_bootstrap_failure_and_fresh_attempt_remain_append_only(
    tmp_path: Path,
) -> None:
    config_path = synthetic_workspace(
        tmp_path, pilot_candidates=1, total_candidates=1, task_invocations=500
    )
    candidate = FakeCandidateAdapter()
    clock = StepClock()
    with pytest.raises(OptimizerOperationError, match="post-compile"):
        run_optimization(
            config_path,
            ExecutionAdapters(candidate, MeasuredBootstrapFailureAdapter()),
            resume=False,
            identity_probe=clean_identity,
            monotonic_ns=clock,
        )

    root = tmp_path / "private" / "run"
    state_before = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    p0_result_id = state_before["baseline_result_id"]
    attempt_path = root / "trials" / "proposal-bootstrap-few-shot-0001" / "attempts" / "0001.json"
    first_attempt_bytes = attempt_path.read_bytes()
    first = TrialStore(root).current("proposal-bootstrap-few-shot-0001")
    assert first is not None
    assert first.status == "interrupted"
    assert first.failure_category == "ValueError"
    assert first.accounting["optimizer_usage"] == {
        "task_calls": 2,
        "proposer_calls": 0,
        "input_tokens": 17,
        "output_tokens": 9,
        "compute_hours": 7 / 3_600_000,
        "compute_cost_usd": (7 / 3_600_000) * (12.05 / 12),
        "retries": 1,
        "latency_ms": 7,
    }
    budget = BudgetLedger(root, load_optimization_config(config_path)).load()
    failed_reservations = [
        reservation for reservation in budget.reservations if reservation.status == "interrupted"
    ]
    assert len(failed_reservations) == 1
    assert failed_reservations[0].reserved.task_invocations == 3
    assert failed_reservations[0].actual is not None
    assert failed_reservations[0].actual.task_invocations == 2
    assert failed_reservations[0].actual.infrastructure_retries == 1

    result = run_optimization(
        config_path,
        ExecutionAdapters(candidate, FakeOptimizerAdapter(max_gepa=0)),
        resume=True,
        identity_probe=clean_identity,
        monotonic_ns=clock,
    )
    assert result["status"] == "pilot-no-improvement"
    assert attempt_path.read_bytes() == first_attempt_bytes
    attempts = TrialStore(root).attempts("proposal-bootstrap-few-shot-0001")
    assert len(attempts) == 2
    assert attempts[0] == first
    assert attempts[1].status == "complete"
    assert "optimizer_usage" in attempts[1].accounting
    state_after = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    assert state_after["baseline_result_id"] == p0_result_id
    assert len(state_after["bootstrap_result_ids"]) == 1
    retained = BudgetLedger(root, load_optimization_config(config_path)).load().reservations
    assert failed_reservations[0] in retained


@pytest.mark.parametrize("mode", ["missing", "dangling", "stale", "hash"])
def test_trial_authority_rejects_every_invalid_pointer(tmp_path: Path, mode: str) -> None:
    store = TrialStore(tmp_path)
    store.append("trial", "interrupted", {"calls": 1})
    store.append("trial", "failed", {"calls": 2})
    current = tmp_path / "trials" / "trial" / "current.json"
    if mode == "missing":
        current.unlink()
    else:
        value = json.loads(current.read_text(encoding="utf-8"))
        if mode == "dangling":
            value["current_attempt"] = 3
        elif mode == "stale":
            value["current_attempt"] = 1
        else:
            value["attempt_sha256"] = "f" * 64
        current.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="missing|dangling|stale|mismatch"):
        store.current("trial")


def test_preflight_proves_complete_development_authority(tmp_path: Path) -> None:
    result = preflight(synthetic_workspace(tmp_path))
    assert result["zero_holdout"] is True
    assert result["authority_files"] == {"inputs": 10, "references": 40}
    assert result["split"][0]["conversations"] == 6
    assert result["split"][1]["conversations"] == 4


@pytest.mark.parametrize(
    "tamper",
    ["overlap", "foreign-parent", "altered-order", "duplicate", "missing-input", "reference"],
)
def test_preflight_rejects_split_and_authority_tampering(tmp_path: Path, tamper: str) -> None:
    config_path = synthetic_workspace(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    train_path = tmp_path / config["train_manifest"]["path"]
    validation_path = tmp_path / config["validation_manifest"]["path"]
    if tamper in {"overlap", "foreign-parent", "altered-order", "duplicate"}:
        value = json.loads(validation_path.read_text(encoding="utf-8"))
        train = json.loads(train_path.read_text(encoding="utf-8"))
        if tamper == "overlap":
            value["ordered_conversations"][0] = train["ordered_conversations"][0]
        elif tamper == "foreign-parent":
            value["parent_development_manifest_sha256"] = "e" * 64
        elif tamper == "altered-order":
            value["ordered_conversations"][0:2] = reversed(value["ordered_conversations"][0:2])
        else:
            value["ordered_conversations"][1] = value["ordered_conversations"][0]
        value["manifest_sha256"] = digest(
            {k: v for k, v in value.items() if k != "manifest_sha256"}
        )
        write_json(validation_path, value)
        config["validation_manifest"]["sha256"] = value["manifest_sha256"]
        config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    elif tamper == "missing-input":
        next((tmp_path / "private" / "inputs").glob("*.json")).unlink()
    else:
        reference = next((tmp_path / "private" / "references").glob("*/*.json"))
        value = json.loads(reference.read_text(encoding="utf-8"))
        value["source_conversation_id"] = 999
        write_json(reference, value)
    with pytest.raises((ValueError, ValidationError)):
        preflight(config_path)


def test_end_to_end_synthetic_optimize_resume_verify_and_shortlist(tmp_path: Path) -> None:
    config_path = synthetic_workspace(tmp_path)
    candidate = FakeCandidateAdapter()
    interrupted = FakeOptimizerAdapter(fail_gepa_once=2)
    clock = StepClock()
    with pytest.raises(ValueError, match="usage is missing"):
        run_optimization(
            config_path,
            ExecutionAdapters(candidate, interrupted),
            resume=False,
            identity_probe=clean_identity,
            monotonic_ns=clock,
        )
    root = tmp_path / "private" / "run"
    state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    assert len(state["gepa_result_ids"]) == 1
    resumed_optimizer = FakeOptimizerAdapter()
    pilot = run_optimization(
        config_path,
        ExecutionAdapters(candidate, resumed_optimizer),
        resume=True,
        identity_probe=clean_identity,
        monotonic_ns=clock,
    )
    assert pilot["status"] == "pilot-complete"
    assert pilot["pilot_checkpoint"]["decision"] == "continue"
    completed = run_optimization(
        config_path,
        ExecutionAdapters(candidate, resumed_optimizer),
        resume=True,
        identity_probe=clean_identity,
        monotonic_ns=clock,
    )
    assert completed["status"] == "complete"
    assert completed["gepa_results"] == 3
    assert completed["budget"]["proposer_calls"] == 5  # includes interruption + exhaustion
    resumed_proposal = TrialStore(root).current("proposal-gepa-0002")
    assert resumed_proposal is not None
    assert resumed_proposal.attempt == 2
    assert resumed_proposal.status == "complete"
    state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    for result_id in [state["baseline_result_id"], *state["gepa_result_ids"]]:
        result = CandidateResult.model_validate_json(
            (root / "results" / f"{result_id}.json").read_text(encoding="utf-8")
        )
        verified = verify_candidate(
            config_path, root / "candidates" / f"{result.candidate_id}.json"
        )
        assert verified["valid"] is True
    inspection = inspect_run(config_path)
    assert inspection["status"] == "complete"
    assert inspection["timing"] == {
        "optimizer_attempts": 6,
        "optimizer_wall_ms": 42,
        "candidate_wall_ms": 200,
    }
    shortlist = export_shortlist(config_path, tmp_path / "shortlist", 3)
    assert shortlist["status"] == "shortlist"
    assert shortlist["count"] == 3
    assert len(list((tmp_path / "shortlist").glob("candidate-*.json"))) == 4
    assert candidate.calls == 20  # five candidates x train/validation x two models


def test_pilot_checkpoint_stops_when_continuation_criteria_fail(tmp_path: Path) -> None:
    config_path = synthetic_workspace(
        tmp_path, pilot_candidates=2, total_candidates=5, task_invocations=500
    )
    result = run_optimization(
        config_path,
        ExecutionAdapters(FakeCandidateAdapter(gepa_valid=False), FakeOptimizerAdapter()),
        resume=False,
        identity_probe=clean_identity,
    )
    checkpoint = result["pilot_checkpoint"]
    assert result["status"] == "pilot-no-improvement"
    assert checkpoint["decision"] == "stop"
    assert checkpoint["validation_no_worse_than_p0"] is False
    assert result["gepa_results"] == 2
    assert (
        run_optimization(
            config_path,
            ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter()),
            resume=True,
            identity_probe=clean_identity,
        )["status"]
        == "pilot-no-improvement"
    )


@pytest.mark.parametrize(
    ("tradeoff", "lower_component"),
    [("worst-model", "worst_model_valid"), ("minimum-task", "minimum_task_valid")],
)
def test_pilot_rejects_total_gain_with_component_reliability_loss(
    tmp_path: Path, tradeoff: str, lower_component: str
) -> None:
    config_path = synthetic_workspace(
        tmp_path, pilot_candidates=1, total_candidates=3, task_invocations=500
    )
    result = run_optimization(
        config_path,
        ExecutionAdapters(
            FakeCandidateAdapter(reliability_tradeoff=tradeoff),
            FakeOptimizerAdapter(max_gepa=1),
        ),
        resume=False,
        identity_probe=clean_identity,
    )
    root = tmp_path / "private" / "run"
    state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    baseline = CandidateResult.model_validate_json(
        (root / "results" / f"{state['baseline_result_id']}.json").read_text(encoding="utf-8")
    )
    candidate = CandidateResult.model_validate_json(
        (root / "results" / f"{state['gepa_result_ids'][0]}.json").read_text(encoding="utf-8")
    )
    assert candidate.validation_metric.total_valid > baseline.validation_metric.total_valid
    assert getattr(candidate.validation_metric, lower_component) < getattr(
        baseline.validation_metric, lower_component
    )
    assert result["status"] == "pilot-no-improvement"
    assert result["pilot_checkpoint"]["validation_no_worse_than_p0"] is False
    assert result["pilot_checkpoint"]["decision"] == "stop"


def test_pilot_checkpoint_permits_continuation_without_rewriting_attempts(
    tmp_path: Path,
) -> None:
    config_path = synthetic_workspace(
        tmp_path, pilot_candidates=2, total_candidates=4, task_invocations=1000
    )
    adapters = ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter(max_gepa=4))
    pilot = run_optimization(config_path, adapters, resume=False, identity_probe=clean_identity)
    assert pilot["status"] == "pilot-complete"
    assert pilot["pilot_checkpoint"]["decision"] == "continue"
    root = tmp_path / "private" / "run"
    attempts_before = {
        path: path.read_bytes() for path in sorted((root / "trials").glob("*/current.json"))
    }
    checkpoint_before = pilot["pilot_checkpoint"]["checkpoint_sha256"]
    completed = run_optimization(config_path, adapters, resume=True, identity_probe=clean_identity)
    assert completed["status"] == "complete"
    assert completed["stop_reason"] == "candidate-ceiling-reached"
    assert completed["gepa_results"] == 4
    assert completed["pilot_checkpoint"]["checkpoint_sha256"] == checkpoint_before
    assert all(path.read_bytes() == value for path, value in attempts_before.items())


def test_continuation_stops_before_budget_limited_next_operation(tmp_path: Path) -> None:
    config_path = synthetic_workspace(
        tmp_path, pilot_candidates=2, total_candidates=5, task_invocations=500
    )
    adapters = ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter(max_gepa=5))
    pilot = run_optimization(config_path, adapters, resume=False, identity_probe=clean_identity)
    assert pilot["status"] == "pilot-complete"
    assert pilot["pilot_checkpoint"]["achievable_additional_candidates"] == 2
    result = run_optimization(config_path, adapters, resume=True, identity_probe=clean_identity)
    assert result["status"] == "budget-limited"
    assert result["stop_reason"] == "next-operation-exceeds-total-ceiling"
    assert result["gepa_results"] == 4
    assert result["budget"]["task_invocations"] == 481


def test_shortlist_returns_explicit_no_improvement(tmp_path: Path) -> None:
    config_path = synthetic_workspace(tmp_path, pilot_candidates=2)
    adapters = ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter(max_gepa=2))
    finish_synthetic_run(config_path, adapters)
    result = export_shortlist(config_path, tmp_path / "shortlist", 3)
    assert result["status"] == "no-improvement"
    assert result["count"] == 0


def test_shortlist_rejects_result_and_trial_tampering(tmp_path: Path) -> None:
    config_path = synthetic_workspace(tmp_path, pilot_candidates=3)
    finish_synthetic_run(
        config_path,
        ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter()),
    )
    root = tmp_path / "private" / "run"
    state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    result_path = root / "results" / f"{state['gepa_result_ids'][0]}.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    current = root / "trials" / result["trial_id"] / "current.json"
    value = json.loads(current.read_text(encoding="utf-8"))
    value["attempt_sha256"] = "0" * 64
    write_json(current, value)
    with pytest.raises((ValueError, ValidationError), match="mismatch|inconsistent"):
        export_shortlist(config_path, tmp_path / "shortlist", 3)


def test_config_aware_verify_rejects_self_consistent_contract_tampering(tmp_path: Path) -> None:
    config_path = synthetic_workspace(tmp_path, pilot_candidates=3)
    finish_synthetic_run(
        config_path,
        ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter()),
    )
    root = tmp_path / "private" / "run"
    state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    result = CandidateResult.model_validate_json(
        (root / "results" / f"{state['gepa_result_ids'][0]}.json").read_text(encoding="utf-8")
    )
    package = read_package(root / "candidates" / f"{result.candidate_id}.json")
    value = package.model_dump(mode="json", exclude={"candidate_id"})
    value["contracts"][TASK_ORDER[0]]["input_selector"] = "substituted-selector"
    malicious = CandidatePackage(candidate_id=candidate_identity(value), **value)
    path = tmp_path / "malicious.json"
    write_package(path, malicious)
    with pytest.raises(ValueError, match="accepted P0 contracts"):
        verify_candidate(config_path, path)


def test_result_authority_tampering_is_rejected_even_when_rehashed(tmp_path: Path) -> None:
    config_path = synthetic_workspace(tmp_path, pilot_candidates=3)
    finish_synthetic_run(
        config_path,
        ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter()),
    )
    root = tmp_path / "private" / "run"
    state_path = root / "run-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    old_id = state["gepa_result_ids"][0]
    result_path = root / "results" / f"{old_id}.json"
    value = json.loads(result_path.read_text(encoding="utf-8"))
    value["authority"]["config_sha256"] = "9" * 64
    value["result_id"] = result_identity(
        {key: item for key, item in value.items() if key != "result_id"}
    )
    new_id = value["result_id"]
    write_json(root / "results" / f"{new_id}.json", value)
    state["gepa_result_ids"][0] = new_id
    state["state_sha256"] = digest(
        {key: item for key, item in state.items() if key != "state_sha256"}
    )
    write_json(state_path, state)
    with pytest.raises(ValueError, match="configuration identity"):
        export_shortlist(config_path, tmp_path / "shortlist", 3)


@pytest.mark.parametrize(
    "guardrail",
    ["total", "model", "task", "privacy", "terminal", "fit", "lineage"],
)
def test_every_shortlist_guardrail_is_fail_closed(tmp_path: Path, guardrail: str) -> None:
    config_path = synthetic_workspace(tmp_path, pilot_candidates=3)
    finish_synthetic_run(
        config_path,
        ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter()),
    )
    root = tmp_path / "private" / "run"
    state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    p0 = CandidateResult.model_validate_json(
        (root / "results" / f"{state['baseline_result_id']}.json").read_text(encoding="utf-8")
    )
    result = CandidateResult.model_validate_json(
        (root / "results" / f"{state['gepa_result_ids'][0]}.json").read_text(encoding="utf-8")
    )
    package = read_package(root / "candidates" / f"{result.candidate_id}.json")
    if guardrail == "total":
        result.validation_metric.total_valid = p0.validation_metric.total_valid - 1
    elif guardrail == "model":
        result.validation_model_valid["qwen"] = p0.validation_model_valid["qwen"] - 2
    elif guardrail == "task":
        result.validation_task_valid[TASK_ORDER[0]] = p0.validation_task_valid[TASK_ORDER[0]] - 2
    elif guardrail == "privacy":
        result.privacy.eligible = False
        result.privacy.finding_count = 1
        result.privacy.counts = {"synthetic": 1}
    elif guardrail == "terminal":
        result.accounting.terminal_invocations -= 1
    elif guardrail == "fit":
        result.prompt_fits_context = False
    else:
        package.lineage.optimizer = "bootstrap-few-shot"
    assert not _eligible(package, result, p0)


def test_complete_request_envelope_inside_outside_and_promotion_rejection(
    tmp_path: Path,
) -> None:
    config_path = synthetic_workspace(tmp_path, pilot_candidates=1, total_candidates=2)
    config = load_optimization_config(config_path)
    authority = verify_authority(config, config_path)
    tasks = load_task_catalog(tmp_path / "tasks.yaml")
    baseline = baseline_package(tmp_path / "tasks.yaml")

    def with_padding(length: int) -> CandidatePackage:
        return mutate_package(
            baseline,
            {
                task: baseline.prompts[task].text
                + (("x" * length) if task == TASK_ORDER[0] else "")
                for task in TASK_ORDER
            },
            optimizer="gepa",
            proposer_id="synthetic",
            mutation_ordinal=length + 1,
        )

    low, high = 0, 40000
    while low + 1 < high:
        middle = (low + high) // 2
        if estimate_request_envelope(with_padding(middle), tasks, authority).fits_context:
            low = middle
        else:
            high = middle
    inside = estimate_request_envelope(with_padding(low), tasks, authority)
    outside = estimate_request_envelope(with_padding(high), tasks, authority)
    assert inside.total_tokens == 8192
    assert outside.total_tokens == 8193
    assert inside.output_allowance_tokens > 0

    run = run_optimization(
        config_path,
        ExecutionAdapters(
            FakeCandidateAdapter(),
            FakeOptimizerAdapter(max_gepa=1, prompt_padding=40000),
        ),
        resume=False,
        identity_probe=clean_identity,
    )
    assert run["status"] == "pilot-no-improvement"
    root = tmp_path / "private" / "run"
    state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    p0 = CandidateResult.model_validate_json(
        (root / "results" / f"{state['baseline_result_id']}.json").read_text(encoding="utf-8")
    )
    result = CandidateResult.model_validate_json(
        (root / "results" / f"{state['gepa_result_ids'][0]}.json").read_text(encoding="utf-8")
    )
    package = read_package(root / "candidates" / f"{result.candidate_id}.json")
    assert result.request_envelope.total_tokens > 8192
    assert not result.prompt_fits_context
    assert not _eligible(package, result, p0)


def test_cli_lifecycle_routes_through_synthetic_orchestrator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = synthetic_workspace(tmp_path, pilot_candidates=3)
    adapters = ExecutionAdapters(FakeCandidateAdapter(), FakeOptimizerAdapter())

    def execute(path: Path, resume: bool) -> None:
        bench_cli.emit(
            run_optimization(path.resolve(), adapters, resume=resume, identity_probe=clean_identity)
        )

    monkeypatch.setattr(bench_cli, "_execute_optimizer", execute)
    flags = [
        "--allow-remote",
        "--confirm-private-eval",
        "--confirm-proposer-disclosure",
        "--confirm-paid-budget",
    ]
    result = CliRunner().invoke(bench_cli.app, ["optimize", "--config", str(config_path), *flags])
    assert result.exit_code == 0
    assert '"status": "pilot-complete"' in result.output
    resumed = CliRunner().invoke(bench_cli.app, ["resume", "--config", str(config_path), *flags])
    assert resumed.exit_code == 0
    assert '"status": "complete"' in resumed.output
    root = tmp_path / "private" / "run"
    state = json.loads((root / "run-state.json").read_text(encoding="utf-8"))
    candidate_result = CandidateResult.model_validate_json(
        (root / "results" / f"{state['gepa_result_ids'][0]}.json").read_text(encoding="utf-8")
    )
    commands = [
        ["preflight", "--config", str(config_path)],
        ["dry-run", "--config", str(config_path)],
        ["inspect", "--config", str(config_path)],
        [
            "verify",
            "--config",
            str(config_path),
            "--package",
            str(root / "candidates" / f"{candidate_result.candidate_id}.json"),
        ],
        [
            "package",
            "--config",
            str(config_path),
            "--output",
            str(tmp_path / "p0.json"),
        ],
        [
            "export-shortlist",
            "--config",
            str(config_path),
            "--output",
            str(tmp_path / "shortlist"),
            "--limit",
            "3",
        ],
    ]
    for command in commands:
        called = CliRunner().invoke(bench_cli.app, command)
        assert called.exit_code == 0, called.output


def test_remote_cli_requires_every_disclosure_flag(tmp_path: Path) -> None:
    config_path = synthetic_workspace(tmp_path)
    for command in ("optimize", "resume"):
        result = CliRunner().invoke(bench_cli.app, [command, "--config", str(config_path)])
        assert result.exit_code == 2
        assert "requires all remote disclosure and budget flags" in result.output


def test_package_serialization_and_lineage_are_append_only(tmp_path: Path) -> None:
    baseline = baseline_package(Path(__file__).parents[1] / "ai-tasks.default.yaml")
    changed = mutate_package(
        baseline,
        {task: baseline.prompts[task].text + "\nSynthetic." for task in TASK_ORDER},
        optimizer="gepa",
        proposer_id="synthetic",
        mutation_ordinal=1,
    )
    path = tmp_path / "candidate.json"
    write_package(path, changed)
    assert read_package(path) == changed
    assert changed.lineage.parent_id == baseline.candidate_id
    with pytest.raises(ValueError, match="safe JSON"):
        write_package(tmp_path / "candidate.pkl", changed)
