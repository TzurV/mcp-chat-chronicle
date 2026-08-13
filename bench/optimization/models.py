"""Strict configuration and artifact contracts for prompt optimization."""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePath
from typing import Any, Literal

import yaml
from pydantic import Field, StrictInt, field_validator, model_validator

from bench.models import TASK_ORDER, StrictModel

OPTIMIZER_SPLIT_SEED = "wp-5.2b3b.1-optimizer-split-v1"
MUTABLE_FIELDS = tuple(f"tasks.{task}.system_prompt" for task in TASK_ORDER)


class VersionPins(StrictModel):
    dspy: Literal["3.3.0"] = "3.3.0"
    gepa: Literal["0.1.1"] = "0.1.1"
    gepa_result_schema: Literal["dspy-gepa-result-v0.1.1"] = "dspy-gepa-result-v0.1.1"


class ManifestBinding(StrictModel):
    path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    role: Literal["optimizer-train", "optimizer-validation"]
    conversations: Literal[4, 6]
    cases: Literal[16, 24]

    @model_validator(mode="after")
    def accounting(self) -> ManifestBinding:
        if self.cases != self.conversations * len(TASK_ORDER):
            raise ValueError("optimizer manifest cases must equal conversations x four tasks")
        _forbid_holdout(self.path)
        return self


class CandidateModel(StrictModel):
    id: Literal["qwen", "phi"]
    profile: str = Field(min_length=1)
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifact_path: str = Field(min_length=1, exclude=True)
    expected_provider: str = Field(min_length=1)
    expected_model: str = Field(min_length=1)
    litellm_model: str = Field(min_length=1)
    api_base: str = Field(min_length=1)
    api_key_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    timeout_seconds: float = Field(default=120, gt=0, le=600)
    estimated_seconds_per_task: float = Field(default=30, gt=0, le=600)
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] = "none"
    context_window: Literal[8192] = 8192
    concurrency: Literal[1] = 1
    infrastructure_retries: StrictInt = Field(default=1, ge=0, le=1)
    semantic_retries: Literal[0] = 0

    @model_validator(mode="after")
    def no_holdout(self) -> CandidateModel:
        _forbid_holdout(self.artifact_path)
        return self


class ProposerProfile(StrictModel):
    id: str = Field(min_length=1)
    litellm_model: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    region: str = Field(min_length=1)
    credential_mode: Literal["api-key-environment", "vertex-adc"] = "api-key-environment"
    api_key_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    google_cloud_project_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    google_cloud_location_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    vertex_project_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    vertex_location_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    vertex_enable_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    resolved_location: Literal["global"] | None = None
    timeout_seconds: float = Field(default=120, gt=0, le=600)
    concurrency: Literal[1] = 1
    temperature: float = Field(default=0, ge=0, le=1)
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] = "none"
    infrastructure_retries: Literal[1] = 1
    semantic_retries: Literal[0] = 0
    output_repair: Literal[False] = False
    cache_namespace: str = Field(min_length=1)
    max_calls: StrictInt = Field(gt=0, le=250)
    per_call_input_tokens: StrictInt = Field(gt=0)
    per_call_output_tokens: StrictInt = Field(gt=0)
    max_input_tokens: StrictInt = Field(gt=0)
    max_output_tokens: StrictInt = Field(gt=0)
    input_usd_per_million: float = Field(ge=0)
    output_usd_per_million: float = Field(ge=0)
    max_cost_usd: float = Field(gt=0)
    disclosure: str = Field(min_length=1)

    @model_validator(mode="after")
    def token_envelope(self) -> ProposerProfile:
        if self.per_call_input_tokens * self.max_calls > self.max_input_tokens:
            raise ValueError("proposer per-call input reservation exceeds total token ceiling")
        if self.per_call_output_tokens * self.max_calls > self.max_output_tokens:
            raise ValueError("proposer per-call output reservation exceeds total token ceiling")
        calculated_cost = (
            self.max_input_tokens * self.input_usd_per_million
            + self.max_output_tokens * self.output_usd_per_million
        ) / 1_000_000
        if calculated_cost > self.max_cost_usd:
            raise ValueError("proposer token envelope exceeds hard cost ceiling")
        vertex_fields = (
            self.google_cloud_project_env,
            self.google_cloud_location_env,
            self.vertex_project_env,
            self.vertex_location_env,
            self.vertex_enable_env,
        )
        if self.credential_mode == "api-key-environment":
            if self.api_key_env is None:
                raise ValueError("api-key-environment proposer requires api_key_env")
            if any(value is not None for value in vertex_fields) or self.resolved_location:
                raise ValueError("api-key-environment proposer cannot contain Vertex ADC fields")
            return self
        if self.api_key_env is not None:
            raise ValueError("vertex-adc proposer cannot require an API key")
        if any(value is None for value in vertex_fields):
            raise ValueError("vertex-adc proposer requires project and location environment names")
        if self.provider != "Google Vertex AI" or not self.litellm_model.startswith("vertex_ai/"):
            raise ValueError("vertex-adc proposer requires a Google Vertex AI LiteLLM model")
        if self.region != "global" or self.resolved_location != "global":
            raise ValueError("vertex-adc proposer location must resolve to global")
        return self


class SearchBudget(StrictModel):
    pilot_candidates: StrictInt = Field(default=12, gt=0, le=12)
    total_candidates: StrictInt = Field(default=40, gt=0, le=40)
    task_invocations: StrictInt = Field(default=3000, gt=0, le=3000)
    pilot_compute_hours: float = Field(default=4, gt=0, le=4)
    total_compute_hours: float = Field(default=12, gt=0, le=12)
    compute_cost_usd: float = Field(gt=0)
    prompt_token_ceiling: StrictInt = Field(default=7000, gt=0, lt=8192)

    @model_validator(mode="after")
    def nested(self) -> SearchBudget:
        if self.pilot_candidates > self.total_candidates:
            raise ValueError("pilot candidate ceiling exceeds total ceiling")
        if self.pilot_compute_hours > self.total_compute_hours:
            raise ValueError("pilot time ceiling exceeds total ceiling")
        return self


class OptimizationPaths(StrictModel):
    development_manifest: str = Field(min_length=1)
    inputs: str = Field(min_length=1)
    references: str = Field(min_length=1)
    accepted_task_catalog: str = Field(min_length=1)
    run_root: str = Field(min_length=1)

    @model_validator(mode="after")
    def no_holdout(self) -> OptimizationPaths:
        for value in self.model_dump().values():
            _forbid_holdout(value)
        return self


class OptimizationConfig(StrictModel):
    version: Literal[1] = 1
    optimizer_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    application_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    seed: StrictInt
    split_seed: Literal[OPTIMIZER_SPLIT_SEED] = OPTIMIZER_SPLIT_SEED
    versions: VersionPins = Field(default_factory=VersionPins)
    tasks: list[str] = Field(default_factory=lambda: list(TASK_ORDER))
    mutable_fields: list[str] = Field(default_factory=lambda: list(MUTABLE_FIELDS))
    context_window: Literal[8192] = 8192
    accepted_task_catalog_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    development_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    train_manifest: ManifestBinding
    validation_manifest: ManifestBinding
    candidate_models: list[CandidateModel]
    proposer: ProposerProfile
    budget: SearchBudget
    paths: OptimizationPaths
    bootstrap_max_labeled_demos: Literal[1] = 1
    bootstrap_max_bootstrapped_demos: Literal[1] = 1
    bootstrap_max_rounds: Literal[1] = 1
    bootstrap_teacher: Literal["candidate-model"] = "candidate-model"
    gepa_track_stats: Literal[True] = True
    gepa_instruction_only: Literal[True] = True
    gepa_max_metric_calls_per_candidate: StrictInt = Field(default=20, gt=0, le=20)
    gepa_max_candidate_proposals: StrictInt | None = Field(default=None, gt=0, le=20)
    gepa_train_conversation_limit: StrictInt | None = Field(default=None, gt=0, le=6)
    gepa_validation_conversation_limit: StrictInt | None = Field(default=None, gt=0, le=4)

    @model_validator(mode="after")
    def fixed_contract(self) -> OptimizationConfig:
        if tuple(self.tasks) != TASK_ORDER:
            raise ValueError("optimizer tasks must be the four accepted tasks in fixed order")
        if tuple(self.mutable_fields) != MUTABLE_FIELDS:
            raise ValueError("optimizer mutation surface must contain only four system prompts")
        if [item.id for item in self.candidate_models] != ["qwen", "phi"]:
            raise ValueError("candidate models must be qwen then phi")
        if self.train_manifest.role != "optimizer-train" or self.train_manifest.conversations != 6:
            raise ValueError("train manifest must bind the frozen six-conversation split")
        if (
            self.validation_manifest.role != "optimizer-validation"
            or self.validation_manifest.conversations != 4
        ):
            raise ValueError("validation manifest must bind the frozen four-conversation split")
        if self.train_manifest.sha256 == self.validation_manifest.sha256:
            raise ValueError("train and validation manifests must be distinct")
        if self.run_id != self.optimizer_id:
            raise ValueError("run_id and optimizer_id must match")
        bounded = (
            self.gepa_train_conversation_limit,
            self.gepa_validation_conversation_limit,
        )
        if (bounded[0] is None) != (bounded[1] is None):
            raise ValueError("bounded GEPA scope requires train and validation limits together")
        return self


class TaskContract(StrictModel):
    task: str
    task_version: str
    input_selector: str
    output_schema: str
    finalizer_version: str
    user_prompt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    generation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    immutable_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class PromptValue(StrictModel):
    text: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    utf8_bytes: StrictInt = Field(gt=0)
    token_estimate: StrictInt = Field(gt=0)

    @field_validator("sha256")
    @classmethod
    def matches_text(cls, value: str, info: Any) -> str:
        text = info.data.get("text")
        if text is not None and hashlib.sha256(text.encode()).hexdigest() != value:
            raise ValueError("prompt hash mismatch")
        return value


def _forbid_holdout(value: str) -> None:
    parts = [part.casefold() for part in PurePath(value.replace("\\", "/")).parts]
    if any("holdout" in part for part in parts):
        raise ValueError("holdout paths and identities are forbidden in optimizer configuration")


def resolve_config_path(config_path: Path, value: str) -> Path:
    _forbid_holdout(value)
    path = Path(value)
    return path.resolve() if path.is_absolute() else (config_path.parent / path).resolve()


def load_optimization_config(path: Path) -> OptimizationConfig:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return OptimizationConfig.model_validate(value)


def optimization_config_identity(config: OptimizationConfig) -> str:
    from bench.io import digest

    return digest(config.model_dump(mode="json"))


def proposer_identity(proposer: ProposerProfile) -> str:
    """Bind only the tracked, non-secret proposer contract."""
    from bench.io import digest

    return digest(proposer.model_dump(mode="json"))


def proposer_cache_identity(proposer: ProposerProfile) -> str:
    """Namespace proposer caches by the full non-secret runtime contract."""
    from bench.io import digest

    return digest(
        {
            "cache_namespace": proposer.cache_namespace,
            "proposer_identity_sha256": proposer_identity(proposer),
        }
    )
