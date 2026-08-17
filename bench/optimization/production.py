"""Tracked DSPy/LiteLLM adapters used by the provider-facing optimizer CLI."""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError

from bench.core import _schema_spec
from bench.io import digest
from bench.models import TASK_ORDER
from chat_chronicle.ai import CompletionRequest, LiteLLMClient, LLMError
from chat_chronicle.ai_config import interpolate_prompt, load_task_catalog

from .authority import VerifiedAuthority
from .candidate_journal import CandidateJournalStore, JournalCase
from .diagnostics import (
    CompleteRequestGuard,
    OptimizerFailureRecorder,
    optimizer_failure_category,
)
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
    OptimizerOperationError,
    Proposal,
)
from .feedback import Diagnostic, render_feedback
from .models import (
    CandidateModel,
    OptimizationConfig,
    ProposerProfile,
    SearchScoreConfig,
    candidate_provider_matches,
    gepa_state_namespace,
    optimizer_framework_identity,
    proposer_cache_identity,
    resolve_config_path,
)
from .observability import (
    AdapterTransportRecorder,
    AdapterTransportStore,
    DurableInstructionProposer,
    GEPAProposalObserver,
    PrivateProposalLogFilter,
    ProposalEventStore,
    ProposalPrivacyEvidence,
    ProposerLifecycleStore,
    explicit_fallback_adapter,
)
from .package import CandidatePackage, mutate_package
from .privacy import scan_package
from .request_envelope import (
    case_request_parts,
    estimate_case_input_tokens,
    verify_demonstration_authority,
)

_RETRYABLE_INFRASTRUCTURE_FAILURES = frozenset({"connection", "rate_limit", "timeout"})


class LiteLLMCandidateAdapter(CandidateAdapter):
    def __init__(
        self,
        config: OptimizationConfig,
        config_path: Path,
        client: LiteLLMClient | None = None,
        *,
        environment: Mapping[str, str] | None = None,
        adc_probe: Callable[[], bool] | None = None,
        failure_injector: Callable[[str, str], None] | None = None,
    ) -> None:
        self.config = config
        self.config_path = config_path
        self.tasks = load_task_catalog(
            resolve_config_path(config_path, config.paths.accepted_task_catalog)
        )
        self.client = client or LiteLLMClient()
        self.failure_injector = failure_injector
        self.config_sha256 = digest(config.model_dump(mode="json"))
        self._active_journal: CandidateJournalStore | None = None
        self._active_cases: list[JournalCase] = []
        self.runtimes = {
            model.id: _candidate_runtime(
                model,
                environment=environment,
                adc_probe=adc_probe,
            )
            for model in config.candidate_models
        }

    def reservation(
        self, scope: Literal["train", "validation"], model_id: str
    ) -> AdapterReservation:
        conversations = (
            self.config.evaluation_train_conversation_limit
            if scope == "train"
            else self.config.evaluation_validation_conversation_limit
        ) or (6 if scope == "train" else 4)
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

    def reservation_for(
        self,
        candidate: CandidatePackage,
        scope: Literal["train", "validation"],
        model_id: str,
        authority: VerifiedAuthority,
    ) -> AdapterReservation:
        model = _model(self.config, model_id)
        journal = self._journal(candidate, scope, model_id)
        calls = retries = 0
        for case in self._expected_cases(candidate, scope, model_id, authority):
            if journal.terminal(case) is not None:
                continue
            prior = journal.attempt_count(case)
            remaining = max(0, 1 + model.infrastructure_retries - prior)
            calls += remaining
            retries += max(0, remaining - (1 if prior == 0 else 0))
        hours = calls * model.estimated_seconds_per_task / 3600
        return AdapterReservation(
            task_calls=calls,
            retries=retries,
            compute_hours=hours,
            compute_cost_usd=hours * _compute_hourly_cost(self.config),
        )

    def recorded_usage(
        self,
        candidate: CandidatePackage,
        scope: Literal["train", "validation"],
        model_id: str,
        authority: VerifiedAuthority,
    ) -> AdapterUsage:
        journal = self._journal(candidate, scope, model_id)
        return journal.usage(self._expected_cases(candidate, scope, model_id, authority))

    def evaluate(
        self,
        candidate: CandidatePackage,
        scope: Literal["train", "validation"],
        model_id: str,
        authority: VerifiedAuthority,
    ) -> EvaluationBatch:
        self._active_journal = None
        self._active_cases = []
        return asyncio.run(self._evaluate(candidate, scope, model_id, authority))

    def interrupted_usage(self) -> AdapterUsage | None:
        if self._active_journal is None:
            return None
        return self._active_journal.usage(self._active_cases)

    async def _evaluate(
        self,
        candidate: CandidatePackage,
        scope: Literal["train", "validation"],
        model_id: str,
        authority: VerifiedAuthority,
    ) -> EvaluationBatch:
        manifest = authority.train if scope == "train" else authority.validation
        inputs = {source.selection_index: source for source in authority.inputs}
        model = _model(self.config, model_id)
        journal = self._journal(candidate, scope, model_id)
        journal.usage(self._expected_cases(candidate, scope, model_id, authority))
        cases: list[JournalCase] = []
        self._active_journal = journal
        self._active_cases = cases
        limit = (
            self.config.evaluation_train_conversation_limit
            if scope == "train"
            else self.config.evaluation_validation_conversation_limit
        )
        for entry in manifest.ordered_conversations[:limit]:
            source = inputs[entry.authority_index]
            for task_name in TASK_ORDER:
                task = self.tasks.tasks[task_name]
                messages, schema, selector = case_request_parts(candidate, task_name, task, source)
                estimated_input_tokens = estimate_case_input_tokens(messages, schema)
                request = CompletionRequest(
                    model=model.litellm_model,
                    messages=messages,
                    response_schema=schema,
                    enforce_schema=True,
                    temperature=task.generation.temperature,
                    max_tokens=task.generation.max_tokens,
                    timeout=model.timeout_seconds,
                    retries=0,
                    context_window=model.context_window,
                    estimated_input_tokens=estimated_input_tokens,
                    reasoning_effort=model.reasoning_effort,
                    **self.runtimes[model_id],
                )
                alias = f"c{source.selection_index:03d}--{task_name}"
                case = JournalCase(
                    position=len(cases),
                    alias=alias,
                    task=task_name,
                    request_sha256=_candidate_request_sha256(request),
                )
                cases.append(case)
                terminal = journal.terminal(case)
                if terminal is not None:
                    continue
                if estimated_input_tokens + task.generation.max_tokens > model.context_window:
                    journal.append_context_outcome(
                        case,
                        CaseOutcome(
                            alias=alias,
                            task=task_name,
                            model_id=model_id,
                            terminal=True,
                            valid=False,
                            semantic_agreement=0,
                            diagnostics=[Diagnostic(category="context-boundary", schema_path="$")],
                        ),
                    )
                    continue
                remaining = 1 + model.infrastructure_retries - journal.attempt_count(case)
                if remaining <= 0:
                    raise RuntimeError("unfinished candidate case exhausted its retry allowance")
                response = None
                for _ in range(remaining):
                    intent = journal.begin_attempt(
                        case,
                        configured_provider=model.expected_provider,
                        configured_model=model.expected_model,
                        configured_region=model.resolved_location or "local",
                        reasoning_effort=model.reasoning_effort or "none",
                    )
                    stage = "before-transport"
                    try:
                        self._inject("before_transport", alias)
                        transport_started = time.monotonic()
                        response = await self.client.complete(request)
                    except LLMError as exc:
                        latency = max(0, round((time.monotonic() - transport_started) * 1000))
                        transport = journal.append_transport(
                            case,
                            intent,
                            terminal="provider-failure",
                            failure_category=_candidate_failure_category(exc),
                            actual_provider="unavailable",
                            actual_provider_sha256=None,
                            actual_model="unavailable",
                            actual_model_sha256=None,
                            finish_available=False,
                            finish_reason=None,
                            latency_available=True,
                            latency_ms=latency,
                        )
                        usage_event = journal.append_usage(
                            case,
                            transport,
                            usage_available=False,
                            input_tokens=None,
                            output_tokens=None,
                            reasoning_tokens=None,
                            provider_cost_available=False,
                            provider_cost_usd=None,
                        )
                        if (
                            intent.attempt_ordinal <= model.infrastructure_retries
                            and exc.kind in _RETRYABLE_INFRASTRUCTURE_FAILURES
                        ):
                            continue
                        outcome = CaseOutcome(
                            alias=alias,
                            task=task_name,
                            model_id=model_id,
                            terminal=True,
                            valid=False,
                            semantic_agreement=0,
                            diagnostics=[
                                Diagnostic(
                                    category="timeout"
                                    if exc.kind == "timeout"
                                    else "provider-failure",
                                    schema_path="$",
                                    observed="provider-failure",
                                )
                            ],
                        )
                        stage = "case-persistence"
                        self._inject("case_persistence", alias)
                        journal.append_outcome(case, transport, usage_event, outcome)
                        response = None
                        break
                    except Exception:
                        journal.append_interruption(case, intent, stage)
                        raise
                    latency = max(0, round((time.monotonic() - transport_started) * 1000))
                    provider_matches = candidate_provider_matches(model, response.provider)
                    model_matches = response.model == model.expected_model
                    transport = journal.append_transport(
                        case,
                        intent,
                        terminal="response",
                        failure_category="none",
                        actual_provider=(
                            "configured"
                            if response.provider == model.expected_provider
                            else ("accepted-alias" if provider_matches else "unexpected")
                        ),
                        actual_provider_sha256=digest(response.provider),
                        actual_model="configured" if model_matches else "unexpected",
                        actual_model_sha256=digest(response.model),
                        finish_available=True,
                        finish_reason=_candidate_finish_reason(response.finish_reason),
                        latency_available=True,
                        latency_ms=latency,
                    )
                    try:
                        stage = "after-response"
                        self._inject("after_response", alias)
                        stage = "identity-validation"
                        self._inject("identity_validation", alias)
                        if not provider_matches or not model_matches:
                            raise ValueError(
                                "candidate response identity mismatch for configured model "
                                f"{model_id}"
                            )
                        stage = "usage-adaptation"
                        self._inject("usage_adaptation", alias)
                        usage = response.usage
                        prompt_count, completion_count, reasoning_count = _history_entry_usage(
                            {"usage": usage}
                        )
                        if reasoning_count:
                            raise RuntimeError(
                                "candidate response violated the no-reasoning contract"
                            )
                        cost_available = isinstance(usage, Mapping) and "cost_usd" in usage
                        provider_cost = _provider_cost(usage or {})
                        usage_event = journal.append_usage(
                            case,
                            transport,
                            usage_available=usage is not None,
                            input_tokens=prompt_count if usage is not None else None,
                            output_tokens=completion_count if usage is not None else None,
                            reasoning_tokens=reasoning_count if usage is not None else None,
                            provider_cost_available=cost_available,
                            provider_cost_usd=provider_cost if cost_available else None,
                        )
                        stage = "output-validation"
                        self._inject("output_validation", alias)
                        outcome = _validate_response(
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
                        stage = "case-persistence"
                        self._inject("case_persistence", alias)
                        journal.append_outcome(case, transport, usage_event, outcome)
                    except Exception:
                        journal.append_interruption(case, intent, stage)
                        raise
                    break
                if journal.terminal(case) is None:
                    raise RuntimeError("candidate case did not reach a terminal journal outcome")
        try:
            self._inject("batch_finalization", f"{scope}:{model_id}")
        except Exception:
            journal.append_batch_interruption(len(cases))
            raise
        return journal.finalize(cases)

    def _inject(self, stage: str, alias: str) -> None:
        if self.failure_injector is not None:
            self.failure_injector(stage, alias)

    def _journal(
        self,
        candidate: CandidatePackage,
        scope: Literal["train", "validation"],
        model_id: str,
    ) -> CandidateJournalStore:
        run_root = resolve_config_path(self.config_path, self.config.paths.run_root)
        return CandidateJournalStore(
            run_root
            / "observability"
            / "candidate-evaluations"
            / candidate.candidate_id
            / scope
            / digest({"model_id": model_id})[:16],
            run_id=self.config.run_id,
            config_sha256=self.config_sha256,
            candidate_id=candidate.candidate_id,
            scope=scope,
            model_id=model_id,
            compute_hourly_cost=_compute_hourly_cost(self.config),
        )

    def _expected_cases(
        self,
        candidate: CandidatePackage,
        scope: Literal["train", "validation"],
        model_id: str,
        authority: VerifiedAuthority,
    ) -> list[JournalCase]:
        manifest = authority.train if scope == "train" else authority.validation
        inputs = {source.selection_index: source for source in authority.inputs}
        model = _model(self.config, model_id)
        limit = (
            self.config.evaluation_train_conversation_limit
            if scope == "train"
            else self.config.evaluation_validation_conversation_limit
        )
        cases = []
        for entry in manifest.ordered_conversations[:limit]:
            source = inputs[entry.authority_index]
            for task_name in TASK_ORDER:
                task = self.tasks.tasks[task_name]
                messages, schema, _ = case_request_parts(candidate, task_name, task, source)
                estimated = estimate_case_input_tokens(messages, schema)
                request = CompletionRequest(
                    model=model.litellm_model,
                    messages=messages,
                    response_schema=schema,
                    enforce_schema=True,
                    temperature=task.generation.temperature,
                    max_tokens=task.generation.max_tokens,
                    timeout=model.timeout_seconds,
                    retries=0,
                    context_window=model.context_window,
                    estimated_input_tokens=estimated,
                    reasoning_effort=model.reasoning_effort,
                    **self.runtimes[model_id],
                )
                cases.append(
                    JournalCase(
                        position=len(cases),
                        alias=f"c{source.selection_index:03d}--{task_name}",
                        task=task_name,
                        request_sha256=_candidate_request_sha256(request),
                    )
                )
        return cases


def build_proposer_client(
    profile: ProposerProfile,
    *,
    lm_factory: Callable[..., Any] = proposer_lm,
    environment: Mapping[str, str] | None = None,
    adc_probe: Callable[[], bool] | None = None,
) -> Any:
    """Resolve credentials transiently and build a proposer without serializing values."""
    environ = os.environ if environment is None else environment
    runtime: dict[str, Any] = {}
    if profile.credential_mode == "api-key-environment":
        assert profile.api_key_env is not None
        api_key = environ.get(profile.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"missing required proposer environment variable {profile.api_key_env}"
            )
        runtime["api_key"] = api_key
    else:
        names = {
            "Google Cloud project": profile.google_cloud_project_env,
            "Google Cloud location": profile.google_cloud_location_env,
            "Vertex project": profile.vertex_project_env,
            "Vertex location": profile.vertex_location_env,
            "Vertex enable flag": profile.vertex_enable_env,
        }
        values: dict[str, str] = {}
        for label, name in names.items():
            assert name is not None
            value = environ.get(name)
            if not value:
                raise RuntimeError(f"missing required {label} environment variable {name}")
            values[label] = value
        if values["Google Cloud project"] != values["Vertex project"]:
            raise RuntimeError("configured Vertex project environment variables disagree")
        if values["Google Cloud location"] != "global" or values["Vertex location"] != "global":
            raise RuntimeError("configured Vertex location must resolve to global")
        if values["Vertex enable flag"].casefold() not in {"1", "true", "yes"}:
            raise RuntimeError("configured Vertex enable environment variable must be true")
        probe = _default_adc_probe if adc_probe is None else adc_probe
        try:
            adc_available = probe()
        except Exception:
            adc_available = False
        if not adc_available:
            raise RuntimeError("Google Vertex AI Application Default Credentials are unavailable")
        runtime.update(
            vertex_project=values["Google Cloud project"],
            vertex_location="global",
        )
    budget_contract = {
        "max_calls": profile.max_calls,
        "max_input_tokens": profile.max_input_tokens,
        "max_output_tokens": profile.max_output_tokens,
        "input_usd_per_million": profile.input_usd_per_million,
        "output_usd_per_million": profile.output_usd_per_million,
        "max_cost_usd": profile.max_cost_usd,
    }
    try:
        return lm_factory(
            profile.litellm_model,
            credential_mode=profile.credential_mode,
            concurrency=profile.concurrency,
            budget_contract=budget_contract,
            temperature=profile.temperature,
            timeout=profile.timeout_seconds,
            num_retries=profile.infrastructure_retries,
            cache=False,
            reasoning_effort=profile.reasoning_effort,
            max_tokens=profile.per_call_output_tokens,
            **runtime,
        )
    except Exception:
        raise RuntimeError("failed to initialize configured optimizer proposer") from None


def _candidate_runtime(
    model: CandidateModel,
    *,
    environment: Mapping[str, str] | None = None,
    adc_probe: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    """Resolve a candidate route transiently without serializing credentials or project values."""
    environ = os.environ if environment is None else environment
    if model.credential_mode == "local-endpoint":
        return {
            "api_base": model.api_base,
            "api_key": _optional_secret(model.api_key_env, environ),
        }
    names = {
        "Google Cloud project": model.google_cloud_project_env,
        "Google Cloud location": model.google_cloud_location_env,
        "Vertex project": model.vertex_project_env,
        "Vertex location": model.vertex_location_env,
        "Vertex enable flag": model.vertex_enable_env,
    }
    values: dict[str, str] = {}
    for label, name in names.items():
        assert name is not None
        value = environ.get(name)
        if not value:
            raise RuntimeError(f"missing required candidate {label} environment variable {name}")
        values[label] = value
    if values["Google Cloud project"] != values["Vertex project"]:
        raise RuntimeError("configured candidate Vertex project environment variables disagree")
    if values["Google Cloud location"] != "global" or values["Vertex location"] != "global":
        raise RuntimeError("configured candidate Vertex location must resolve to global")
    if values["Vertex enable flag"].casefold() not in {"1", "true", "yes"}:
        raise RuntimeError("configured candidate Vertex enable environment variable must be true")
    probe = _default_adc_probe if adc_probe is None else adc_probe
    try:
        adc_available = probe()
    except Exception:
        adc_available = False
    if not adc_available:
        raise RuntimeError("Google Vertex AI Application Default Credentials are unavailable")
    return {
        "vertex_project": values["Google Cloud project"],
        "vertex_location": "global",
    }


def _default_adc_probe() -> bool:
    """Check ADC only when an explicitly authorized production adapter is constructed."""
    try:
        import google.auth

        credentials, _ = google.auth.default()
    except Exception:
        return False
    return credentials is not None


class DspyOptimizerAdapter(OptimizerAdapter):
    def __init__(
        self, config: OptimizationConfig, config_path: Path, authority: VerifiedAuthority
    ) -> None:
        self.config = config
        self.config_path = config_path
        self.authority = authority
        self.tasks = load_task_catalog(
            resolve_config_path(config_path, config.paths.accepted_task_catalog)
        )
        self.candidate_lms = self._candidate_lms()
        self.reflection_lm = build_proposer_client(config.proposer)

    def reservation(self, optimizer: Literal["bootstrap-few-shot", "gepa"]) -> AdapterReservation:
        if optimizer == "bootstrap-few-shot":
            task_calls = 6 * len(TASK_ORDER) * 2
            hours = self._reserved_optimizer_hours(task_calls, 0)
            return AdapterReservation(
                task_calls=task_calls,
                compute_hours=hours,
                compute_cost_usd=hours * _compute_hourly_cost(self.config),
            )
        validation_conversations = self.config.gepa_validation_conversation_limit or 4
        validation_positions = validation_conversations * len(TASK_ORDER)
        reflection_positions = 3
        if self.config.gepa_max_candidate_proposals is not None:
            logical_positions = validation_positions + (
                self.config.gepa_max_candidate_proposals
                * (2 * reflection_positions + validation_positions)
            )
        else:
            logical_positions = self.config.gepa_max_metric_calls_per_candidate + (
                2 * reflection_positions + validation_positions
            )
        task_calls = logical_positions * 2
        proposer_calls = self.config.gepa_max_candidate_proposals or max(
            1, self.config.proposer.max_calls // self.config.budget.pilot_candidates
        )
        hours = self._reserved_optimizer_hours(task_calls, proposer_calls)
        return AdapterReservation(
            task_calls=task_calls,
            proposer_calls=proposer_calls,
            input_tokens=proposer_calls * self.config.proposer.per_call_input_tokens,
            output_tokens=proposer_calls * self.config.proposer.per_call_output_tokens,
            retries=proposer_calls * self.config.proposer.infrastructure_retries,
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
        authorized = {
            (example.task, example.model_id, example.selected_input): example.case_alias
            for example in examples
        }
        prompts = {task: parent.prompts[task].text for task in TASK_ORDER}
        demonstrations = {task: [] for task in TASK_ORDER}
        observed_lms: list[Any] = []
        for task in TASK_ORDER:
            program = build_program(
                parent,
                self.candidate_lms,
                context_eligible=self._context_eligibility(parent, authority),
            )
            task_examples = [example for example in examples if example.task == task]
            try:
                compiled = compile_bootstrap(
                    program,
                    task_examples,
                    self._metric,
                    task=task,
                    history_sink=observed_lms.extend,
                )
                prompts[task] = prompts_from_program(compiled)[task]
                demonstrations[task] = demonstrations_from_program(compiled, task, authorized)
            except OptimizerOperationError:
                raise
            except Exception as exc:
                usage = _bootstrap_observed_usage(observed_lms)
                if usage is None:
                    raise
                raise OptimizerOperationError(
                    "BootstrapFewShot post-inference adaptation failed",
                    usage=usage,
                    failure_category=type(exc).__name__,
                ) from exc
        usage = _bootstrap_observed_usage(observed_lms)
        try:
            verify_demonstration_authority(
                parent.model_copy(update={"demonstrations": demonstrations}),
                self.tasks,
                authority,
            )
            if usage is None:
                raise ValueError("BootstrapFewShot copied-teacher usage history is missing")
            return Proposal(
                prompts=prompts,
                demonstrations=demonstrations,
                strategy="bootstrap-one-labeled-one-bootstrapped-candidate-teacher",
                usage=usage,
            )
        except OptimizerOperationError:
            raise
        except Exception as exc:
            if usage is None:
                raise
            raise OptimizerOperationError(
                "BootstrapFewShot post-inference authority validation failed",
                usage=usage,
                failure_category=type(exc).__name__,
            ) from exc

    def gepa(
        self,
        parent: CandidatePackage,
        authority: VerifiedAuthority,
        feedback: str,
        ordinal: int,
    ) -> Proposal:
        del feedback
        run_root = resolve_config_path(self.config_path, self.config.paths.run_root)
        identity = optimizer_framework_identity(self.config)
        evidence_root = run_root / "observability" / f"gepa-{ordinal:04d}"
        transport_store = AdapterTransportStore(
            evidence_root / "adapter-transports",
            run_id=self.config.run_id,
            optimizer_identity=identity,
        )
        candidate_lms = self.candidate_lms
        program = build_program(
            parent,
            candidate_lms,
            context_eligible=self._context_eligibility(parent, authority),
        )
        train = self._examples(authority, "train")
        validation = self._examples(authority, "validation")
        lms = [*candidate_lms.values(), self.reflection_lm]
        before = _history_counts(lms)
        for lm in candidate_lms.values():
            lm._chronicle_optimizer_role = "candidate"
        self.reflection_lm._chronicle_optimizer_role = "proposer"
        recorder = OptimizerFailureRecorder(usage_extractor=_history_entry_usage)
        context_guard = CompleteRequestGuard(
            context_window=self.config.context_window,
            output_allowance_tokens=max(
                task.generation.max_tokens for task in self.tasks.tasks.values()
            ),
        )
        import dspy

        proposal_store = ProposalEventStore(
            evidence_root / "proposal-events",
            run_id=self.config.run_id,
            optimizer_id=self.config.optimizer_id,
            optimizer_identity=identity,
        )
        lifecycle_store = ProposerLifecycleStore(
            evidence_root / "proposer-lifecycle",
            run_id=self.config.run_id,
            optimizer_id=self.config.optimizer_id,
            optimizer_identity=identity,
        )
        proposal_privacy_scan = self._proposal_privacy_scan(parent, authority, ordinal)
        observer = GEPAProposalObserver(
            proposal_store,
            demonstration_identities=[
                demo.demonstration_sha256
                for task in TASK_ORDER
                for demo in parent.demonstrations[task]
            ],
            privacy_scan=proposal_privacy_scan,
            lifecycle_store=lifecycle_store,
        )
        instruction_proposer = DurableInstructionProposer(
            lifecycle_store,
            observer,
            self.reflection_lm,
            configured_provider=self.config.proposer.provider,
            configured_model=self.config.proposer.litellm_model,
            configured_location=(
                self.config.proposer.resolved_location or self.config.proposer.region
            ),
            usage_extractor=_history_entry_usage,
            privacy_scan=proposal_privacy_scan,
        )
        adapter = explicit_fallback_adapter(transport_store)
        transport_recorder = AdapterTransportRecorder(transport_store, _transport_history_usage)
        log_filter = PrivateProposalLogFilter()
        gepa_logger = logging.getLogger("dspy.teleprompt.gepa.gepa")
        gepa_logger.addFilter(log_filter)

        try:
            with dspy.context(
                callbacks=[context_guard, recorder, transport_recorder], adapter=adapter
            ):
                state_namespace = gepa_state_namespace(self.config)
                state_root = (
                    run_root
                    / "dspy"
                    / self.config.proposer.cache_namespace
                    / proposer_cache_identity(self.config.proposer)[:16]
                )
                if state_namespace is not None:
                    state_root = state_root / f"search-{state_namespace}"
                compiled = compile_gepa(
                    program,
                    train,
                    validation,
                    self._metric,
                    self.reflection_lm,
                    seed=self.config.seed + ordinal - 1,
                    max_metric_calls=self.config.gepa_max_metric_calls_per_candidate,
                    max_candidate_proposals=self.config.gepa_max_candidate_proposals,
                    log_dir=state_root / f"gepa-{ordinal:04d}",
                    callbacks=[observer],
                    instruction_proposer=instruction_proposer,
                    use_merge=True if self.config.version == 1 else self.config.gepa_use_merge,
                )
            observer.reconcile()
            transport_recorder.reconcile(expected_task_calls=recorder.task_calls)
        except Exception as exc:
            usage = (
                AdapterUsage(
                    task_calls=recorder.task_calls,
                    proposer_calls=recorder.proposer_calls,
                    input_tokens=recorder.proposer_input_tokens,
                    output_tokens=recorder.proposer_output_tokens,
                )
                if recorder.task_calls or recorder.proposer_calls
                else None
            )
            primary = recorder.primary_category or optimizer_failure_category(exc)
            raise OptimizerOperationError(
                "GEPA provider or serialization operation failed",
                usage=usage,
                failure_category=primary,
                usage_complete=recorder.primary_category is None,
            ) from exc
        finally:
            gepa_logger.removeFilter(log_filter)
        usage = _history_usage(lms, before, proposer_index=len(lms) - 1).model_copy(
            update={
                "task_calls": recorder.task_calls,
                "proposer_calls": recorder.proposer_calls,
                "input_tokens": recorder.proposer_input_tokens,
                "output_tokens": recorder.proposer_output_tokens,
            }
        )
        if _reasoning_tokens_since(list(candidate_lms.values()), before[:-1]):
            raise OptimizerOperationError(
                "GEPA candidate violated the no-reasoning contract",
                usage=usage,
                failure_category="reasoning-policy",
            )
        return Proposal(
            prompts=prompts_from_program(compiled),
            strategy=f"gepa-instruction-only-pareto-{ordinal:04d}",
            usage=usage,
        )

    def _candidate_lms(self) -> dict[str, Any]:
        import dspy

        result = {}
        for model in self.config.candidate_models:
            runtime = _candidate_runtime(model)
            result[model.id] = dspy.LM(
                model.litellm_model,
                temperature=0,
                timeout=model.timeout_seconds,
                num_retries=0,
                cache=False,
                reasoning_effort=model.reasoning_effort,
                **runtime,
            )
        return result

    def _examples(
        self, authority: VerifiedAuthority, scope: Literal["train", "validation"]
    ) -> list[Any]:
        import dspy

        manifest = authority.train if scope == "train" else authority.validation
        limit = (
            self.config.gepa_train_conversation_limit
            if scope == "train"
            else self.config.gepa_validation_conversation_limit
        )
        inputs = {source.selection_index: source for source in authority.inputs}
        examples = []
        for entry in manifest.ordered_conversations[:limit]:
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
                for model_id in (model.id for model in self.config.candidate_models):
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

    def _metric(self, gold, pred, trace=None, pred_name=None, pred_trace=None, **kwargs):
        del trace, pred_name, pred_trace, kwargs
        if getattr(pred, "context_boundary", False):
            score = 0.0 if self.config.version == 1 else self.config.search_score.provider_invalid
            diagnostics = [Diagnostic(category="context-boundary", schema_path="$")]
        elif self.config.version == 1:
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
            diagnostics = outcome.diagnostics
        else:
            assessment = _search_assessment(
                gold.task,
                pred.response_json,
                list(gold.allowed_evidence),
                gold.start_date,
                gold.last_active_date,
                json.loads(gold.reference_json),
                gold.output_schema,
                self.config.search_score,
            )
            score = assessment.score
            diagnostics = assessment.diagnostics
        import dspy

        return dspy.Prediction(score=score, feedback=render_feedback(diagnostics))

    def _context_eligibility(
        self, parent: CandidatePackage, authority: VerifiedAuthority
    ) -> Callable[[str, str, str], bool]:
        values_by_input: dict[tuple[str, str], tuple[dict[str, str], Any]] = {}
        for source in authority.inputs:
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
                selected_input = interpolate_prompt(task.user_prompt, values)
                key = (task_name, selected_input)
                if key in values_by_input:
                    raise ValueError("optimizer context authority contains duplicate task inputs")
                values_by_input[key] = (values, selector)

        def eligible(task_name: str, selected_input: str, instructions: str) -> bool:
            key = (task_name, selected_input)
            if key not in values_by_input:
                raise ValueError("optimizer context request is outside development authority")
            values, selector = values_by_input[key]
            task = self.tasks.tasks[task_name]
            messages = [
                {
                    "role": "system",
                    "content": interpolate_prompt(instructions, values),
                }
            ]
            for demonstration in parent.demonstrations[task_name]:
                messages.extend(
                    (
                        {"role": "user", "content": demonstration.selected_input},
                        {"role": "assistant", "content": demonstration.response_json},
                    )
                )
            messages.append({"role": "user", "content": selected_input})
            schema = _schema_spec(task.output_schema).provider_model.model_json_schema()
            evidence = schema.get("properties", {}).get("evidence_message_ids", {})
            if selector.selected_message_ids and isinstance(evidence, dict):
                evidence.setdefault("items", {"type": "integer"})["enum"] = (
                    selector.selected_message_ids
                )
            estimated = estimate_case_input_tokens(messages, schema)
            return estimated + task.generation.max_tokens <= self.config.context_window

        return eligible

    def _proposal_privacy_scan(
        self, parent: CandidatePackage, authority: VerifiedAuthority, ordinal: int
    ) -> Callable[[dict[str, str]], ProposalPrivacyEvidence]:
        private_texts: list[str] = []
        exact_values: list[str] = []
        for source in authority.inputs:
            private_texts.extend((source.overview.transcript, source.recent.transcript))
            exact_values.append(source.source_title)
            exact_values.extend(str(value) for value in source.overview.selected_message_ids)
            exact_values.extend(str(value) for value in source.recent.selected_message_ids)
        for reference in authority.references.values():
            private_texts.append(json.dumps(reference.output, sort_keys=True))

        def scan(components: dict[str, str]) -> ProposalPrivacyEvidence:
            prompts = {task: components[f"task_{index}"] for index, task in enumerate(TASK_ORDER)}
            candidate = mutate_package(
                parent,
                prompts,
                optimizer="gepa",
                proposer_id=self.config.proposer.id,
                mutation_ordinal=ordinal,
            )
            result = scan_package(candidate, private_texts, exact_values=exact_values)
            return ProposalPrivacyEvidence(
                scanner_version=result.scanner_version,
                eligible=result.eligible,
                finding_count=result.finding_count,
                counts=result.counts,
                evidence_sha256=digest(result.model_dump(mode="json")),
            )

        return scan


@dataclass(frozen=True)
class SearchAssessment:
    stage: Literal[
        "provider-invalid",
        "invalid-json",
        "schema-invalid",
        "evidence-invalid",
        "cross-field-invalid",
        "fully-valid",
    ]
    score: float
    diagnostics: list[Diagnostic]


def _search_assessment(
    task: str,
    content: str,
    allowed_evidence: list[int],
    start_date: str,
    last_active_date: str,
    reference: dict[str, Any],
    output_schema: str,
    contract: SearchScoreConfig | None,
) -> SearchAssessment:
    """Grade deterministic reliability for GEPA reflection only."""
    if contract is None:
        raise ValueError("graded optimizer score contract is unavailable")
    if not isinstance(content, str) or not content.strip():
        return SearchAssessment(
            "provider-invalid",
            contract.provider_invalid,
            [Diagnostic(category="provider-failure", schema_path="$")],
        )
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return SearchAssessment(
            "invalid-json",
            contract.invalid_json,
            [Diagnostic(category="invalid-json", schema_path="$")],
        )
    spec = _schema_spec(output_schema)
    try:
        final = spec.final_model.model_validate(parsed).model_dump(mode="json")
    except ValidationError:
        return SearchAssessment(
            "schema-invalid",
            contract.schema_invalid,
            [Diagnostic(category="schema", schema_path="$")],
        )
    if not set(final.get("evidence_message_ids", [])) <= set(allowed_evidence):
        return SearchAssessment(
            "evidence-invalid",
            contract.evidence_invalid,
            [Diagnostic(category="evidence-mismatch", schema_path="$.evidence_message_ids")],
        )
    if task == "conversation-summary" and (
        final["start_date"] != start_date or final["last_active_date"] != last_active_date
    ):
        return SearchAssessment(
            "cross-field-invalid",
            contract.cross_field_invalid,
            [Diagnostic(category="date-mismatch", schema_path="$.start_date")],
        )
    agreement = _agreement(final, reference)
    return SearchAssessment(
        "fully-valid",
        contract.fully_valid_base + agreement * contract.fable_tiebreak_scale,
        [],
    )


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
    except json.JSONDecodeError:
        return _invalid_case_outcome(alias, task, model_id, "schema")
    spec = _schema_spec(output_schema)
    try:
        final = spec.final_model.model_validate(parsed).model_dump(mode="json")
    except ValidationError:
        return _invalid_case_outcome(alias, task, model_id, "schema")
    if not set(final.get("evidence_message_ids", [])) <= set(allowed_evidence):
        return _invalid_case_outcome(alias, task, model_id, "evidence-mismatch")
    if task == "conversation-summary" and (
        final["start_date"] != start_date or final["last_active_date"] != last_active_date
    ):
        return _invalid_case_outcome(alias, task, model_id, "date-mismatch")
    return CaseOutcome(
        alias=alias,
        task=task,
        model_id=model_id,
        terminal=True,
        valid=True,
        semantic_agreement=_agreement(final, reference),
        diagnostics=[],
    )


def _invalid_case_outcome(alias: str, task: str, model_id: str, category: str) -> CaseOutcome:
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


def _candidate_request_sha256(request: CompletionRequest) -> str:
    """Bind resumability to complete request bytes without persisting private text."""
    return digest(
        {
            "model": request.model,
            "messages": request.messages,
            "response_schema": request.response_schema,
            "enforce_schema": request.enforce_schema,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "timeout": request.timeout,
            "retries": request.retries,
            "api_base": request.api_base,
            "context_window": request.context_window,
            "estimated_input_tokens": request.estimated_input_tokens,
            "reasoning_effort": request.reasoning_effort,
            "vertex_location": request.vertex_location,
        }
    )


def _candidate_finish_reason(value: str) -> str:
    return (
        value if value in {"stop", "length", "content_filter", "tool_calls", "unknown"} else "other"
    )


def _candidate_failure_category(exc: LLMError) -> str:
    return {
        "connection": "connection",
        "rate_limit": "rate-limit",
        "timeout": "timeout",
        "invalid_json": "format",
        "dependency": "dependency",
    }.get(exc.kind, "provider")


def _optional_secret(name: str | None, environment: Mapping[str, str] | None = None) -> str | None:
    if name is None:
        return None
    environ = os.environ if environment is None else environment
    value = environ.get(name)
    if not value:
        raise RuntimeError(f"missing required candidate environment variable {name}")
    return value


def _provider_cost(usage: Mapping[str, Any]) -> float:
    value = usage.get("cost_usd", 0)
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(value)
        or value < 0
    ):
        raise TypeError("invalid provider cost field")
    return float(value)


def _compute_hourly_cost(config: OptimizationConfig) -> float:
    return config.budget.compute_cost_usd / config.budget.total_compute_hours


def _history_counts(lms: list[Any]) -> list[int]:
    return [len(getattr(lm, "history", [])) for lm in lms]


def _bootstrap_observed_usage(lms: list[Any]) -> AdapterUsage | None:
    """Return usage only when copied teacher history proves an inference occurred."""
    counts = _history_counts(lms)
    if not any(counts):
        return None
    return _history_usage(lms, [0] * len(lms))


def _history_usage(
    lms: list[Any], before: list[int], proposer_index: int | None = None
) -> AdapterUsage:
    calls = input_tokens = output_tokens = 0
    proposer_calls = 0
    for index, (lm, start) in enumerate(zip(lms, before, strict=True)):
        for item in getattr(lm, "history", [])[start:]:
            calls += 1
            prompt_tokens, completion_tokens, reasoning_tokens = _history_entry_usage(item)
            if proposer_index is None or index == proposer_index:
                input_tokens += prompt_tokens
                # Fail closed: separately reported reasoning is charged as output even when a
                # provider's completion-token semantics are ambiguous. Top-level and nested
                # reports are aliases, so reasoning is included once through their maximum.
                output_tokens += completion_tokens + reasoning_tokens
            if index == proposer_index:
                proposer_calls += 1
            # DSPy history does not provide a portable latency field. The orchestrator records
            # one monotonic wall-clock duration around the complete optimizer attempt.
    return AdapterUsage(
        task_calls=calls - proposer_calls,
        proposer_calls=proposer_calls,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=0,
    )


def _reasoning_tokens_since(lms: list[Any], before: list[int]) -> int:
    return sum(
        _history_entry_usage(item)[2]
        for lm, start in zip(lms, before, strict=True)
        for item in getattr(lm, "history", [])[start:]
    )


def _usage_field(value: Any, *names: str) -> tuple[bool, Any]:
    """Read one bounded usage field from mappings, models, or typed wrappers."""
    if value is None:
        return False, None
    mapping: Mapping[str, Any] | None = value if isinstance(value, Mapping) else None
    saw_field = False
    for name in names:
        if mapping is not None and name in mapping:
            saw_field = True
            candidate = mapping[name]
        elif hasattr(value, name):
            saw_field = True
            candidate = getattr(value, name)
        else:
            continue
        if candidate is not None:
            return True, candidate
    if saw_field:
        return True, None
    if mapping is not None:
        return False, None
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            dumped = model_dump(mode="python", exclude_none=False)
        except TypeError:
            dumped = model_dump()
        if not isinstance(dumped, Mapping):
            raise TypeError("unsupported populated DSPy usage structure")
        return _usage_field(dumped, *names)
    raise TypeError("unsupported populated DSPy usage structure")


def _token_count(value: Any, field: str) -> int:
    if value is None:
        return 0
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TypeError(f"invalid DSPy usage token field: {field}")
    return value


def _meaningfully_populated(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, Mapping):
        return any(item not in (None, {}, [], ()) for item in value.values())
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            dumped = model_dump(mode="python", exclude_none=True)
        except TypeError:
            dumped = model_dump()
        return isinstance(dumped, Mapping) and _meaningfully_populated(dumped)
    return True


def _transport_history_usage(item: Any) -> tuple[int, int, int] | None:
    has_response, response = _usage_field(item, "response")
    if has_response:
        has_usage, usage = _usage_field(response, "usage")
    else:
        has_usage, usage = _usage_field(item, "usage")
    if not has_usage or usage is None:
        return None
    return _history_entry_usage(item)


def _history_entry_usage(item: Any) -> tuple[int, int, int]:
    """Extract conservative token counts from the complete DSPy 3.3 history shape."""
    has_response, response = _usage_field(item, "response")
    if has_response:
        has_usage, usage = _usage_field(response, "usage")
    else:
        has_usage, usage = _usage_field(item, "usage")
    if not has_usage or usage is None:
        return 0, 0, 0

    has_prompt, prompt = _usage_field(usage, "prompt_tokens")
    has_input, input_value = _usage_field(usage, "input_tokens")
    has_completion, completion = _usage_field(usage, "completion_tokens")
    has_output, output_value = _usage_field(usage, "output_tokens")
    has_top_reasoning, top_reasoning = _usage_field(usage, "reasoning_tokens")
    has_details, details = _usage_field(usage, "completion_tokens_details")
    if not has_details:
        has_general_details, general_details = _usage_field(usage, "details")
        if has_general_details and general_details:
            has_nested_details, nested_details = _usage_field(
                general_details, "completion_tokens_details"
            )
            details = nested_details if has_nested_details else general_details
            has_details = True
    has_nested_reasoning = False
    nested_reasoning = None
    if details is not None:
        has_nested_reasoning, nested_reasoning = _usage_field(details, "reasoning_tokens")

    supported = any(
        (
            has_prompt,
            has_input,
            has_completion,
            has_output,
            has_top_reasoning,
            has_details,
            has_nested_reasoning,
        )
    )
    if not supported and _meaningfully_populated(usage):
        raise TypeError("unsupported populated DSPy usage structure")

    prompt_tokens = max(
        _token_count(prompt, "prompt"),
        _token_count(input_value, "input"),
    )
    completion_tokens = max(
        _token_count(completion, "completion"),
        _token_count(output_value, "output"),
    )
    reasoning_tokens = max(
        _token_count(top_reasoning, "reasoning"),
        _token_count(nested_reasoning, "completion details reasoning"),
    )
    return prompt_tokens, completion_tokens, reasoning_tokens
