"""Private append-only evidence for GEPA proposals and adapter transports."""

from __future__ import annotations

import logging
import math
import time
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, StrictBool, StrictInt, field_validator, model_validator

from bench.io import canonical_bytes, digest, digest_bytes
from bench.models import StrictModel

_SHA256 = r"^[0-9a-f]{64}$"
_TASK_COMPONENT = r"^task_[0-3]$"


class ProposalFeedbackFact(StrictModel):
    category: Literal[
        "valid",
        "schema",
        "invalid-json",
        "invalid-enum",
        "evidence-mismatch",
        "cross-field",
        "date-mismatch",
        "label-mismatch",
        "timeout",
        "provider-failure",
        "context-boundary",
    ]
    schema_path: str = Field(default="$", min_length=1, max_length=120)

    @field_validator("schema_path")
    @classmethod
    def bounded_path(cls, value: str) -> str:
        if "\n" in value or "\r" in value:
            raise ValueError("proposal feedback path must be a bounded single line")
        return value


class ProposalPrivacyEvidence(StrictModel):
    scanner_version: str = Field(min_length=1, max_length=80)
    eligible: StrictBool
    finding_count: StrictInt = Field(ge=0)
    counts: dict[str, StrictInt]
    evidence_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def reconciles(self) -> ProposalPrivacyEvidence:
        if self.eligible != (self.finding_count == 0):
            raise ValueError("proposal privacy eligibility/count mismatch")
        if sum(self.counts.values()) != self.finding_count:
            raise ValueError("proposal privacy counts do not reconcile")
        return self


class ProposalEnvelope(StrictModel):
    contract_version: Literal[1] = 1
    run_id: str = Field(min_length=1, max_length=120)
    optimizer_id: str = Field(min_length=1, max_length=120)
    optimizer_identity_sha256: str = Field(pattern=_SHA256)
    proposal_ordinal: StrictInt = Field(gt=0)
    selected_component: str = Field(pattern=_TASK_COMPONENT)
    parent_identity_sha256: str = Field(pattern=_SHA256)
    proposed_prompt_text: str = Field(min_length=1)
    parent_prompt_sha256: str = Field(pattern=_SHA256)
    proposal_prompt_sha256: str = Field(pattern=_SHA256)
    parent_utf8_bytes: StrictInt = Field(gt=0)
    proposal_utf8_bytes: StrictInt = Field(gt=0)
    utf8_byte_delta: StrictInt
    demonstration_identities: list[str]
    example_local_ids: list[StrictInt]
    parent_scores: list[float]
    proposal_scores: list[float]
    feedback: list[ProposalFeedbackFact] = Field(max_length=64)
    privacy: ProposalPrivacyEvidence
    event_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def reconciles(self) -> ProposalEnvelope:
        parent = self.parent_utf8_bytes
        proposed = self.proposed_prompt_text.encode("utf-8")
        if digest_bytes(proposed) != self.proposal_prompt_sha256:
            raise ValueError("proposal prompt identity mismatch")
        if len(proposed) != self.proposal_utf8_bytes:
            raise ValueError("proposal prompt byte length mismatch")
        if self.proposal_utf8_bytes - parent != self.utf8_byte_delta:
            raise ValueError("proposal prompt byte delta mismatch")
        if len(self.parent_scores) != len(self.proposal_scores) or not self.parent_scores:
            raise ValueError("proposal score vectors must be nonempty and aligned")
        if len(self.example_local_ids) != len(self.parent_scores):
            raise ValueError("proposal examples and scores must be aligned")
        if len(self.example_local_ids) != len(set(self.example_local_ids)):
            raise ValueError("proposal example identities must be unique")
        if any(value < 0 for value in self.example_local_ids):
            raise ValueError("proposal example identities must be nonnegative")
        if any(not item or len(item) != 64 for item in self.demonstration_identities):
            raise ValueError("proposal demonstration identity is malformed")
        if any(
            not math.isfinite(score) or not 0 <= score <= 1
            for score in [*self.parent_scores, *self.proposal_scores]
        ):
            raise ValueError("proposal scores must be finite and bounded")
        payload = self.model_dump(mode="json", exclude={"event_sha256"})
        if digest(payload) != self.event_sha256:
            raise ValueError("proposal event identity mismatch")
        return self


class ProposalDecision(StrictModel):
    contract_version: Literal[1] = 1
    run_id: str = Field(min_length=1, max_length=120)
    optimizer_id: str = Field(min_length=1, max_length=120)
    optimizer_identity_sha256: str = Field(pattern=_SHA256)
    proposal_ordinal: StrictInt = Field(gt=0)
    proposal_event_sha256: str = Field(pattern=_SHA256)
    decision: Literal["accepted", "rejected"]
    reason: Literal["gepa-accepted", "gepa-strict-score-rejection", "gepa-rejected"]
    decision_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def identity(self) -> ProposalDecision:
        if (self.decision == "accepted") != (self.reason == "gepa-accepted"):
            raise ValueError("proposal decision and reason do not reconcile")
        payload = self.model_dump(mode="json", exclude={"decision_sha256"})
        if digest(payload) != self.decision_sha256:
            raise ValueError("proposal decision identity mismatch")
        return self


def proposal_envelope(**values: Any) -> ProposalEnvelope:
    values = _json_value(values)
    values["event_sha256"] = digest(values)
    return ProposalEnvelope.model_validate(values)


def proposal_decision(**values: Any) -> ProposalDecision:
    values["decision_sha256"] = digest(values)
    return ProposalDecision.model_validate(values)


def _json_value(value: Any) -> Any:
    if isinstance(value, StrictModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


class ProposalEventStore:
    """Append-only private store; envelope must precede its decision."""

    def __init__(self, root: Path, *, run_id: str, optimizer_id: str, optimizer_identity: str):
        self.root = root.resolve()
        self.run_id = run_id
        self.optimizer_id = optimizer_id
        self.optimizer_identity = optimizer_identity

    def append_envelope(self, event: ProposalEnvelope) -> None:
        self._owned(event.run_id, event.optimizer_id, event.optimizer_identity_sha256)
        path = self._path("envelopes", event.proposal_ordinal, event.event_sha256)
        self._append_new(path, event.model_dump(mode="json"))

    def append_decision(self, event: ProposalDecision) -> None:
        self._owned(event.run_id, event.optimizer_id, event.optimizer_identity_sha256)
        envelopes, decisions = self.verify(allow_pending=True)
        envelope = envelopes.get(event.proposal_ordinal)
        if envelope is None or envelope.event_sha256 != event.proposal_event_sha256:
            raise ValueError("proposal decision has no matching pre-decision envelope")
        if event.proposal_ordinal in decisions:
            raise ValueError("proposal decision is duplicate or ambiguous")
        path = self._path("decisions", event.proposal_ordinal, event.decision_sha256)
        self._append_new(path, event.model_dump(mode="json"))

    def verify(
        self, *, allow_pending: bool = False
    ) -> tuple[dict[int, ProposalEnvelope], dict[int, ProposalDecision]]:
        if self.root.exists():
            for path in self.root.iterdir():
                if path.name not in {"envelopes", "decisions"} or not path.is_dir():
                    raise ValueError("proposal store contains a foreign artifact")
        envelopes = self._read_kind("envelopes", ProposalEnvelope, "event_sha256")
        decisions = self._read_kind("decisions", ProposalDecision, "decision_sha256")
        unknown = set(decisions) - set(envelopes)
        if unknown:
            raise ValueError("proposal store contains a foreign decision")
        for ordinal, decision in decisions.items():
            if decision.proposal_event_sha256 != envelopes[ordinal].event_sha256:
                raise ValueError("proposal decision references the wrong envelope")
        if not allow_pending and set(envelopes) != set(decisions):
            raise ValueError("proposal store contains an interrupted pending decision")
        return envelopes, decisions

    def _read_kind(self, name: str, model: type[StrictModel], hash_field: str) -> dict[int, Any]:
        directory = self.root / name
        if not directory.exists():
            return {}
        if directory.is_symlink():
            raise ValueError("proposal store directory cannot be a symlink")
        result: dict[int, Any] = {}
        for path in sorted(directory.iterdir()):
            if path.is_symlink() or not path.is_file() or path.suffix != ".json":
                raise ValueError("proposal store contains a foreign artifact")
            try:
                value = model.model_validate_json(path.read_text(encoding="utf-8"))
            except Exception as exc:
                raise ValueError("proposal store contains invalid or tampered evidence") from exc
            self._owned(value.run_id, value.optimizer_id, value.optimizer_identity_sha256)
            expected = f"{value.proposal_ordinal:04d}-{getattr(value, hash_field)}.json"
            if path.name != expected:
                raise ValueError("proposal evidence filename identity mismatch")
            if value.proposal_ordinal in result:
                raise ValueError("proposal store contains a duplicate ordinal")
            result[value.proposal_ordinal] = value
        return result

    def _owned(self, run_id: str, optimizer_id: str, optimizer_identity: str) -> None:
        if (run_id, optimizer_id, optimizer_identity) != (
            self.run_id,
            self.optimizer_id,
            self.optimizer_identity,
        ):
            raise ValueError("proposal evidence belongs to a foreign optimizer run")

    def _path(self, kind: str, ordinal: int, identity: str) -> Path:
        return self.root / kind / f"{ordinal:04d}-{identity}.json"

    @staticmethod
    def _append_new(path: Path, value: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("xb") as handle:
                handle.write(canonical_bytes(value))
                handle.flush()
        except FileExistsError as exc:
            raise ValueError("proposal evidence is append-only and already exists") from exc


class AdapterTransportEvent(StrictModel):
    contract_version: Literal[1] = 1
    run_id: str = Field(min_length=1, max_length=120)
    optimizer_identity_sha256: str = Field(pattern=_SHA256)
    logical_score_position: StrictInt = Field(ge=0)
    transport_ordinal: StrictInt = Field(gt=0)
    adapter: Literal["chat", "json"]
    fallback: StrictBool
    terminal: Literal["response", "provider-error", "adapter-format-error"]
    provider_retry_ordinal: Literal[0] = 0
    usage_available: StrictBool
    input_tokens: StrictInt | None = Field(default=None, ge=0)
    output_tokens: StrictInt | None = Field(default=None, ge=0)
    latency_available: StrictBool
    latency_ms: StrictInt | None = Field(default=None, ge=0)
    event_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def reconciles(self) -> AdapterTransportEvent:
        values = (self.input_tokens, self.output_tokens)
        if self.usage_available != all(value is not None for value in values):
            raise ValueError("adapter transport availability does not reconcile")
        if self.latency_available != (self.latency_ms is not None):
            raise ValueError("adapter transport latency availability does not reconcile")
        if self.adapter == "chat" and self.fallback:
            raise ValueError("primary ChatAdapter transport cannot be a fallback")
        if self.adapter == "json" and not self.fallback:
            raise ValueError("JSONAdapter transport must be identified as fallback")
        payload = self.model_dump(mode="json", exclude={"event_sha256"})
        if digest(payload) != self.event_sha256:
            raise ValueError("adapter transport event identity mismatch")
        return self


def adapter_transport_event(**values: Any) -> AdapterTransportEvent:
    values["event_sha256"] = digest(values)
    return AdapterTransportEvent.model_validate(values)


class AdapterTransportStore:
    """Append-only exact transport ledger, distinct from provider retry accounting."""

    def __init__(self, root: Path, *, run_id: str, optimizer_identity: str):
        self.root = root.resolve()
        self.run_id = run_id
        self.optimizer_identity = optimizer_identity

    def append(self, event: AdapterTransportEvent) -> None:
        if (event.run_id, event.optimizer_identity_sha256) != (
            self.run_id,
            self.optimizer_identity,
        ):
            raise ValueError("adapter transport belongs to a foreign optimizer run")
        path = self.root / f"{event.transport_ordinal:06d}-{event.event_sha256}.json"
        ProposalEventStore._append_new(path, event.model_dump(mode="json"))

    def next_transport_ordinal(self) -> int:
        return len(self.verify()) + 1

    def next_logical_score_position(self) -> int:
        events = self.verify()
        return max((event.logical_score_position for event in events), default=-1) + 1

    def verify(self, *, expected_task_calls: int | None = None) -> list[AdapterTransportEvent]:
        if not self.root.exists():
            events: list[AdapterTransportEvent] = []
        else:
            events = []
            seen_positions: dict[int, list[AdapterTransportEvent]] = {}
            for path in sorted(self.root.iterdir()):
                if path.is_symlink() or not path.is_file() or path.suffix != ".json":
                    raise ValueError("adapter transport store contains a foreign artifact")
                try:
                    event = AdapterTransportEvent.model_validate_json(path.read_text("utf-8"))
                except Exception as exc:
                    raise ValueError("adapter transport evidence is invalid or tampered") from exc
                if (event.run_id, event.optimizer_identity_sha256) != (
                    self.run_id,
                    self.optimizer_identity,
                ):
                    raise ValueError("adapter transport evidence belongs to a foreign run")
                expected = f"{event.transport_ordinal:06d}-{event.event_sha256}.json"
                if path.name != expected or event.transport_ordinal != len(events) + 1:
                    raise ValueError("adapter transport ordinals are ambiguous or incomplete")
                events.append(event)
                seen_positions.setdefault(event.logical_score_position, []).append(event)
            for position_events in seen_positions.values():
                signature = [(event.adapter, event.fallback) for event in position_events]
                if signature not in [[("chat", False)], [("chat", False), ("json", True)]]:
                    raise ValueError("adapter fallback sequence is ambiguous")
        if expected_task_calls is not None and len(events) != expected_task_calls:
            raise ValueError("adapter transports do not reconcile with task-call accounting")
        return events


_ADAPTER_TRANSPORT_CONTEXT: ContextVar[tuple[int, Literal["chat", "json"], bool] | None] = (
    ContextVar("chronicle_adapter_transport", default=None)
)


class AdapterTransportRecorder:
    """Record LM transports through DSPy's public callback interface."""

    def __init__(self, store: AdapterTransportStore, usage_extractor: Any) -> None:
        self.store = store
        self.usage_extractor = usage_extractor
        self.error: str | None = None
        self._calls: dict[str, tuple[Any, float, tuple[int, str, bool]]] = {}

    def __getattr__(self, name: str):
        if name.startswith("on_"):
            return lambda *args, **kwargs: None
        raise AttributeError(name)

    def on_lm_start(self, call_id: str, instance: Any, inputs: dict[str, Any]) -> None:
        del inputs
        context = _ADAPTER_TRANSPORT_CONTEXT.get()
        if context is not None:
            self._calls[call_id] = (instance, time.monotonic(), context)

    def on_lm_end(
        self, call_id: str, outputs: Any | None, exception: Exception | None = None
    ) -> None:
        del outputs
        captured = self._calls.pop(call_id, None)
        if captured is None:
            return
        try:
            instance, started, context = captured
            position, adapter, fallback = context
            usage = (
                self.usage_extractor(instance.history[-1])
                if exception is None and getattr(instance, "history", None)
                else None
            )
            event = adapter_transport_event(
                contract_version=1,
                run_id=self.store.run_id,
                optimizer_identity_sha256=self.store.optimizer_identity,
                logical_score_position=position,
                transport_ordinal=self.store.next_transport_ordinal(),
                adapter=adapter,
                fallback=fallback,
                terminal="response" if exception is None else "provider-error",
                provider_retry_ordinal=0,
                usage_available=usage is not None,
                input_tokens=None if usage is None else int(usage[0]),
                output_tokens=None if usage is None else int(usage[1]),
                latency_available=True,
                latency_ms=max(0, round((time.monotonic() - started) * 1000)),
            )
            self.store.append(event)
        except Exception:
            self.error = "adapter transport evidence capture failed"
            raise RuntimeError(self.error) from None

    def reconcile(self, *, expected_task_calls: int) -> list[AdapterTransportEvent]:
        if self.error is not None or self._calls:
            raise ValueError(self.error or "adapter transport callback is incomplete")
        return self.store.verify(expected_task_calls=expected_task_calls)


def explicit_fallback_adapter(store: AdapterTransportStore) -> Any:
    """Build an explicit ChatAdapter -> JSONAdapter fallback with no output repair."""
    import dspy
    from dspy.utils.exceptions import AdapterParseError

    class ExplicitFallbackAdapter(dspy.ChatAdapter):
        def __init__(self) -> None:
            super().__init__(use_json_adapter_fallback=False)

        def __call__(
            self, lm: Any, lm_kwargs: dict[str, Any], signature: Any, demos: Any, inputs: Any
        ):
            position = store.next_logical_score_position()
            token = _ADAPTER_TRANSPORT_CONTEXT.set((position, "chat", False))
            try:
                return super().__call__(lm, lm_kwargs, signature, demos, inputs)
            except AdapterParseError:
                json_token = _ADAPTER_TRANSPORT_CONTEXT.set((position, "json", True))
                try:
                    return self._make_json_adapter_fallback()(
                        lm, lm_kwargs, signature, demos, inputs
                    )
                finally:
                    _ADAPTER_TRANSPORT_CONTEXT.reset(json_token)
            finally:
                _ADAPTER_TRANSPORT_CONTEXT.reset(token)

    return ExplicitFallbackAdapter()


class PrivateProposalLogFilter(logging.Filter):
    """Redact GEPA's public logger surface that otherwise prints proposal text."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        if "Proposed new text for" in message:
            record.msg = "GEPA produced a private proposal; text retained in ignored evidence only"
            record.args = ()
        return True


def sanitized_feedback_facts(dataset: list[dict[str, Any]]) -> list[ProposalFeedbackFact]:
    """Extract only allowlisted category/path pairs from reflective examples."""
    allowed = set(ProposalFeedbackFact.model_fields["category"].annotation.__args__)
    result: list[ProposalFeedbackFact] = []
    for item in dataset:
        feedback = item.get("feedback")
        if not isinstance(feedback, str):
            continue
        for row in feedback.splitlines()[:16]:
            if row == "valid: no deterministic contract violation":
                fact = ProposalFeedbackFact(category="valid", schema_path="$")
            elif " at " in row:
                category, rest = row.split(" at ", 1)
                if category not in allowed:
                    continue
                path = rest.split(";", 1)[0][:120]
                fact = ProposalFeedbackFact(category=category, schema_path=path)
            else:
                continue
            if fact not in result:
                result.append(fact)
            if len(result) == 64:
                return result
    return result


class GEPAProposalObserver:
    """Use GEPA's public callback contract and verify it after compilation."""

    def __init__(
        self,
        store: ProposalEventStore,
        *,
        demonstration_identities: list[str],
        privacy_scan: Any,
    ) -> None:
        self.store = store
        self.demonstration_identities = sorted(demonstration_identities)
        self.privacy_scan = privacy_scan
        self._iterations: dict[int, dict[str, Any]] = {}
        self.error: str | None = None

    def on_minibatch_sampled(self, event: dict[str, Any]) -> None:
        self._capture(event, example_local_ids=[int(value) for value in event["minibatch_ids"]])

    def on_evaluation_end(self, event: dict[str, Any]) -> None:
        try:
            state = self._iterations.setdefault(int(event["iteration"]), {})
            scores = [float(value) for value in event["scores"]]
            if event["candidate_idx"] is not None:
                state["parent_scores"] = scores
                return
            state["proposal_scores"] = scores
            self._persist_predecision(int(event["iteration"]), state)
        except Exception:
            self.error = "proposal pre-decision evidence capture failed"
            raise RuntimeError(self.error) from None

    def on_proposal_start(self, event: dict[str, Any]) -> None:
        self._capture(
            event,
            parent_candidate=dict(event["parent_candidate"]),
            components=list(event["components"]),
            reflective_dataset=dict(event["reflective_dataset"]),
        )

    def on_proposal_end(self, event: dict[str, Any]) -> None:
        self._capture(event, new_instructions=dict(event["new_instructions"]))

    def on_candidate_accepted(self, event: dict[str, Any]) -> None:
        self._finalize(int(event["iteration"]), "accepted", "gepa-accepted")

    def on_candidate_rejected(self, event: dict[str, Any]) -> None:
        state = self._iterations.get(int(event["iteration"]), {})
        reason = (
            "gepa-strict-score-rejection"
            if sum(state.get("proposal_scores", [])) <= sum(state.get("parent_scores", []))
            else "gepa-rejected"
        )
        self._finalize(int(event["iteration"]), "rejected", reason)

    def reconcile(self) -> tuple[dict[int, ProposalEnvelope], dict[int, ProposalDecision]]:
        if self.error is not None:
            raise ValueError(self.error)
        return self.store.verify()

    def _capture(self, event: dict[str, Any], **values: Any) -> None:
        try:
            self._iterations.setdefault(int(event["iteration"]), {}).update(values)
        except Exception:
            self.error = "proposal callback event capture failed"
            raise RuntimeError(self.error) from None

    def _persist_predecision(self, iteration: int, state: dict[str, Any]) -> None:
        components = state["components"]
        new_instructions = state["new_instructions"]
        if len(components) != 1 or set(new_instructions) != set(components):
            raise ValueError("GEPA proposal must mutate exactly one observed component")
        component = components[0]
        parent_candidate = state["parent_candidate"]
        parent_text = parent_candidate[component]
        proposed_text = new_instructions[component]
        proposed_candidate = dict(parent_candidate)
        proposed_candidate[component] = proposed_text
        privacy = self.privacy_scan(proposed_candidate)
        event = proposal_envelope(
            contract_version=1,
            run_id=self.store.run_id,
            optimizer_id=self.store.optimizer_id,
            optimizer_identity_sha256=self.store.optimizer_identity,
            proposal_ordinal=iteration,
            selected_component=component,
            parent_identity_sha256=digest({"components": parent_candidate}),
            proposed_prompt_text=proposed_text,
            parent_prompt_sha256=digest_bytes(parent_text.encode("utf-8")),
            proposal_prompt_sha256=digest_bytes(proposed_text.encode("utf-8")),
            parent_utf8_bytes=len(parent_text.encode("utf-8")),
            proposal_utf8_bytes=len(proposed_text.encode("utf-8")),
            utf8_byte_delta=len(proposed_text.encode("utf-8")) - len(parent_text.encode("utf-8")),
            demonstration_identities=self.demonstration_identities,
            example_local_ids=state["example_local_ids"],
            parent_scores=state["parent_scores"],
            proposal_scores=state["proposal_scores"],
            feedback=sanitized_feedback_facts(state["reflective_dataset"][component]),
            privacy=privacy,
        )
        self.store.append_envelope(event)
        state["event"] = event
        if not privacy.eligible:
            raise ValueError("proposal privacy scan failed")

    def _finalize(self, iteration: int, decision: str, reason: str) -> None:
        try:
            state = self._iterations[iteration]
            event = state["event"]
            value = proposal_decision(
                contract_version=1,
                run_id=self.store.run_id,
                optimizer_id=self.store.optimizer_id,
                optimizer_identity_sha256=self.store.optimizer_identity,
                proposal_ordinal=iteration,
                proposal_event_sha256=event.event_sha256,
                decision=decision,
                reason=reason,
            )
            self.store.append_decision(value)
        except Exception:
            self.error = "proposal decision evidence finalization failed"
            raise RuntimeError(self.error) from None
