"""Canonical candidate requests and conservative complete-context envelopes."""

from __future__ import annotations

import json
from typing import Any

from bench.core import _schema_spec
from bench.models import TASK_ORDER
from chat_chronicle.ai_config import interpolate_prompt

from .authority import VerifiedAuthority
from .package import CandidatePackage, RequestEnvelopeEvidence

ESTIMATOR_VERSION = "complete-request-envelope-v1"
WRAPPER_ALLOWANCE_TOKENS = 64


def case_request_parts(
    candidate: CandidatePackage,
    task_name: str,
    task: Any,
    source: Any,
) -> tuple[list[dict[str, str]], dict[str, Any], Any]:
    """Build the exact message/schema surface used by the production adapter."""
    selector = source.recent if task_name == "last-activity" else source.overview
    values = {
        "conversation_id": str(source.source_conversation_id),
        "provider": source.provider,
        "title": source.source_title,
        "start_date": source.start_date,
        "last_active_date": source.last_active_date,
        "transcript": selector.transcript,
    }
    messages = [
        {
            "role": "system",
            "content": interpolate_prompt(candidate.prompts[task_name].text, values),
        }
    ]
    for demonstration in candidate.demonstrations[task_name]:
        messages.extend(
            (
                {"role": "user", "content": demonstration.selected_input},
                {"role": "assistant", "content": demonstration.response_json},
            )
        )
    messages.append({"role": "user", "content": interpolate_prompt(task.user_prompt, values)})
    schema = _schema_spec(task.output_schema).provider_model.model_json_schema()
    evidence = schema.get("properties", {}).get("evidence_message_ids", {})
    if selector.selected_message_ids and isinstance(evidence, dict):
        evidence.setdefault("items", {"type": "integer"})["enum"] = selector.selected_message_ids
    return messages, schema, selector


def estimate_request_envelope(
    candidate: CandidatePackage,
    tasks: Any,
    authority: VerifiedAuthority,
) -> RequestEnvelopeEvidence:
    maximum: tuple[int, int, int, str, str] | None = None
    for source in authority.inputs:
        for task_name in TASK_ORDER:
            task = tasks.tasks[task_name]
            messages, schema, _ = case_request_parts(candidate, task_name, task, source)
            input_tokens = estimate_case_input_tokens(messages, schema)
            output_tokens = task.generation.max_tokens
            total = input_tokens + output_tokens
            alias = f"c{source.selection_index:03d}--{task_name}"
            candidate_value = (total, input_tokens, output_tokens, alias, task_name)
            if maximum is None or candidate_value > maximum:
                maximum = candidate_value
    if maximum is None:
        raise ValueError("complete request envelope has no development cases")
    total, input_tokens, output_tokens, alias, task_name = maximum
    return RequestEnvelopeEvidence(
        estimator_version=ESTIMATOR_VERSION,
        context_window=8192,
        max_case_alias=alias,
        max_task=task_name,
        input_tokens=input_tokens,
        output_allowance_tokens=output_tokens,
        total_tokens=total,
        fits_context=total <= 8192,
    )


def estimate_case_input_tokens(
    messages: list[dict[str, str]], response_schema: dict[str, Any]
) -> int:
    """Conservatively estimate the complete provider request before a live call."""
    serialized = json.dumps(
        {
            "messages": messages,
            "response_schema": response_schema,
            "enforce_schema": True,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return _conservative_tokens(serialized) + WRAPPER_ALLOWANCE_TOKENS


def verify_demonstration_authority(
    candidate: CandidatePackage,
    tasks: Any,
    authority: VerifiedAuthority,
) -> None:
    """Revalidate packaged demonstrations without invoking any model or credential path."""
    inputs = {source.selection_index: source for source in authority.inputs}
    for task_name, demonstrations in candidate.demonstrations.items():
        task = tasks.tasks[task_name]
        for demonstration in demonstrations:
            index = int(demonstration.case_alias[1:4])
            if index not in inputs or demonstration.case_alias not in authority.references:
                raise ValueError("BootstrapFewShot demonstration case is outside authority")
            source = inputs[index]
            messages, _, selector = case_request_parts(candidate, task_name, task, source)
            if demonstration.selected_input != messages[-1]["content"]:
                raise ValueError("BootstrapFewShot demonstration input authority mismatch")
            try:
                parsed = json.loads(demonstration.response_json)
                final = (
                    _schema_spec(task.output_schema)
                    .final_model.model_validate(parsed)
                    .model_dump(mode="json")
                )
            except Exception as exc:
                raise ValueError(
                    "BootstrapFewShot demonstration output failed task authority"
                ) from exc
            if not set(final.get("evidence_message_ids", [])) <= set(selector.selected_message_ids):
                raise ValueError("BootstrapFewShot demonstration evidence authority mismatch")
            if task_name == "conversation-summary" and (
                final["start_date"] != source.start_date
                or final["last_active_date"] != source.last_active_date
            ):
                raise ValueError("BootstrapFewShot demonstration date authority mismatch")
            reference = authority.references[demonstration.case_alias].output
            if demonstration.kind == "labeled" and final != reference:
                raise ValueError("BootstrapFewShot labeled demonstration differs from reference")


def _conservative_tokens(value: str) -> int:
    """Use a documented byte/3 upper estimate when provider tokenizers are unavailable."""
    return (len(value.encode("utf-8")) + 2) // 3
