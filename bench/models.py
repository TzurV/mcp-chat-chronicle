"""Strict, portable contracts for Chronicle development evaluation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TASK_ORDER = (
    "conversation-summary",
    "work-mode-classification",
    "last-activity",
    "title-assessment",
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Paths(StrictModel):
    root: str
    source: str
    references: str
    bundle: str
    generation_work: str
    candidate_package: str
    scoring: str


class Candidate(StrictModel):
    id: str
    profile: str
    artifact_sha256: str
    artifact_file: str
    quantization: str = "Q4_K_M"
    runtime: str = "LM Studio"
    artifact_repository: str = "unknown"
    artifact_size: int = Field(default=0, ge=0)
    runtime_version: str = "unknown"
    execution_device: str = "unknown"
    advertised_context: int | None = Field(default=None, gt=0)
    application_commit: str = "unknown"
    artifact_path: str | None = Field(default=None, exclude=True)
    expected_provider: str
    expected_model: str
    allow_dirty_tracked: bool = False
    tracked_diff_sha256: str | None = None

    @model_validator(mode="after")
    def dirty_policy(self) -> Candidate:
        if self.allow_dirty_tracked != (self.tracked_diff_sha256 is not None):
            raise ValueError("allow_dirty_tracked requires exactly one pinned tracked_diff_sha256")
        return self


class Judge(StrictModel):
    enabled: bool = False
    profile: str
    rubric_version: str = "1"
    temperature: float = Field(default=0, ge=0, le=2)
    max_tokens: int = Field(default=500, gt=0)


class EvaluationConfig(StrictModel):
    version: Literal[1] = 1
    corpus_id: str
    expected_conversations: int = Field(default=30, gt=0)
    expected_cases: int = Field(default=120, gt=0)
    tasks: list[str] = Field(default_factory=lambda: list(TASK_ORDER))
    task_catalog: str = "ai-tasks.default.yaml"
    model_catalog: str = "ai-models.default.yaml"
    paths: Paths
    candidate: Candidate
    judge: Judge

    @model_validator(mode="after")
    def accounting(self) -> EvaluationConfig:
        if tuple(self.tasks) != TASK_ORDER:
            raise ValueError("tasks must be the four accepted tasks in fixed order")
        if self.expected_cases != self.expected_conversations * len(TASK_ORDER):
            raise ValueError("expected_cases must equal expected_conversations x four tasks")
        return self


class BundleCase(StrictModel):
    alias: str
    fingerprint: str
    task: str
    task_version: str
    schema_name: str
    schema_version: str
    selector: str
    selector_version: str
    messages: list[dict[str, str]]
    response_schema: dict[str, Any]
    selected: dict[str, Any]
    generation: dict[str, Any]
    contract_hashes: dict[str, str]


class Attempt(StrictModel):
    version: Literal[1] = 1
    alias: str
    case_fingerprint: str
    attempt_id: str
    status: Literal["success", "failed"]
    failure_boundary: str | None = None
    result: dict[str, Any] | None = None
    raw_invalid_file: str | None = None
    provider: str | None = None
    model: str | None = None
    latency_ms: int
    usage: dict[str, Any] | None = None
    started_at: str
    completed_at: str


class SelectorEnvelope(StrictModel):
    selector: str
    selector_version: str
    canonical_input_hash: str
    transcript: str
    selected_message_ids: list[int]
    selection_metadata: dict[str, Any]


class InputEnvelope(StrictModel):
    format_version: int
    corpus_version: str
    case_group_id: str
    selection_index: int = Field(gt=0)
    source_conversation_id: int
    provider: str
    source_content_hash: str
    source_title: str
    start_date: str
    last_active_date: str
    overview: SelectorEnvelope
    recent: SelectorEnvelope
    created_at_utc: str
    snapshot_hash_reference: str
    task_catalog_hash_reference: str


class ReferenceEnvelope(StrictModel):
    format_version: int
    corpus_version: str
    run_id: str
    case_id: str
    case_group_id: str
    source_conversation_id: int
    provider: str
    task_name: str
    task_version: str
    output_schema: str
    provider_schema_version: str
    finalizer_version: str
    input_selector: str
    selector_version: str
    input_hash: str
    task_catalog_hash: str
    teacher_alias: str
    teacher_model: str
    teacher_session_id: str
    status: str
    output: dict[str, Any]
    failure: dict[str, Any] | str | None
    created_at_utc: str
    validated_at_utc: str


class JudgeResult(StrictModel):
    case_alias: str
    case_fingerprint: str
    task: str
    status: Literal["success"]
    scores: dict[str, int]
    rationale: str = Field(min_length=1, max_length=500)
    evidence_message_ids: list[int] = Field(default_factory=list)
    unsupported_claim_count: int = Field(default=0, ge=0)

    @field_validator("scores")
    @classmethod
    def anchored_scores(cls, value: dict[str, int]) -> dict[str, int]:
        if not value or any(score < 0 or score > 4 for score in value.values()):
            raise ValueError("judge scores must use the anchored 0-4 scale")
        return value


class ConversationScope(StrictModel):
    selection: Literal["frozen-prefix-v1"] = "frozen-prefix-v1"
    requested_conversation_limit: int | None = Field(default=None, gt=0)
    effective_conversation_count: int = Field(gt=0)
    case_count: int = Field(gt=0)
    frozen_prefix_identity: str

    @model_validator(mode="after")
    def accounting(self) -> ConversationScope:
        if self.case_count != self.effective_conversation_count * len(TASK_ORDER):
            raise ValueError("scope case count must equal conversations x four tasks")
        if (
            self.requested_conversation_limit is not None
            and self.requested_conversation_limit != self.effective_conversation_count
        ):
            raise ValueError("requested and effective conversation scope differ")
        return self
