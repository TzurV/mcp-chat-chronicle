"""Append-only ordinary candidate evaluation evidence and batch recovery."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, StrictBool, StrictInt, model_validator

from bench.io import canonical_bytes, digest
from bench.models import StrictModel

from .execution import AdapterUsage, CaseOutcome, EvaluationBatch

_SHA256 = r"^[0-9a-f]{64}$"


class CandidateRequestIntent(StrictModel):
    contract_version: Literal[1] = 1
    run_id: str = Field(min_length=1, max_length=120)
    config_sha256: str = Field(pattern=_SHA256)
    candidate_id: str = Field(min_length=1, max_length=120)
    scope: Literal["train", "validation"]
    model_id: str = Field(min_length=1, max_length=120)
    case_position: StrictInt = Field(ge=0)
    alias: str = Field(min_length=1, max_length=160)
    task: str = Field(min_length=1, max_length=80)
    attempt_ordinal: StrictInt = Field(gt=0)
    request_sha256: str = Field(pattern=_SHA256)
    configured_provider: str = Field(min_length=1, max_length=120)
    configured_model: str = Field(min_length=1, max_length=160)
    configured_region: str = Field(min_length=1, max_length=80)
    reasoning_effort: str = Field(min_length=1, max_length=40)
    event_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def identity(self) -> CandidateRequestIntent:
        if digest(self.model_dump(mode="json", exclude={"event_sha256"})) != self.event_sha256:
            raise ValueError("candidate request intent identity mismatch")
        return self


class CandidateTransportEvent(StrictModel):
    contract_version: Literal[1] = 1
    request_event_sha256: str = Field(pattern=_SHA256)
    attempt_ordinal: StrictInt = Field(gt=0)
    terminal: Literal["response", "provider-failure"]
    failure_category: Literal[
        "none",
        "connection",
        "rate-limit",
        "timeout",
        "format",
        "dependency",
        "provider",
    ]
    actual_provider: Literal["configured", "accepted-alias", "unexpected", "unavailable"]
    actual_provider_sha256: str | None = Field(default=None, pattern=_SHA256)
    actual_model: Literal["configured", "unexpected", "unavailable"]
    actual_model_sha256: str | None = Field(default=None, pattern=_SHA256)
    finish_available: StrictBool
    finish_reason: (
        Literal["stop", "length", "content_filter", "tool_calls", "other", "unknown"] | None
    ) = None
    latency_available: StrictBool
    latency_ms: StrictInt | None = Field(default=None, ge=0)
    event_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def reconciles(self) -> CandidateTransportEvent:
        if self.finish_available != (self.finish_reason is not None):
            raise ValueError("candidate transport finish availability mismatch")
        if self.latency_available != (self.latency_ms is not None):
            raise ValueError("candidate transport latency availability mismatch")
        if self.terminal == "response" and self.failure_category != "none":
            raise ValueError("candidate response cannot carry a provider failure")
        if self.terminal == "provider-failure" and self.failure_category == "none":
            raise ValueError("candidate provider failure requires a category")
        if digest(self.model_dump(mode="json", exclude={"event_sha256"})) != self.event_sha256:
            raise ValueError("candidate transport identity mismatch")
        return self


class CandidateUsageEvent(StrictModel):
    contract_version: Literal[1] = 1
    transport_event_sha256: str = Field(pattern=_SHA256)
    usage_available: StrictBool
    input_tokens: StrictInt | None = Field(default=None, ge=0)
    output_tokens: StrictInt | None = Field(default=None, ge=0)
    reasoning_tokens: StrictInt | None = Field(default=None, ge=0)
    provider_cost_available: StrictBool
    provider_cost_usd: float | None = Field(default=None, ge=0)
    event_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def reconciles(self) -> CandidateUsageEvent:
        counts = (self.input_tokens, self.output_tokens, self.reasoning_tokens)
        if self.usage_available != all(value is not None for value in counts):
            raise ValueError("candidate usage availability mismatch")
        if self.provider_cost_available != (self.provider_cost_usd is not None):
            raise ValueError("candidate cost availability mismatch")
        if digest(self.model_dump(mode="json", exclude={"event_sha256"})) != self.event_sha256:
            raise ValueError("candidate usage identity mismatch")
        return self


class CandidateTerminalOutcome(StrictModel):
    contract_version: Literal[1] = 1
    request_sha256: str = Field(pattern=_SHA256)
    transport_event_sha256: str | None = Field(default=None, pattern=_SHA256)
    usage_event_sha256: str | None = Field(default=None, pattern=_SHA256)
    terminal_category: Literal[
        "valid-response", "invalid-output", "provider-failure", "context-boundary"
    ]
    outcome: CaseOutcome
    event_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def reconciles(self) -> CandidateTerminalOutcome:
        if any(item.category == "context-boundary" for item in self.outcome.diagnostics):
            expected = "context-boundary"
        else:
            expected = (
                "valid-response"
                if self.outcome.valid
                else (
                    "provider-failure"
                    if any(
                        item.category in {"provider-failure", "timeout"}
                        for item in self.outcome.diagnostics
                    )
                    else "invalid-output"
                )
            )
        if self.terminal_category != expected or not self.outcome.terminal:
            raise ValueError("candidate terminal outcome category mismatch")
        linked = self.transport_event_sha256 is not None and self.usage_event_sha256 is not None
        if (expected != "context-boundary") != linked:
            raise ValueError("candidate terminal transport linkage mismatch")
        if digest(self.model_dump(mode="json", exclude={"event_sha256"})) != self.event_sha256:
            raise ValueError("candidate terminal outcome identity mismatch")
        return self


class CandidateInterruption(StrictModel):
    contract_version: Literal[1] = 1
    request_event_sha256: str = Field(pattern=_SHA256)
    category: Literal[
        "before-transport",
        "after-response",
        "identity-validation",
        "usage-adaptation",
        "output-validation",
        "case-persistence",
        "application-error",
    ]
    event_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def identity(self) -> CandidateInterruption:
        if digest(self.model_dump(mode="json", exclude={"event_sha256"})) != self.event_sha256:
            raise ValueError("candidate interruption identity mismatch")
        return self


class CandidateBatchEvent(StrictModel):
    contract_version: Literal[1] = 1
    run_id: str = Field(min_length=1, max_length=120)
    config_sha256: str = Field(pattern=_SHA256)
    candidate_id: str = Field(min_length=1, max_length=120)
    scope: Literal["train", "validation"]
    model_id: str = Field(min_length=1, max_length=120)
    terminal_event_sha256: list[str]
    usage: AdapterUsage
    event_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def identity(self) -> CandidateBatchEvent:
        if not self.terminal_event_sha256 or len(self.terminal_event_sha256) != len(
            set(self.terminal_event_sha256)
        ):
            raise ValueError("candidate batch terminal identities are incomplete")
        if digest(self.model_dump(mode="json", exclude={"event_sha256"})) != self.event_sha256:
            raise ValueError("candidate batch identity mismatch")
        return self


class CandidateBatchInterruption(StrictModel):
    contract_version: Literal[1] = 1
    run_id: str = Field(min_length=1, max_length=120)
    config_sha256: str = Field(pattern=_SHA256)
    candidate_id: str = Field(min_length=1, max_length=120)
    scope: Literal["train", "validation"]
    model_id: str = Field(min_length=1, max_length=120)
    terminal_case_count: StrictInt = Field(ge=0)
    category: Literal["batch-finalization"] = "batch-finalization"
    event_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def identity(self) -> CandidateBatchInterruption:
        if digest(self.model_dump(mode="json", exclude={"event_sha256"})) != self.event_sha256:
            raise ValueError("candidate batch interruption identity mismatch")
        return self


def _event(model: type[StrictModel], **values: Any) -> Any:
    values["event_sha256"] = digest(values)
    return model.model_validate(values)


@dataclass(frozen=True)
class JournalCase:
    position: int
    alias: str
    task: str
    request_sha256: str


class CandidateJournalStore:
    """Private append-only journal; only verified terminal cases are reusable."""

    def __init__(
        self,
        root: Path,
        *,
        run_id: str,
        config_sha256: str,
        candidate_id: str,
        scope: Literal["train", "validation"],
        model_id: str,
        compute_hourly_cost: float = 0,
    ) -> None:
        self.root = root.resolve()
        self.run_id = run_id
        self.config_sha256 = config_sha256
        self.candidate_id = candidate_id
        self.scope = scope
        self.model_id = model_id
        self.compute_hourly_cost = compute_hourly_cost

    def attempt_count(self, case: JournalCase) -> int:
        return len(self._case_state(case)[0])

    def terminal(self, case: JournalCase) -> CandidateTerminalOutcome | None:
        state = self._case_state(case)
        return state[3]

    def begin_attempt(
        self,
        case: JournalCase,
        *,
        configured_provider: str,
        configured_model: str,
        configured_region: str,
        reasoning_effort: str,
    ) -> CandidateRequestIntent:
        intents, _, _, terminal, _ = self._case_state(case)
        if terminal is not None:
            raise ValueError("candidate terminal case cannot be called again")
        intent = _event(
            CandidateRequestIntent,
            contract_version=1,
            run_id=self.run_id,
            config_sha256=self.config_sha256,
            candidate_id=self.candidate_id,
            scope=self.scope,
            model_id=self.model_id,
            case_position=case.position,
            alias=case.alias,
            task=case.task,
            attempt_ordinal=len(intents) + 1,
            request_sha256=case.request_sha256,
            configured_provider=configured_provider,
            configured_model=configured_model,
            configured_region=configured_region,
            reasoning_effort=reasoning_effort,
        )
        self._append(self._case_root(case) / "intents" / self._name(intent), intent)
        return intent

    def append_transport(self, case: JournalCase, intent: CandidateRequestIntent, **values: Any):
        self._require_intent(case, intent)
        event = _event(
            CandidateTransportEvent,
            contract_version=1,
            request_event_sha256=intent.event_sha256,
            attempt_ordinal=intent.attempt_ordinal,
            **values,
        )
        self._append(self._case_root(case) / "transports" / self._name(event), event)
        return event

    def append_usage(self, case: JournalCase, transport: CandidateTransportEvent, **values: Any):
        event = _event(
            CandidateUsageEvent,
            contract_version=1,
            transport_event_sha256=transport.event_sha256,
            **values,
        )
        self._append(self._case_root(case) / "usage" / self._name(event), event)
        return event

    def append_outcome(
        self,
        case: JournalCase,
        transport: CandidateTransportEvent,
        usage: CandidateUsageEvent,
        outcome: CaseOutcome,
    ) -> CandidateTerminalOutcome:
        if self.terminal(case) is not None:
            raise ValueError("candidate terminal outcome is duplicate")
        category = (
            "valid-response"
            if outcome.valid
            else (
                "provider-failure"
                if any(
                    item.category in {"provider-failure", "timeout"} for item in outcome.diagnostics
                )
                else "invalid-output"
            )
        )
        event = _event(
            CandidateTerminalOutcome,
            contract_version=1,
            request_sha256=case.request_sha256,
            transport_event_sha256=transport.event_sha256,
            usage_event_sha256=usage.event_sha256,
            terminal_category=category,
            outcome=outcome.model_dump(mode="json"),
        )
        self._append(self._case_root(case) / "terminal" / self._name(event), event)
        return event

    def append_context_outcome(
        self, case: JournalCase, outcome: CaseOutcome
    ) -> CandidateTerminalOutcome:
        intents, transports, usages, terminal, _ = self._case_state(case)
        if terminal is not None or intents or transports or usages:
            raise ValueError("candidate context outcome must precede every transport intent")
        event = _event(
            CandidateTerminalOutcome,
            contract_version=1,
            request_sha256=case.request_sha256,
            transport_event_sha256=None,
            usage_event_sha256=None,
            terminal_category="context-boundary",
            outcome=outcome.model_dump(mode="json"),
        )
        self._append(self._case_root(case) / "terminal" / self._name(event), event)
        return event

    def append_interruption(
        self, case: JournalCase, intent: CandidateRequestIntent, category: str
    ) -> None:
        event = _event(
            CandidateInterruption,
            contract_version=1,
            request_event_sha256=intent.event_sha256,
            category=category,
        )
        self._append(self._case_root(case) / "interruptions" / self._name(event), event)

    def append_batch_interruption(self, terminal_case_count: int) -> None:
        event = _event(
            CandidateBatchInterruption,
            contract_version=1,
            run_id=self.run_id,
            config_sha256=self.config_sha256,
            candidate_id=self.candidate_id,
            scope=self.scope,
            model_id=self.model_id,
            terminal_case_count=terminal_case_count,
            category="batch-finalization",
        )
        path = self.root / "batch-interruptions" / self._name(event)
        self._append(path, event)

    def finalize(self, cases: list[JournalCase]) -> EvaluationBatch:
        outcomes: list[CaseOutcome] = []
        terminal_hashes: list[str] = []
        for case in cases:
            _, _, _, terminal, _ = self._case_state(case)
            if terminal is None:
                raise ValueError("candidate batch contains an unfinished case journal")
            outcomes.append(terminal.outcome)
            terminal_hashes.append(terminal.event_sha256)
        usage = self.usage(cases, complete=True)
        batch = _event(
            CandidateBatchEvent,
            contract_version=1,
            run_id=self.run_id,
            config_sha256=self.config_sha256,
            candidate_id=self.candidate_id,
            scope=self.scope,
            model_id=self.model_id,
            terminal_event_sha256=terminal_hashes,
            usage=usage.model_dump(mode="json"),
        )
        path = self.root / "batches" / self._name(batch)
        if path.exists():
            if path.read_bytes() != canonical_bytes(batch.model_dump(mode="json")):
                raise ValueError("candidate batch evidence is not byte stable")
        else:
            existing = self._read(self.root / "batches", CandidateBatchEvent)
            if existing:
                raise ValueError("candidate batch evidence is duplicate or ambiguous")
            self._append(path, batch)
        return EvaluationBatch(
            scope=self.scope, model_id=self.model_id, outcomes=outcomes, usage=usage
        )

    def usage(self, cases: list[JournalCase], *, complete: bool = False) -> AdapterUsage:
        self._verify_layout(cases, complete=complete)
        task_calls = input_tokens = output_tokens = reasoning_tokens = latency_ms = 0
        attempted_cases = context_cases = 0
        provider_cost = 0.0
        for case in cases:
            intents, transports, usages, terminal, _ = self._case_state(case)
            if complete and terminal is None:
                raise ValueError("candidate batch contains an unfinished case journal")
            context_cases += (
                terminal is not None and terminal.terminal_category == "context-boundary"
            )
            task_calls += len(intents)
            attempted_cases += bool(intents)
            for usage in usages.values():
                input_tokens += usage.input_tokens or 0
                output_tokens += usage.output_tokens or 0
                reasoning_tokens += usage.reasoning_tokens or 0
                provider_cost += usage.provider_cost_usd or 0
            latency_ms += sum(event.latency_ms or 0 for event in transports.values())
        hours = latency_ms / 3_600_000
        return AdapterUsage(
            task_calls=task_calls,
            retries=task_calls - ((len(cases) - context_cases) if complete else attempted_cases),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            reasoning_tokens=reasoning_tokens,
            provider_cost_usd=provider_cost,
            compute_hours=hours,
            compute_cost_usd=hours * self.compute_hourly_cost,
            latency_ms=latency_ms,
        )

    def _case_state(self, case: JournalCase):
        root = self._case_root(case)
        if root.exists():
            allowed = {"intents", "transports", "usage", "terminal", "interruptions"}
            if root.is_symlink() or any(
                item.name not in allowed or item.is_symlink() or not item.is_dir()
                for item in root.iterdir()
            ):
                raise ValueError("candidate case journal contains a foreign artifact")
        intents = self._read(root / "intents", CandidateRequestIntent)
        transports = self._read(root / "transports", CandidateTransportEvent)
        usages = self._read(root / "usage", CandidateUsageEvent)
        terminals = self._read(root / "terminal", CandidateTerminalOutcome)
        interruptions = self._read(root / "interruptions", CandidateInterruption)
        intent_by_hash = {item.event_sha256: item for item in intents}
        if [item.attempt_ordinal for item in intents] != list(range(1, len(intents) + 1)):
            raise ValueError("candidate request attempt ordinals are incomplete")
        if any(
            (item.run_id, item.config_sha256, item.candidate_id, item.scope, item.model_id)
            != (self.run_id, self.config_sha256, self.candidate_id, self.scope, self.model_id)
            or (item.case_position, item.alias, item.task, item.request_sha256)
            != (case.position, case.alias, case.task, case.request_sha256)
            for item in intents
        ):
            raise ValueError("candidate request journal identity mismatch")
        transport_by_intent: dict[str, CandidateTransportEvent] = {}
        for item in transports:
            if (
                item.request_event_sha256 not in intent_by_hash
                or item.request_event_sha256 in transport_by_intent
            ):
                raise ValueError("candidate transport journal is foreign or duplicate")
            if item.attempt_ordinal != intent_by_hash[item.request_event_sha256].attempt_ordinal:
                raise ValueError("candidate transport attempt identity mismatch")
            transport_by_intent[item.request_event_sha256] = item
        usage_by_transport: dict[str, CandidateUsageEvent] = {}
        transport_hashes = {item.event_sha256 for item in transports}
        for item in usages:
            if (
                item.transport_event_sha256 not in transport_hashes
                or item.transport_event_sha256 in usage_by_transport
            ):
                raise ValueError("candidate usage journal is foreign or duplicate")
            usage_by_transport[item.transport_event_sha256] = item
        if any(item.request_event_sha256 not in intent_by_hash for item in interruptions):
            raise ValueError("candidate interruption journal is foreign")
        if len(terminals) > 1:
            raise ValueError("candidate terminal journal is duplicate or ambiguous")
        terminal = terminals[0] if terminals else None
        if terminal is not None:
            if terminal.request_sha256 != case.request_sha256:
                raise ValueError("candidate terminal request bytes do not match")
            if terminal.terminal_category == "context-boundary":
                if intents or transports or usages:
                    raise ValueError("candidate context terminal has transport evidence")
            else:
                transport = next(
                    (
                        item
                        for item in transports
                        if item.event_sha256 == terminal.transport_event_sha256
                    ),
                    None,
                )
                if transport is None or terminal.usage_event_sha256 not in {
                    item.event_sha256 for item in usages
                }:
                    raise ValueError("candidate terminal evidence chain is incomplete")
                terminal_attempt = transport.attempt_ordinal
                if any(item.attempt_ordinal > terminal_attempt for item in intents):
                    raise ValueError("candidate terminal case has a duplicate later call intent")
        return intents, transport_by_intent, usage_by_transport, terminal, interruptions

    def _verify_layout(self, cases: list[JournalCase], *, complete: bool) -> None:
        if not self.root.exists():
            if complete:
                raise ValueError("candidate journal is missing")
            return
        allowed = {"cases", "batches", "batch-interruptions"}
        if self.root.is_symlink() or any(item.name not in allowed for item in self.root.iterdir()):
            raise ValueError("candidate journal contains a foreign artifact")
        expected = {self._case_root(case).name for case in cases}
        cases_root = self.root / "cases"
        actual = set()
        if cases_root.exists():
            if cases_root.is_symlink() or not cases_root.is_dir():
                raise ValueError("candidate case journal root is invalid")
            for item in cases_root.iterdir():
                if item.is_symlink() or not item.is_dir():
                    raise ValueError("candidate case journal root contains a foreign artifact")
                actual.add(item.name)
        if not actual <= expected or (complete and actual != expected):
            raise ValueError("candidate case journal positions do not reconcile")
        batches = self._read(self.root / "batches", CandidateBatchEvent)
        interruptions = self._read(self.root / "batch-interruptions", CandidateBatchInterruption)
        for item in [*batches, *interruptions]:
            if (
                item.run_id,
                item.config_sha256,
                item.candidate_id,
                item.scope,
                item.model_id,
            ) != (
                self.run_id,
                self.config_sha256,
                self.candidate_id,
                self.scope,
                self.model_id,
            ):
                raise ValueError("candidate batch journal identity mismatch")

    def _require_intent(self, case: JournalCase, intent: CandidateRequestIntent) -> None:
        intents, transports, _, terminal, _ = self._case_state(case)
        if terminal is not None or intent.event_sha256 not in {
            item.event_sha256 for item in intents
        }:
            raise ValueError("candidate transport has no active request intent")
        if intent.event_sha256 in transports:
            raise ValueError("candidate transport attempt is duplicate")

    def _case_root(self, case: JournalCase) -> Path:
        return self.root / "cases" / f"{case.position:04d}-{case.alias}"

    @staticmethod
    def _name(event: Any) -> str:
        ordinal = getattr(event, "attempt_ordinal", 0)
        return f"{ordinal:04d}-{event.event_sha256}.json"

    @staticmethod
    def _append(path: Path, event: StrictModel) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("xb") as handle:
                handle.write(canonical_bytes(event.model_dump(mode="json")))
                handle.flush()
        except FileExistsError as exc:
            raise ValueError("candidate journal is append-only") from exc

    @staticmethod
    def _read(path: Path, model: type[StrictModel]) -> list[Any]:
        if not path.exists():
            return []
        if path.is_symlink() or not path.is_dir():
            raise ValueError("candidate journal directory is invalid")
        result = []
        for item in sorted(path.iterdir()):
            if item.is_symlink() or not item.is_file() or item.suffix != ".json":
                raise ValueError("candidate journal contains a foreign artifact")
            try:
                payload = item.read_bytes()
                value = model.model_validate_json(payload)
            except Exception as exc:
                raise ValueError("candidate journal contains invalid or tampered evidence") from exc
            if payload != canonical_bytes(value.model_dump(mode="json")):
                raise ValueError("candidate journal is not canonically byte verified")
            if item.name != CandidateJournalStore._name(value):
                raise ValueError("candidate journal filename identity mismatch")
            result.append(value)
        return result
