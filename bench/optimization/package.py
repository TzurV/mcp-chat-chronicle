"""Stable prompt candidates and separately identified evaluation envelopes."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import Field, StrictInt, field_validator, model_validator

from bench.io import atomic_json, digest
from bench.models import TASK_ORDER, StrictModel

from .metrics import MetricVector
from .models import PromptValue, TaskContract

FINALIZER_VERSIONS = {
    "conversation-summary": "2",
    "work-mode-classification": "1",
    "last-activity": "2",
    "title-assessment": "1",
}


class CandidateLineage(StrictModel):
    parent_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    optimizer: Literal["p0", "bootstrap-few-shot", "gepa"]
    proposer_id: str | None = None
    mutation_ordinal: StrictInt = Field(default=0, ge=0)
    strategy: str = "baseline"


class CandidateDemonstration(StrictModel):
    kind: Literal["labeled", "bootstrapped"]
    case_alias: str = Field(pattern=r"^c\d{3}--[a-z-]+$")
    model_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    selected_input: str = Field(min_length=1)
    response_json: str = Field(min_length=2)
    demonstration_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def valid_hash(self) -> CandidateDemonstration:
        value = self.model_dump(mode="json", exclude={"demonstration_sha256"})
        if digest(value) != self.demonstration_sha256:
            raise ValueError("candidate demonstration identity mismatch")
        return self


class CandidatePackage(StrictModel):
    format_version: Literal[3] = 3
    candidate_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    prompts: dict[str, PromptValue]
    contracts: dict[str, TaskContract]
    demonstrations: dict[str, list[CandidateDemonstration]]
    lineage: CandidateLineage
    context_window: Literal[8192] = 8192

    @model_validator(mode="after")
    def complete(self) -> CandidatePackage:
        if (
            set(self.prompts) != set(TASK_ORDER)
            or set(self.contracts) != set(TASK_ORDER)
            or set(self.demonstrations) != set(TASK_ORDER)
        ):
            raise ValueError("candidate package must contain all four tasks")
        for task, demonstrations in self.demonstrations.items():
            kinds = [item.kind for item in demonstrations]
            if len(demonstrations) > 2 or len(kinds) != len(set(kinds)):
                raise ValueError(f"candidate {task} demonstrations exceed one labeled/bootstrapped")
            if any(item.case_alias.rsplit("--", 1)[-1] != task for item in demonstrations):
                raise ValueError("candidate demonstration task authority mismatch")
        if self.lineage.optimizer != "bootstrap-few-shot" and any(self.demonstrations.values()):
            raise ValueError("only BootstrapFewShot candidates may contain demonstrations")
        if self.candidate_id != candidate_identity(self):
            raise ValueError("candidate package identity mismatch")
        if self.lineage.optimizer == "p0" and self.lineage.parent_id is not None:
            raise ValueError("P0 candidate cannot have a parent")
        if self.lineage.optimizer != "p0" and self.lineage.parent_id is None:
            raise ValueError("optimized candidate requires a parent")
        return self


class CandidateAccounting(StrictModel):
    task_invocations: StrictInt = Field(ge=0)
    proposer_calls: StrictInt = Field(ge=0)
    infrastructure_retries: StrictInt = Field(ge=0)
    terminal_invocations: StrictInt = Field(ge=0)
    expected_invocations: StrictInt = Field(ge=0)
    failures: dict[str, StrictInt]
    latency_ms: StrictInt = Field(ge=0)
    optimizer_latency_ms: StrictInt = Field(default=0, ge=0)
    usage: dict[str, StrictInt | float]

    @field_validator("usage", mode="before")
    @classmethod
    def nonnegative_finite_usage(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        if any(
            not isinstance(key, str)
            or not key
            or isinstance(amount, bool)
            or not isinstance(amount, int | float)
            or amount < 0
            or (isinstance(amount, float) and not math.isfinite(amount))
            for key, amount in value.items()
        ):
            raise ValueError("candidate usage values must be named, finite, and nonnegative")
        return value

    @model_validator(mode="after")
    def terminal(self) -> CandidateAccounting:
        if self.terminal_invocations != self.expected_invocations:
            raise ValueError("candidate result has non-terminal invocation accounting")
        context_boundaries = self.failures.get("context-boundary", 0)
        if context_boundaries > self.expected_invocations:
            raise ValueError("candidate context-boundary accounting exceeds expected invocations")
        if self.task_invocations + context_boundaries < self.expected_invocations:
            raise ValueError("candidate task invocation accounting is incomplete")
        return self


class PrivacyEvidence(StrictModel):
    scanner_version: Literal["optimizer-prompt-privacy-v1"]
    ngram_words: Literal[8]
    eligible: bool
    finding_count: StrictInt = Field(ge=0)
    counts: dict[str, StrictInt]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def consistent(self) -> PrivacyEvidence:
        if self.eligible != (self.finding_count == 0):
            raise ValueError("privacy result eligibility/count mismatch")
        if sum(self.counts.values()) != self.finding_count:
            raise ValueError("privacy result counts do not reconcile")
        return self


class RequestEnvelopeEvidence(StrictModel):
    estimator_version: Literal["complete-request-envelope-v1"]
    context_window: Literal[8192]
    max_case_alias: str = Field(pattern=r"^c\d{3}--[a-z-]+$")
    max_task: Literal[
        "conversation-summary",
        "work-mode-classification",
        "last-activity",
        "title-assessment",
    ]
    input_tokens: StrictInt = Field(ge=0)
    output_allowance_tokens: StrictInt = Field(ge=0)
    total_tokens: StrictInt = Field(ge=0)
    fits_context: bool

    @model_validator(mode="after")
    def consistent(self) -> RequestEnvelopeEvidence:
        if self.total_tokens != self.input_tokens + self.output_allowance_tokens:
            raise ValueError("complete request token envelope does not reconcile")
        if self.fits_context != (self.total_tokens <= self.context_window):
            raise ValueError("complete request context-fit evidence is inconsistent")
        return self


class ResultAuthority(StrictModel):
    run_id: str
    application_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    config_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    train_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_artifact_sha256: dict[str, str]
    proposer_identity_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    optimizer_identity_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_authority_sha256: str | None = Field(
        default=None,
        pattern=r"^[0-9a-f]{64}$",
        exclude_if=lambda value: value is None,
    )


class CandidateResult(StrictModel):
    format_version: Literal[1] = 1
    result_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    candidate_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    authority: ResultAuthority
    train_metric: MetricVector
    validation_metric: MetricVector
    validation_model_valid: dict[str, StrictInt]
    validation_task_valid: dict[str, StrictInt]
    prompt_token_max: StrictInt = Field(ge=0)
    request_envelope: RequestEnvelopeEvidence
    prompt_fits_context: bool
    privacy: PrivacyEvidence
    accounting: CandidateAccounting
    trial_id: str

    @model_validator(mode="after")
    def complete(self) -> CandidateResult:
        if self.train_metric.candidate_id != self.candidate_id:
            raise ValueError("train metric candidate identity mismatch")
        if self.validation_metric.candidate_id != self.candidate_id:
            raise ValueError("validation metric candidate identity mismatch")
        if set(self.validation_model_valid) != set(self.authority.model_artifact_sha256):
            raise ValueError("result candidate-model accounting differs from authority")
        if set(self.validation_task_valid) != set(TASK_ORDER):
            raise ValueError("result must account for all four tasks")
        if self.prompt_fits_context != self.request_envelope.fits_context:
            raise ValueError("candidate context-fit result is inconsistent")
        if self.result_id != result_identity(self):
            raise ValueError("candidate result identity mismatch")
        return self


def candidate_identity(package: CandidatePackage | dict[str, Any]) -> str:
    value = (
        package.model_dump(mode="json", exclude={"candidate_id"})
        if isinstance(package, CandidatePackage)
        else package
    )
    return digest(value)


def result_identity(result: CandidateResult | dict[str, Any]) -> str:
    value = (
        result.model_dump(mode="json", exclude={"result_id"})
        if isinstance(result, CandidateResult)
        else result
    )
    return digest(value)


def prompt_value(text: str) -> PromptValue:
    raw = text.encode("utf-8")
    return PromptValue(
        text=text,
        sha256=hashlib.sha256(raw).hexdigest(),
        utf8_bytes=len(raw),
        token_estimate=max(1, (len(raw) + 3) // 4),
    )


def demonstration_value(
    *,
    kind: Literal["labeled", "bootstrapped"],
    case_alias: str,
    model_id: str,
    selected_input: str,
    response_json: str,
) -> CandidateDemonstration:
    payload = {
        "kind": kind,
        "case_alias": case_alias,
        "model_id": model_id,
        "selected_input": selected_input,
        "response_json": response_json,
    }
    return CandidateDemonstration(**payload, demonstration_sha256=digest(payload))


def baseline_package(task_catalog: Path) -> CandidatePackage:
    source = yaml.safe_load(task_catalog.read_text(encoding="utf-8"))
    if source.get("version") != 1 or tuple(source.get("tasks", {})) != TASK_ORDER:
        raise ValueError("accepted task catalog structure is incompatible")
    prompts: dict[str, PromptValue] = {}
    contracts: dict[str, TaskContract] = {}
    for task in TASK_ORDER:
        item = source["tasks"][task]
        prompts[task] = prompt_value(item["system_prompt"])
        immutable = {key: value for key, value in item.items() if key != "system_prompt"}
        contracts[task] = TaskContract(
            task=task,
            task_version=str(item["version"]),
            input_selector=item["input_selector"],
            output_schema=item["output_schema"],
            finalizer_version=FINALIZER_VERSIONS[task],
            user_prompt_sha256=digest(item["user_prompt"]),
            generation_sha256=digest(item["generation"]),
            immutable_sha256=digest(immutable),
        )
    payload: dict[str, Any] = {
        "format_version": 3,
        "prompts": {key: value.model_dump(mode="json") for key, value in prompts.items()},
        "contracts": {key: value.model_dump(mode="json") for key, value in contracts.items()},
        "demonstrations": {task: [] for task in TASK_ORDER},
        "lineage": CandidateLineage(optimizer="p0").model_dump(mode="json"),
        "context_window": 8192,
    }
    return CandidatePackage(candidate_id=candidate_identity(payload), **payload)


def mutate_package(
    parent: CandidatePackage,
    prompts: dict[str, str],
    *,
    optimizer: Literal["bootstrap-few-shot", "gepa"],
    proposer_id: str | None,
    mutation_ordinal: int,
    strategy: str = "instruction-only",
    demonstrations: dict[str, list[CandidateDemonstration]] | None = None,
) -> CandidatePackage:
    if tuple(prompts) != TASK_ORDER:
        raise ValueError("mutation must provide exactly four prompts in fixed order")
    payload = {
        "format_version": 3,
        "prompts": {
            task: prompt_value(prompts[task]).model_dump(mode="json") for task in TASK_ORDER
        },
        "contracts": {task: parent.contracts[task].model_dump(mode="json") for task in TASK_ORDER},
        "demonstrations": {
            task: [item.model_dump(mode="json") for item in (demonstrations or {}).get(task, [])]
            for task in TASK_ORDER
        },
        "lineage": CandidateLineage(
            parent_id=parent.candidate_id,
            optimizer=optimizer,
            proposer_id=proposer_id,
            mutation_ordinal=mutation_ordinal,
            strategy=strategy,
        ).model_dump(mode="json"),
        "context_window": 8192,
    }
    return CandidatePackage(candidate_id=candidate_identity(payload), **payload)


def _write_immutable(path: Path, value: StrictModel, model: type[StrictModel]) -> None:
    if path.suffix.casefold() != ".json":
        raise ValueError("optimizer artifacts must use safe JSON serialization")
    if path.exists():
        existing = model.model_validate_json(path.read_text(encoding="utf-8"))
        if existing != value:
            raise ValueError("optimizer artifact is append-only and already exists")
        return
    atomic_json(path, value.model_dump(mode="json"))


def write_package(path: Path, package: CandidatePackage) -> None:
    _write_immutable(path, package, CandidatePackage)


def read_package(path: Path) -> CandidatePackage:
    if path.suffix.casefold() != ".json":
        raise ValueError("unsafe candidate package serialization")
    return CandidatePackage.model_validate_json(path.read_text(encoding="utf-8"))


def write_result(path: Path, result: CandidateResult) -> None:
    _write_immutable(path, result, CandidateResult)


def read_result(path: Path) -> CandidateResult:
    if path.suffix.casefold() != ".json":
        raise ValueError("unsafe candidate result serialization")
    return CandidateResult.model_validate_json(path.read_text(encoding="utf-8"))
