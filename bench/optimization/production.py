"""Tracked DSPy/LiteLLM adapters used by the provider-facing optimizer CLI."""

from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Literal

from bench.core import _schema_spec
from bench.models import TASK_ORDER
from chat_chronicle.ai import CompletionRequest, LiteLLMClient, LLMError
from chat_chronicle.ai_config import interpolate_prompt, load_task_catalog

from .authority import VerifiedAuthority
from .dspy_bridge import (
    build_program,
    compile_bootstrap,
    compile_gepa,
    demonstrations_from_program,
    prompts_from_program,
    proposer_lm,
)
from .execution import (
    AdapterReservation,
    AdapterUsage,
    CandidateAdapter,
    CaseOutcome,
    EvaluationBatch,
    ExecutionAdapters,
    OptimizerAdapter,
    Proposal,
)
from .feedback import Diagnostic, render_feedback
from .models import OptimizationConfig, resolve_config_path
from .package import CandidatePackage
from .request_envelope import case_request_parts, verify_demonstration_authority


class LiteLLMCandidateAdapter(CandidateAdapter):
    def __init__(
        self,
        config: OptimizationConfig,
        config_path: Path,
        client: LiteLLMClient | None = None,
    ) -> None:
        self.config = config
        self.tasks = load_task_catalog(
            resolve_config_path(config_path, config.paths.accepted_task_catalog)
        )
        self.client = client or LiteLLMClient()

    def reservation(
        self, scope: Literal["train", "validation"], model_id: Literal["qwen", "phi"]
    ) -> AdapterReservation:
        conversations = 6 if scope == "train" else 4
        model = _model(self.config, model_id)
        cases = conversations * len(TASK_ORDER)
        attempts = cases * (1 + model.infrastructure_retries)
        hours = attempts * model.estimated_seconds_per_task / 3600
        return AdapterReservation(
            task_calls=attempts,
            retries=cases * model.infrastructure_retries,
            compute_hours=hours,
            compute_cost_usd=hours * _compute_hourly_cost(self.config),
        )

    def evaluate(
        self,
        candidate: CandidatePackage,
        scope: Literal["train", "validation"],
        model_id: Literal["qwen", "phi"],
        authority: VerifiedAuthority,
    ) -> EvaluationBatch:
        return asyncio.run(self._evaluate(candidate, scope, model_id, authority))

    async def _evaluate(
        self,
        candidate: CandidatePackage,
        scope: Literal["train", "validation"],
        model_id: Literal["qwen", "phi"],
        authority: VerifiedAuthority,
    ) -> EvaluationBatch:
        manifest = authority.train if scope == "train" else authority.validation
        inputs = {source.selection_index: source for source in authority.inputs}
        model = _model(self.config, model_id)
        outcomes: list[CaseOutcome] = []
        attempts = retries = input_tokens = output_tokens = 0
        started = time.monotonic()
        for entry in manifest.ordered_conversations:
            source = inputs[entry.authority_index]
            for task_name in TASK_ORDER:
                task = self.tasks.tasks[task_name]
                messages, schema, selector = case_request_parts(candidate, task_name, task, source)
                request = CompletionRequest(
                    model=model.litellm_model,
                    messages=messages,
                    response_schema=schema,
                    enforce_schema=True,
                    temperature=task.generation.temperature,
                    max_tokens=task.generation.max_tokens,
                    timeout=model.timeout_seconds,
                    retries=0,
                    api_base=model.api_base,
                    api_key=_optional_secret(model.api_key_env),
                    context_window=8192,
                    reasoning_effort=model.reasoning_effort,
                )
                alias = f"c{source.selection_index:03d}--{task_name}"
                response = None
                failure = None
                for retry in range(model.infrastructure_retries + 1):
                    attempts += 1
                    try:
                        response = await self.client.complete(request)
                        break
                    except LLMError as exc:
                        failure = exc
                        if retry < model.infrastructure_retries:
                            retries += 1
                if response is None:
                    outcomes.append(
                        CaseOutcome(
                            alias=alias,
                            task=task_name,
                            model_id=model_id,
                            terminal=True,
                            valid=False,
                            semantic_agreement=0,
                            diagnostics=[
                                Diagnostic(
                                    category="timeout"
                                    if getattr(failure, "kind", "") == "timeout"
                                    else "schema",
                                    schema_path="$",
                                    observed="provider-failure",
                                )
                            ],
                        )
                    )
                    continue
                if (
                    response.provider != model.expected_provider
                    or response.model != model.expected_model
                ):
                    raise ValueError(
                        f"candidate response identity mismatch for configured model {model_id}"
                    )
                usage = response.usage or {}
                input_tokens += int(usage.get("prompt_tokens", 0) or 0)
                output_tokens += int(usage.get("completion_tokens", 0) or 0)
                outcomes.append(
                    _validate_response(
                        alias,
                        task_name,
                        model_id,
                        response.content,
                        selector.selected_message_ids,
                        source.start_date,
                        source.last_active_date,
                        authority.references[alias].output,
                        task.output_schema,
                    )
                )
        latency = round((time.monotonic() - started) * 1000)
        hours = latency / 3_600_000
        return EvaluationBatch(
            scope=scope,
            model_id=model_id,
            outcomes=outcomes,
            usage=AdapterUsage(
                task_calls=attempts,
                retries=retries,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                compute_hours=hours,
                compute_cost_usd=hours * _compute_hourly_cost(self.config),
                latency_ms=latency,
            ),
        )


class DspyOptimizerAdapter(OptimizerAdapter):
    def __init__(
        self, config: OptimizationConfig, config_path: Path, authority: VerifiedAuthority
    ) -> None:
        if config.proposer.provider != "Anthropic" or config.proposer.region != "global":
            raise ValueError("tracked proposer adapter supports Anthropic global processing only")
        self.config = config
        self.config_path = config_path
        self.authority = authority
        self.tasks = load_task_catalog(
            resolve_config_path(config_path, config.paths.accepted_task_catalog)
        )
        self.candidate_lms = self._candidate_lms()
        self.reflection_lm = proposer_lm(
            config.proposer.litellm_model,
            config.proposer.api_key_env,
            temperature=config.proposer.temperature,
            timeout=config.proposer.timeout_seconds,
            num_retries=0,
            cache=False,
            reasoning_effort=config.proposer.reasoning_effort,
        )

    def reservation(self, optimizer: Literal["bootstrap-few-shot", "gepa"]) -> AdapterReservation:
        if optimizer == "bootstrap-few-shot":
            task_calls = 6 * len(TASK_ORDER) * 2
            hours = self._reserved_optimizer_hours(task_calls, 0)
            return AdapterReservation(
                task_calls=task_calls,
                compute_hours=hours,
                compute_cost_usd=hours * _compute_hourly_cost(self.config),
            )
        task_calls = self.config.gepa_max_metric_calls_per_candidate
        proposer_calls = max(
            1, self.config.proposer.max_calls // self.config.budget.pilot_candidates
        )
        hours = self._reserved_optimizer_hours(task_calls, proposer_calls)
        return AdapterReservation(
            task_calls=task_calls,
            proposer_calls=proposer_calls,
            input_tokens=proposer_calls * self.config.proposer.per_call_input_tokens,
            output_tokens=proposer_calls * self.config.proposer.per_call_output_tokens,
            compute_hours=hours,
            compute_cost_usd=hours * _compute_hourly_cost(self.config),
        )

    def _reserved_optimizer_hours(self, task_calls: int, proposer_calls: int) -> float:
        candidate_seconds = max(
            model.estimated_seconds_per_task for model in self.config.candidate_models
        )
        seconds = (
            task_calls * candidate_seconds + proposer_calls * self.config.proposer.timeout_seconds
        )
        return seconds / 3600

    def bootstrap(self, parent: CandidatePackage, authority: VerifiedAuthority) -> Proposal:
        examples = self._examples(authority, "train")
        before = _history_counts([*self.candidate_lms.values()])
        authorized = {
            (example.task, example.model_id, example.selected_input): example.case_alias
            for example in examples
        }
        prompts = {task: parent.prompts[task].text for task in TASK_ORDER}
        demonstrations = {task: [] for task in TASK_ORDER}
        for task in TASK_ORDER:
            program = build_program(parent, self.candidate_lms)
            task_examples = [example for example in examples if example.task == task]
            compiled = compile_bootstrap(program, task_examples, self._metric)
            prompts[task] = prompts_from_program(compiled)[task]
            demonstrations[task] = demonstrations_from_program(compiled, task, authorized)
        verify_demonstration_authority(
            parent.model_copy(update={"demonstrations": demonstrations}),
            self.tasks,
            authority,
        )
        usage = _history_usage([*self.candidate_lms.values()], before)
        return Proposal(
            prompts=prompts,
            demonstrations=demonstrations,
            strategy="bootstrap-one-labeled-one-bootstrapped-candidate-teacher",
            usage=usage,
        )

    def gepa(
        self,
        parent: CandidatePackage,
        authority: VerifiedAuthority,
        feedback: str,
        ordinal: int,
    ) -> Proposal:
        del feedback
        program = build_program(parent, self.candidate_lms)
        train = self._examples(authority, "train")
        validation = self._examples(authority, "validation")
        lms = [*self.candidate_lms.values(), self.reflection_lm]
        before = _history_counts(lms)
        reservation = self.reservation("gepa")
        compiled = compile_gepa(
            program,
            train,
            validation,
            self._metric,
            self.reflection_lm,
            seed=self.config.seed + ordinal - 1,
            max_metric_calls=reservation.task_calls,
            log_dir=resolve_config_path(self.config_path, self.config.paths.run_root)
            / "dspy"
            / self.config.proposer.cache_namespace
            / f"gepa-{ordinal:04d}",
        )
        usage = _history_usage(lms, before, proposer_index=len(lms) - 1)
        return Proposal(
            prompts=prompts_from_program(compiled),
            strategy=f"gepa-instruction-only-pareto-{ordinal:04d}",
            usage=usage,
        )

    def _candidate_lms(self) -> dict[str, Any]:
        import dspy

        result = {}
        for model in self.config.candidate_models:
            result[model.id] = dspy.LM(
                model.litellm_model,
                api_base=model.api_base,
                api_key=_optional_secret(model.api_key_env),
                temperature=0,
                timeout=model.timeout_seconds,
                num_retries=0,
                cache=False,
            )
        return result

    def _examples(
        self, authority: VerifiedAuthority, scope: Literal["train", "validation"]
    ) -> list[Any]:
        import dspy

        manifest = authority.train if scope == "train" else authority.validation
        inputs = {source.selection_index: source for source in authority.inputs}
        examples = []
        for entry in manifest.ordered_conversations:
            source = inputs[entry.authority_index]
            for task_name in TASK_ORDER:
                task = self.tasks.tasks[task_name]
                selector = source.recent if task_name == "last-activity" else source.overview
                values = {
                    "conversation_id": str(source.source_conversation_id),
                    "provider": source.provider,
                    "title": source.source_title,
                    "start_date": source.start_date,
                    "last_active_date": source.last_active_date,
                    "transcript": selector.transcript,
                }
                for model_id in ("qwen", "phi"):
                    examples.append(
                        dspy.Example(
                            task=task_name,
                            model_id=model_id,
                            case_alias=f"c{source.selection_index:03d}--{task_name}",
                            selected_input=interpolate_prompt(task.user_prompt, values),
                            response_json=json.dumps(
                                authority.references[
                                    f"c{source.selection_index:03d}--{task_name}"
                                ].output,
                                sort_keys=True,
                            ),
                            reference_json=json.dumps(
                                authority.references[
                                    f"c{source.selection_index:03d}--{task_name}"
                                ].output,
                                sort_keys=True,
                            ),
                            allowed_evidence=selector.selected_message_ids,
                            start_date=source.start_date,
                            last_active_date=source.last_active_date,
                            output_schema=task.output_schema,
                        ).with_inputs("task", "model_id", "selected_input")
                    )
        return examples

    @staticmethod
    def _metric(gold, pred, trace=None, pred_name=None, pred_trace=None, **kwargs):
        del trace, pred_name, pred_trace, kwargs
        outcome = _validate_response(
            "optimizer-trace",
            gold.task,
            gold.model_id,
            pred.response_json,
            list(gold.allowed_evidence),
            gold.start_date,
            gold.last_active_date,
            json.loads(gold.reference_json),
            gold.output_schema,
        )
        score = (0.999 if outcome.valid else 0.0) + outcome.semantic_agreement / 1_000_000
        import dspy

        return dspy.Prediction(score=score, feedback=render_feedback(outcome.diagnostics))


def build_production_adapters(
    config: OptimizationConfig,
    config_path: Path,
    authority: VerifiedAuthority,
) -> ExecutionAdapters:
    return ExecutionAdapters(
        candidate=LiteLLMCandidateAdapter(config, config_path),
        optimizer=DspyOptimizerAdapter(config, config_path, authority),
    )


def _validate_response(
    alias: str,
    task: str,
    model_id: str,
    content: str,
    allowed_evidence: list[int],
    start_date: str,
    last_active_date: str,
    reference: dict[str, Any],
    output_schema: str,
) -> CaseOutcome:
    try:
        parsed = json.loads(content)
        spec = _schema_spec(output_schema)
        final = spec.final_model.model_validate(parsed).model_dump(mode="json")
        if not set(final.get("evidence_message_ids", [])) <= set(allowed_evidence):
            raise ValueError("evidence")
        if task == "conversation-summary" and (
            final["start_date"] != start_date or final["last_active_date"] != last_active_date
        ):
            raise ValueError("date")
        return CaseOutcome(
            alias=alias,
            task=task,
            model_id=model_id,
            terminal=True,
            valid=True,
            semantic_agreement=_agreement(final, reference),
            diagnostics=[],
        )
    except Exception as exc:
        category = (
            "evidence-mismatch"
            if str(exc) == "evidence"
            else ("date-mismatch" if str(exc) == "date" else "schema")
        )
        return CaseOutcome(
            alias=alias,
            task=task,
            model_id=model_id,
            terminal=True,
            valid=False,
            semantic_agreement=0,
            diagnostics=[Diagnostic(category=category, schema_path="$")],
        )


def _agreement(left: dict[str, Any], right: dict[str, Any]) -> float:
    keys = sorted(set(left) | set(right))
    return sum(left.get(key) == right.get(key) for key in keys) / len(keys) if keys else 1


def _model(config: OptimizationConfig, model_id: str):
    return next(model for model in config.candidate_models if model.id == model_id)


def _optional_secret(name: str | None) -> str | None:
    if name is None:
        return None
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"missing required candidate environment variable {name}")
    return value


def _compute_hourly_cost(config: OptimizationConfig) -> float:
    return config.budget.compute_cost_usd / config.budget.total_compute_hours


def _history_counts(lms: list[Any]) -> list[int]:
    return [len(getattr(lm, "history", [])) for lm in lms]


def _history_usage(
    lms: list[Any], before: list[int], proposer_index: int | None = None
) -> AdapterUsage:
    calls = input_tokens = output_tokens = 0
    proposer_calls = 0
    for index, (lm, start) in enumerate(zip(lms, before, strict=True)):
        for item in getattr(lm, "history", [])[start:]:
            calls += 1
            usage = item.get("usage") or {}
            if index == proposer_index:
                proposer_calls += 1
                input_tokens += int(usage.get("prompt_tokens", 0) or 0)
                output_tokens += int(usage.get("completion_tokens", 0) or 0)
            # DSPy history does not provide a portable latency field. The orchestrator records
            # one monotonic wall-clock duration around the complete optimizer attempt.
    return AdapterUsage(
        task_calls=calls - proposer_calls,
        proposer_calls=proposer_calls,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=0,
    )
