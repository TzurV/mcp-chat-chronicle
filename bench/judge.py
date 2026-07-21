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
    _attempts,
    _open_package,
    build_authority,
    utc_now,
    validate_reference_authority,
    verify,
)
from .io import atomic_json, digest
from .loaders import load_inputs, load_references
from .models import EvaluationConfig, JudgeResult
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


def _response_schema() -> dict[str, Any]:
    return JudgeResult.model_json_schema()


async def score_with_judge(
    package_path: Path,
    config: EvaluationConfig,
    config_path: Path,
    *,
    client: LLMClient | None = None,
    retry_failures: bool = False,
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
            path.parent.name: _attempts(path.parent)[0]
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
                response_schema=_response_schema(),
                enforce_schema=True,
                temperature=config.judge.temperature,
                max_tokens=config.judge.max_tokens,
                timeout=profile.timeout,
                retries=profile.retries,
                api_base=profile.api_base,
                api_key=resolved.get("api_key"),
                context_window=profile.context_window,
            )
            started = utc_now()
            clock = time.monotonic()
            try:
                response = await client.complete(request)
                result = JudgeResult.model_validate_json(response.content)
                if (
                    result.case_alias != case.alias
                    or result.case_fingerprint != case.fingerprint
                    or result.task != case.task
                    or set(result.scores) != set(RUBRICS[case.task])
                    or not set(result.evidence_message_ids)
                    <= set(case.selected["selected_message_ids"])
                ):
                    raise JudgeContractError("judge result identity, rubric, or evidence mismatch")
                record = {
                    **result.model_dump(mode="json"),
                    "judge_profile": config.judge.profile,
                    "resolved_model": resolved["model"],
                    "rubric_version": config.judge.rubric_version,
                    "started_at": started,
                    "completed_at": utc_now(),
                    "latency_ms": int((time.monotonic() - clock) * 1000),
                    "usage": response.usage,
                    "failure_category": None,
                    "cache_identity": identity,
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
        aggregate_path = output_root / "reports" / "aggregate.json"
        aggregate = (
            json.loads(aggregate_path.read_text(encoding="utf-8"))
            if aggregate_path.exists()
            else {}
        )
        aggregate["judge_semantic"] = metrics
        atomic_json(aggregate_path, aggregate)
        markdown_path = output_root / "reports" / "aggregate.md"
        existing_markdown = (
            markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else ""
        )
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(
            existing_markdown
            + "\n## Judge coverage\n\n"
            + f"Eligible: {metrics['eligible']}  \nCompleted: {metrics['completed']}  \n"
            + f"Failed: {metrics['failed']}  \nSkipped invalid: {metrics['skipped_invalid']}\n",
            encoding="utf-8",
        )
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
