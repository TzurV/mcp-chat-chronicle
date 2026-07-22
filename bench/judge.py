"""Task-specific, blinded, resumable semantic judging."""

from __future__ import annotations

import json
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from chat_chronicle.ai import CompletionRequest, LiteLLMClient, LLMClient, LLMError
from chat_chronicle.ai_config import load_model_catalog, resolve_model

from .config import _relative
from .core import (
    _authoritative_attempt,
    _open_package,
    build_authority,
    utc_now,
    validate_reference_authority,
    verify,
    write_aggregate_reports,
)
from .io import atomic_json, digest
from .loaders import load_inputs, load_references
from .models import JUDGE_RATIONALE_MAX_LENGTH, EvaluationConfig, JudgeResult
from .paths import resolve_member

RUBRICS: dict[str, tuple[str, ...]] = {
    "conversation-summary": (
        "factual_consistency",
        "material_coverage",
        "unsupported_claim_avoidance",
        "concise_usefulness",
        "conversation_characterization",
    ),
    "work-mode-classification": (
        "label_support",
        "mode_distinction",
        "reason_specificity",
        "unsupported_claim_avoidance",
    ),
    "last-activity": (
        "final_meaningful_activity",
        "status_correctness",
        "blocker_correctness",
        "next_action_support",
        "not_source_copying",
        "unsupported_claim_avoidance",
    ),
    "title-assessment": (
        "title_fits_correctness",
        "dominant_activity_fit",
        "suggestion_usefulness",
        "unsupported_claim_avoidance",
        "suggestion_only_compliance",
    ),
}

PROVIDER_JUDGE_SCHEMA_NAME = "chronicle-judge-provider"
PROVIDER_JUDGE_SCHEMA_VERSION = "3"
APPLICATION_JUDGE_SCHEMA_NAME = "JudgeResult"
APPLICATION_JUDGE_SCHEMA_VERSION = "1"
JUDGE_RESPONSE_NORMALIZER_VERSION = "1"
JUDGE_REQUEST_CONSTRUCTION_VERSION = "2"


class JudgeContractError(ValueError):
    """A known judge response identity or evidence contract failure."""


_PROVIDER_FAILURE_CATEGORIES = {
    "authentication",
    "connection",
    "context_length",
    "dependency",
    "invalid_json",
    "model_not_found",
    "provider_response",
    "provider_route",
    "rate_limit",
    "timeout",
}


def rubric(task: str, version: str = "1") -> dict[str, Any]:
    return {
        "version": version,
        "dimensions": list(RUBRICS[task]),
        "scale": {
            "0": "incorrect or unsupported",
            "1": "major deficiencies",
            "2": "partially supported",
            "3": "well supported with minor issues",
            "4": "fully supported and useful",
        },
        "instruction": (
            "Score against source and rubric. The reference is interpretation context, not wording "
            "ground truth. Give a concise verdict, not chain-of-thought."
        ),
    }


def provider_judge_schema(task: str) -> dict[str, Any]:
    """Return the small Vertex-compatible contract used for controlled generation."""
    dimensions = RUBRICS[task]
    properties: dict[str, Any] = {
        "case_alias": {"type": "string"},
        "case_fingerprint": {"type": "string"},
        "task": {"type": "string"},
        "status": {"type": "string", "enum": ["success"]},
        "scores": {
            "type": "object",
            "properties": {
                name: {"type": "integer", "minimum": 0, "maximum": 4}
                for name in dimensions
            },
            "required": list(dimensions),
            "additionalProperties": False,
        },
        "rationale": {
            "type": "string",
            "maxLength": JUDGE_RATIONALE_MAX_LENGTH,
            "description": (
                "Give a concise verdict with no chain-of-thought; remain within "
                f"{JUDGE_RATIONALE_MAX_LENGTH} characters."
            ),
        },
        "evidence_message_ids": {"type": "array", "items": {"type": "integer"}},
        "unsupported_claim_count": {"type": "integer", "minimum": 0},
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _safe_validation_diagnostics(exc: ValidationError) -> list[dict[str, str]]:
    """Keep only bounded field/category facts; never retain provider values."""
    return [
        {
            "field": ".".join(str(part) for part in error.get("loc", ())) or "response",
            "category": str(error.get("type", "invalid")),
        }
        for error in exc.errors(include_url=False, include_context=False, include_input=False)[:8]
    ]


def _contract_diagnostic(category: str, field: str) -> list[dict[str, str]]:
    return [{"field": field, "category": category}]


_USAGE_COUNTERS = {
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "reasoning_tokens",
    "thoughts_token_count",
    "cached_tokens",
}


def _safe_usage(usage: dict[str, Any] | None) -> dict[str, int]:
    """Extract only numeric counters, including nested reasoning-token details."""
    safe: dict[str, int] = {}

    def visit(value: Any) -> None:
        if not isinstance(value, dict):
            return
        for key, child in value.items():
            if key in _USAGE_COUNTERS and isinstance(child, int) and child >= 0:
                safe[key] = child
            elif isinstance(child, dict):
                visit(child)

    visit(usage)
    return dict(sorted(safe.items()))


async def score_with_judge(
    package_path: Path,
    config: EvaluationConfig,
    config_path: Path,
    *,
    client: LLMClient | None = None,
    retry_failures: bool = False,
    cache_only: bool = False,
) -> dict[str, Any]:
    if not config.judge.enabled:
        raise ValueError("judge is disabled in evaluation configuration")
    client = client or LiteLLMClient()
    models = load_model_catalog(_relative(config_path, config.model_catalog))
    profile = models.profiles[config.judge.profile]
    resolved = resolve_model(profile)  # Credential preflight occurs before private reads/prompts.
    output_root = resolve_member(config, config_path, config.paths.scoring, output=True)
    judge_root = output_root / "judge"
    attempts_root = judge_root / "attempts"
    attempts_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        package = _open_package(package_path, Path(temporary), candidate=True)
        verification = verify(package, config, config_path)
        limit = verification["scope"]["effective_conversation_count"]
        authority = build_authority(config, config_path, limit)
        inputs = load_inputs(
            resolve_member(config, config_path, config.paths.source, output=False),
            config.expected_conversations,
        )
        references = load_references(
            resolve_member(config, config_path, config.paths.references, output=False), inputs
        )
        validate_reference_authority(authority, inputs, references)
        baselines = {
            path.parent.name: _authoritative_attempt(path.parent)
            for path in package.glob("results/*/index.json")
        }
        records: list[dict[str, Any]] = []
        judge_baselines: list[dict[str, Any]] = []
        for case in authority:
            candidate = baselines[case.alias]
            if candidate.status != "success":
                records.append(
                    {"alias": case.alias, "task": case.task, "status": "skipped_invalid"}
                )
                continue
            reference = references[case.alias]
            rubric_value = rubric(case.task, config.judge.rubric_version)
            provider_schema = provider_judge_schema(case.task)
            application_schema = JudgeResult.model_json_schema()
            judge_contract = {
                "provider_schema_name": PROVIDER_JUDGE_SCHEMA_NAME,
                "provider_schema_version": PROVIDER_JUDGE_SCHEMA_VERSION,
                "provider_schema_hash": digest(provider_schema),
                "application_schema_name": APPLICATION_JUDGE_SCHEMA_NAME,
                "application_schema_version": APPLICATION_JUDGE_SCHEMA_VERSION,
                "application_schema_hash": digest(application_schema),
                "response_normalizer_version": JUDGE_RESPONSE_NORMALIZER_VERSION,
                "request_construction_version": JUDGE_REQUEST_CONSTRUCTION_VERSION,
                "rubric_dimension_identity": digest(list(RUBRICS[case.task])),
            }
            identity = digest(
                {
                    "candidate": digest(candidate.result),
                    "source": case.contract_hashes["input"],
                    "reference": digest(reference.output),
                    "rubric": rubric_value,
                    "profile": config.judge.profile,
                    "resolved_model": resolved["model"],
                    "profile_config": {
                        key: value for key, value in resolved.items() if key != "api_key"
                    },
                    "generation": config.judge.model_dump(mode="json"),
                    "judge_contract": judge_contract,
                }
            )
            case_cache = attempts_root / case.alias / identity
            existing = sorted(case_cache.glob("*.json")) if case_cache.exists() else []
            existing_records = [json.loads(path.read_text(encoding="utf-8")) for path in existing]
            if existing_records:
                judge_baselines.append(existing_records[0])
            if existing_records and (
                existing_records[-1].get("status") != "failed" or not retry_failures
            ):
                records.append(existing_records[-1])
                continue
            if cache_only:
                raise ValueError("judge cache miss in cache-only mode")
            case_cache.mkdir(parents=True, exist_ok=True)
            prompt = {
                "case_alias": case.alias,
                "case_fingerprint": case.fingerprint,
                "task": case.task,
                "selected_source": case.selected["transcript"],
                "allowed_evidence_message_ids": case.selected["selected_message_ids"],
                "reference": reference.output,
                "candidate": candidate.result,
                "rubric": rubric_value,
            }
            request = CompletionRequest(
                model=resolved["model"],
                messages=[
                    {"role": "system", "content": "Return only the requested structured verdict."},
                    {
                        "role": "user",
                        "content": json.dumps(prompt, ensure_ascii=False, sort_keys=True),
                    },
                ],
                response_schema=provider_schema,
                enforce_schema=True,
                temperature=config.judge.temperature,
                max_tokens=config.judge.max_tokens,
                timeout=profile.timeout,
                retries=profile.retries,
                api_base=profile.api_base,
                api_key=resolved.get("api_key"),
                context_window=profile.context_window,
                reasoning_effort=profile.reasoning_effort,
            )
            started = utc_now()
            clock = time.monotonic()
            response = None
            try:
                response = await client.complete(request)
                try:
                    parsed = json.loads(response.content)
                except json.JSONDecodeError as exc:
                    raise LLMError("invalid_json", "Provider returned invalid JSON.") from exc
                result = JudgeResult.model_validate(parsed)
                contract_diagnostics: list[dict[str, str]] = []
                if result.case_alias != case.alias:
                    contract_diagnostics += _contract_diagnostic("identity_mismatch", "case_alias")
                if result.case_fingerprint != case.fingerprint:
                    contract_diagnostics += _contract_diagnostic(
                        "identity_mismatch", "case_fingerprint"
                    )
                if result.task != case.task:
                    contract_diagnostics += _contract_diagnostic("identity_mismatch", "task")
                missing = set(RUBRICS[case.task]) - set(result.scores)
                extra = set(result.scores) - set(RUBRICS[case.task])
                if missing:
                    contract_diagnostics += _contract_diagnostic("missing_dimension", "scores")
                if extra:
                    contract_diagnostics += _contract_diagnostic("extra_dimension", "scores")
                if not set(result.evidence_message_ids) <= set(
                    case.selected["selected_message_ids"]
                ):
                    contract_diagnostics += _contract_diagnostic(
                        "membership_failure", "evidence_message_ids"
                    )
                if contract_diagnostics:
                    contract_error = JudgeContractError("judge output contract mismatch")
                    contract_error.diagnostics = contract_diagnostics  # type: ignore[attr-defined]
                    raise contract_error
                record = {
                    **result.model_dump(mode="json"),
                    "judge_profile": config.judge.profile,
                    "resolved_model": resolved["model"],
                    "rubric_version": config.judge.rubric_version,
                    "started_at": started,
                    "completed_at": utc_now(),
                    "latency_ms": int((time.monotonic() - clock) * 1000),
                    "usage": _safe_usage(response.usage),
                    "finish_reason": response.finish_reason,
                    "failure_category": None,
                    "cache_identity": identity,
                    "judge_contract": judge_contract,
                    "reasoning_effort": profile.reasoning_effort,
                }
            except (LLMError, ValidationError, JudgeContractError) as exc:
                # Do not persist exception text: providers may echo disclosed private content.
                category = (
                    (
                        f"provider_{exc.kind}"
                        if exc.kind in _PROVIDER_FAILURE_CATEGORIES
                        else "provider_failure"
                    )
                    if isinstance(exc, LLMError)
                    else "output_schema"
                    if isinstance(exc, ValidationError)
                    else "output_contract"
                )
                record = {
                    "alias": case.alias,
                    "task": case.task,
                    "status": "failed",
                    "failure_category": category,
                    "started_at": started,
                    "completed_at": utc_now(),
                    "latency_ms": int((time.monotonic() - clock) * 1000),
                    "cache_identity": identity,
                    "diagnostics": (
                        _safe_validation_diagnostics(exc)
                        if isinstance(exc, ValidationError)
                        else getattr(exc, "diagnostics", [])
                    ),
                    "judge_contract": judge_contract,
                    "reasoning_effort": profile.reasoning_effort,
                    "response_metadata": {
                        "finish_reason": response.finish_reason if response else "unknown",
                        "response_present": bool(response and response.content),
                        "response_characters": len(response.content) if response else 0,
                        "usage": _safe_usage(response.usage if response else None),
                    },
                }
            ordinal = len(existing_records) + 1
            atomic_json(case_cache / f"{ordinal:04d}.json", record)
            if not existing_records:
                judge_baselines.append(record)
            records.append(record)
        (judge_root / "case-scores.jsonl").write_text(
            "".join(json.dumps(item, sort_keys=True) + "\n" for item in records),
            encoding="utf-8",
        )
        completed = [
            item for item in records if item.get("status") not in {"failed", "skipped_invalid"}
        ]
        metrics = {
            "scope": verification["scope"],
            "eligible": sum(item.status == "success" for item in baselines.values()),
            "completed": len(completed),
            "failed": sum(item.get("status") == "failed" for item in records),
            "skipped_invalid": sum(item.get("status") == "skipped_invalid" for item in records),
            "failure_categories": dict(
                Counter(
                    item.get("failure_category") for item in records if item.get("failure_category")
                )
            ),
            "dimension_means": _dimension_means(completed),
            "baseline_attempts": _attempt_accounting(judge_baselines),
            "current_attempts": _attempt_accounting(
                [item for item in records if item.get("status") != "skipped_invalid"]
            ),
            "total_attempts": sum(1 for _ in attempts_root.glob("*/*/*.json")),
        }
        atomic_json(judge_root / "metrics.json", metrics)
        deterministic_metrics = json.loads(
            (output_root / "deterministic" / "metrics.json").read_text(encoding="utf-8")
        )
        write_aggregate_reports(output_root, deterministic_metrics, metrics)
        run_manifest_path = output_root / "run-manifest.json"
        run_manifest = (
            json.loads(run_manifest_path.read_text(encoding="utf-8"))
            if run_manifest_path.exists()
            else {"version": 1}
        )
        run_manifest.update(
            deterministic_only=False,
            judge_profile=config.judge.profile,
            rubric_version=config.judge.rubric_version,
            updated_at_utc=utc_now(),
        )
        atomic_json(run_manifest_path, run_manifest)
        return metrics


def _dimension_means(records: list[dict[str, Any]]) -> dict[str, float]:
    values: dict[str, list[int]] = {}
    for record in records:
        for name, score in record.get("scores", {}).items():
            values.setdefault(name, []).append(score)
    return {name: sum(scores) / len(scores) for name, scores in sorted(values.items())}


def _attempt_accounting(records: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "completed": sum(item.get("status") != "failed" for item in records),
        "failed": sum(item.get("status") == "failed" for item in records),
    }
