"""Provider-free regressions for GEPA observability and search scoring."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from bench.io import digest, digest_bytes
from bench.optimization import production
from bench.optimization.models import (
    OptimizationConfig,
    gepa_state_namespace,
    optimization_config_identity,
    optimizer_framework_identity,
)
from bench.optimization.observability import (
    AdapterTransportStore,
    GEPAProposalObserver,
    PrivateProposalLogFilter,
    ProposalEventStore,
    ProposalPrivacyEvidence,
    adapter_transport_event,
    explicit_fallback_adapter,
    proposal_decision,
    proposal_envelope,
)
from bench.optimization.production import DspyOptimizerAdapter, _search_assessment

SHA = "a" * 64


def _privacy() -> ProposalPrivacyEvidence:
    return ProposalPrivacyEvidence(
        scanner_version="optimizer-prompt-privacy-v1",
        eligible=True,
        finding_count=0,
        counts={},
        evidence_sha256=SHA,
    )


def _envelope(*, run_id: str = "synthetic", ordinal: int = 1, text: str = "new prompt"):
    parent = "old prompt"
    return proposal_envelope(
        contract_version=1,
        run_id=run_id,
        optimizer_id="synthetic",
        optimizer_identity_sha256=SHA,
        proposal_ordinal=ordinal,
        selected_component="task_0",
        parent_identity_sha256=SHA,
        proposed_prompt_text=text,
        parent_prompt_sha256=digest_bytes(parent.encode()),
        proposal_prompt_sha256=digest_bytes(text.encode()),
        parent_utf8_bytes=len(parent.encode()),
        proposal_utf8_bytes=len(text.encode()),
        utf8_byte_delta=len(text.encode()) - len(parent.encode()),
        demonstration_identities=[],
        example_local_ids=[0, 2, 1],
        parent_scores=[0.0, 0.0, 0.0],
        proposal_scores=[0.0, 0.0, 0.0],
        feedback=[{"category": "schema", "schema_path": "$"}],
        privacy=_privacy(),
    )


def _decision(event, *, decision: str = "rejected"):
    return proposal_decision(
        contract_version=1,
        run_id=event.run_id,
        optimizer_id=event.optimizer_id,
        optimizer_identity_sha256=event.optimizer_identity_sha256,
        proposal_ordinal=event.proposal_ordinal,
        proposal_event_sha256=event.event_sha256,
        decision=decision,
        reason="gepa-strict-score-rejection" if decision == "rejected" else "gepa-accepted",
    )


def _store(tmp_path: Path, *, run_id: str = "synthetic") -> ProposalEventStore:
    return ProposalEventStore(
        tmp_path / "private" / "proposal-events",
        run_id=run_id,
        optimizer_id="synthetic",
        optimizer_identity=SHA,
    )


def test_predecision_envelope_precedes_decision_and_rejected_text_is_retained(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    event = _envelope(text="private synthetic proposal")
    store.append_envelope(event)
    envelopes, decisions = store.verify(allow_pending=True)
    assert envelopes[1].proposed_prompt_text == "private synthetic proposal"
    assert decisions == {}
    with pytest.raises(ValueError, match="pending"):
        store.verify()

    store.append_decision(_decision(event))
    envelopes, decisions = store.verify()
    assert decisions[1].decision == "rejected"
    assert envelopes[1].proposal_scores == [0.0, 0.0, 0.0]


def test_interrupted_finalization_resumes_only_by_appending_decision(tmp_path: Path) -> None:
    store = _store(tmp_path)
    event = _envelope()
    store.append_envelope(event)
    with pytest.raises(ValueError, match="already exists"):
        store.append_envelope(event)
    store.append_decision(_decision(event))
    with pytest.raises(ValueError, match="duplicate or ambiguous"):
        store.append_decision(_decision(event))
    assert store.verify()[1][1].decision == "rejected"


def test_public_callback_persists_envelope_before_strict_rejection(tmp_path: Path) -> None:
    store = _store(tmp_path)
    observer = GEPAProposalObserver(
        store,
        demonstration_identities=[],
        privacy_scan=lambda prompts: _privacy(),
    )
    parent = {f"task_{index}": f"parent {index}" for index in range(4)}
    observer.on_minibatch_sampled({"iteration": 1, "minibatch_ids": [0, 2, 1]})
    observer.on_evaluation_end({"iteration": 1, "candidate_idx": 0, "scores": [0.0, 0.0, 0.0]})
    observer.on_proposal_start(
        {
            "iteration": 1,
            "parent_candidate": parent,
            "components": ["task_0"],
            "reflective_dataset": {"task_0": [{"feedback": "schema at $.summary; expected=array"}]},
        }
    )
    observer.on_proposal_end(
        {"iteration": 1, "new_instructions": {"task_0": "changed private prompt"}}
    )
    observer.on_evaluation_end({"iteration": 1, "candidate_idx": None, "scores": [0.0, 0.0, 0.0]})
    envelopes, decisions = store.verify(allow_pending=True)
    assert decisions == {}
    assert envelopes[1].example_local_ids == [0, 2, 1]
    assert envelopes[1].feedback[0].category == "schema"
    observer.on_candidate_rejected({"iteration": 1})
    assert observer.reconcile()[1][1].reason == "gepa-strict-score-rejection"


def test_proposal_store_rejects_tamper_foreign_and_duplicate_ordinals(tmp_path: Path) -> None:
    store = _store(tmp_path)
    event = _envelope()
    store.append_envelope(event)
    path = next((store.root / "envelopes").iterdir())
    payload = json.loads(path.read_text("utf-8"))
    payload["proposal_scores"] = [1.0, 1.0, 1.0]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid or tampered"):
        store.verify(allow_pending=True)

    foreign = _store(tmp_path / "foreign", run_id="other")
    with pytest.raises(ValueError, match="foreign"):
        foreign.append_envelope(event)

    duplicate = _store(tmp_path / "duplicate")
    first = _envelope()
    second = _envelope(text="different")
    duplicate.append_envelope(first)
    duplicate.append_envelope(second)
    with pytest.raises(ValueError, match="duplicate ordinal"):
        duplicate.verify(allow_pending=True)


def test_gepa_logger_filter_never_emits_proposal_text() -> None:
    filter_ = PrivateProposalLogFilter()
    record = logging.LogRecord(
        "dspy.teleprompt.gepa.gepa",
        logging.INFO,
        __file__,
        1,
        "Iteration 1: Proposed new text for task_0: secret proposal body",
        (),
        None,
    )
    assert filter_.filter(record)
    rendered = record.getMessage()
    assert "secret proposal body" not in rendered
    assert "private proposal" in rendered


def _transport(store: AdapterTransportStore, ordinal: int, position: int, adapter: str):
    return adapter_transport_event(
        contract_version=1,
        run_id="synthetic",
        optimizer_identity_sha256=SHA,
        logical_score_position=position,
        transport_ordinal=ordinal,
        adapter=adapter,
        fallback=adapter == "json",
        terminal="response",
        provider_retry_ordinal=0,
        usage_available=False,
        input_tokens=None,
        output_tokens=None,
        latency_available=True,
        latency_ms=4,
    )


def test_chat_json_fallback_and_provider_retry_accounting_are_distinct(tmp_path: Path) -> None:
    store = AdapterTransportStore(
        tmp_path / "private" / "transports",
        run_id="synthetic",
        optimizer_identity=SHA,
    )
    store.append(_transport(store, 1, 0, "chat"))
    store.append(_transport(store, 2, 0, "json"))
    store.append(_transport(store, 3, 1, "chat"))
    events = store.verify(expected_task_calls=3)
    assert [(e.logical_score_position, e.adapter, e.fallback) for e in events] == [
        (0, "chat", False),
        (0, "json", True),
        (1, "chat", False),
    ]
    assert {e.provider_retry_ordinal for e in events} == {0}
    assert not any(e.usage_available for e in events)
    with pytest.raises(ValueError, match="reconcile"):
        store.verify(expected_task_calls=2)


def test_only_adapter_parse_error_makes_exactly_one_json_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import dspy
    from dspy.utils.exceptions import AdapterParseError

    store = AdapterTransportStore(
        tmp_path / "private" / "transports",
        run_id="synthetic",
        optimizer_identity=SHA,
    )
    adapter = explicit_fallback_adapter(store)
    calls = {"chat": 0, "json": 0}
    sentinel = object()

    def chat(*args, **kwargs):
        del args, kwargs
        calls["chat"] += 1
        raise AdapterParseError(
            "ChatAdapter", SimpleNamespace(output_fields={}), "synthetic malformed response"
        )

    def json_fallback(*args, **kwargs):
        del args, kwargs
        calls["json"] += 1
        return sentinel

    monkeypatch.setattr(dspy.ChatAdapter, "__call__", chat)
    monkeypatch.setattr(adapter, "_make_json_adapter_fallback", lambda: json_fallback)
    assert adapter(None, {}, object(), [], {}) is sentinel
    assert calls == {"chat": 1, "json": 1}


class SyntheticCallbackError(RuntimeError):
    pass


class SyntheticConfigurationError(RuntimeError):
    pass


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(ValueError("value defect"), id="value-error"),
        pytest.param(TypeError("type defect"), id="type-error"),
        pytest.param(SyntheticCallbackError("callback defect"), id="callback-error"),
        pytest.param(SyntheticConfigurationError("configuration defect"), id="configuration-error"),
        pytest.param(RuntimeError("unexpected defect"), id="unexpected-error"),
    ],
)
def test_unrelated_adapter_errors_make_one_chat_and_zero_json_transports(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
) -> None:
    import dspy

    store = AdapterTransportStore(
        tmp_path / "private" / "transports",
        run_id="synthetic",
        optimizer_identity=SHA,
    )
    adapter = explicit_fallback_adapter(store)
    calls = {"chat": 0, "json": 0}

    def chat(*args, **kwargs):
        del args, kwargs
        calls["chat"] += 1
        raise error

    def json_fallback(*args, **kwargs):
        del args, kwargs
        calls["json"] += 1
        return object()

    monkeypatch.setattr(dspy.ChatAdapter, "__call__", chat)
    monkeypatch.setattr(adapter, "_make_json_adapter_fallback", lambda: json_fallback)
    with pytest.raises(type(error), match=str(error)):
        adapter(None, {}, object(), [], {})
    assert calls == {"chat": 1, "json": 0}


def test_lm_error_makes_one_chat_and_zero_json_transports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import dspy
    from dspy.utils.exceptions import LMError

    store = AdapterTransportStore(
        tmp_path / "private" / "transports",
        run_id="synthetic",
        optimizer_identity=SHA,
    )
    adapter = explicit_fallback_adapter(store)
    calls = {"chat": 0, "json": 0}

    def chat(*args, **kwargs):
        del args, kwargs
        calls["chat"] += 1
        raise LMError("provider failure")

    def json_fallback(*args, **kwargs):
        del args, kwargs
        calls["json"] += 1
        return object()

    monkeypatch.setattr(dspy.ChatAdapter, "__call__", chat)
    monkeypatch.setattr(adapter, "_make_json_adapter_fallback", lambda: json_fallback)
    with pytest.raises(LMError, match="provider failure"):
        adapter(None, {}, object(), [], {})
    assert calls == {"chat": 1, "json": 0}


@pytest.mark.parametrize(("proposals", "task_calls"), [(3, 164), (4, 208), (5, 252)])
def test_fallback_aware_gepa_reservation_is_exact(proposals: int, task_calls: int) -> None:
    config = _score_config().model_copy(update={"gepa_max_candidate_proposals": proposals})
    optimizer = object.__new__(DspyOptimizerAdapter)
    optimizer.config = config
    reservation = optimizer.reservation("gepa")
    assert reservation.task_calls == task_calls
    assert reservation.proposer_calls == proposals
    assert reservation.retries == proposals


def test_transport_store_rejects_ambiguous_fallback_and_foreign_events(tmp_path: Path) -> None:
    store = AdapterTransportStore(
        tmp_path / "private" / "transports",
        run_id="synthetic",
        optimizer_identity=SHA,
    )
    store.append(_transport(store, 1, 0, "json"))
    with pytest.raises(ValueError, match="fallback sequence"):
        store.verify()
    foreign = _transport(store, 2, 1, "chat").model_copy(update={"run_id": "foreign"})
    with pytest.raises(ValueError, match="foreign"):
        store.append(foreign)


def _score_config():
    template = yaml.safe_load(
        (Path(__file__).parents[1] / "bench" / "optimization.default.yaml").read_text("utf-8")
    )
    return OptimizationConfig.model_validate(template)


def _valid_summary(*, evidence: list[int] | None = None, start: str = "2026-01-01") -> str:
    return json.dumps(
        {
            "summary": "Synthetic work began. Synthetic work completed.",
            "start_date": start,
            "last_active_date": "2026-01-02",
            "evidence_message_ids": evidence if evidence is not None else [10],
        }
    )


def test_graded_search_ladder_is_strict_and_invalid_never_reaches_promotion_threshold() -> None:
    contract = _score_config().search_score
    reference = json.loads(_valid_summary())
    values = [
        _search_assessment(
            "conversation-summary",
            content,
            [10],
            "2026-01-01",
            "2026-01-02",
            reference,
            "conversation-summary-v1",
            contract,
        )
        for content in (
            "",
            "not json",
            "{}",
            _valid_summary(evidence=[999]),
            _valid_summary(start="2025-12-31"),
            _valid_summary(),
        )
    ]
    assert [value.stage for value in values] == [
        "provider-invalid",
        "invalid-json",
        "schema-invalid",
        "evidence-invalid",
        "cross-field-invalid",
        "fully-valid",
    ]
    assert [value.score for value in values] == sorted(value.score for value in values)
    assert max(value.score for value in values[:-1]) < 0.999
    assert values[-1].score >= 0.999


def test_gepa_context_boundary_uses_provider_invalid_score_without_output_adaptation() -> None:
    optimizer = object.__new__(DspyOptimizerAdapter)
    optimizer.config = _score_config()
    gold = SimpleNamespace(
        task="conversation-summary",
        model_id="synthetic",
        allowed_evidence=[10],
        start_date="2026-01-01",
        last_active_date="2026-01-02",
        reference_json=_valid_summary(),
        output_schema="conversation-summary-v1",
    )
    prediction = SimpleNamespace(response_json="", context_boundary=True)
    result = optimizer._metric(gold, prediction)
    assert result.score == optimizer.config.search_score.provider_invalid
    assert result.feedback == "context-boundary at $"


def _assert_score_failure_has_no_decision_or_additional_transport(
    tmp_path: Path, operation
) -> None:
    transports = AdapterTransportStore(
        tmp_path / "private" / "transports",
        run_id="synthetic",
        optimizer_identity=SHA,
    )
    transports.append(_transport(transports, 1, 0, "chat"))
    proposals = _store(tmp_path)
    operation()
    assert len(transports.verify(expected_task_calls=1)) == 1
    assert proposals.verify(allow_pending=True) == ({}, {})


def test_unknown_search_schema_propagates_without_decision_or_additional_call(
    tmp_path: Path,
) -> None:
    def operation() -> None:
        with pytest.raises(KeyError):
            _search_assessment(
                "conversation-summary",
                _valid_summary(),
                [10],
                "2026-01-01",
                "2026-01-02",
                json.loads(_valid_summary()),
                "unknown-schema-v999",
                _score_config().search_score,
            )

    _assert_score_failure_has_no_decision_or_additional_transport(tmp_path, operation)


def test_injected_schema_application_defect_propagates_without_decision_or_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class DefectiveModel:
        @staticmethod
        def model_validate(value):
            del value
            raise RuntimeError("injected model-validation defect")

    monkeypatch.setattr(
        production, "_schema_spec", lambda schema: SimpleNamespace(final_model=DefectiveModel)
    )

    def operation() -> None:
        with pytest.raises(RuntimeError, match="injected model-validation defect"):
            _search_assessment(
                "conversation-summary",
                _valid_summary(),
                [10],
                "2026-01-01",
                "2026-01-02",
                json.loads(_valid_summary()),
                "conversation-summary-v1",
                _score_config().search_score,
            )

    _assert_score_failure_has_no_decision_or_additional_transport(tmp_path, operation)


def test_unrelated_search_defect_propagates_without_decision_or_additional_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        production,
        "_agreement",
        lambda left, right: (_ for _ in ()).throw(RuntimeError("unrelated scoring defect")),
    )

    def operation() -> None:
        with pytest.raises(RuntimeError, match="unrelated scoring defect"):
            _search_assessment(
                "conversation-summary",
                _valid_summary(),
                [10],
                "2026-01-01",
                "2026-01-02",
                json.loads(_valid_summary()),
                "conversation-summary-v1",
                _score_config().search_score,
            )

    _assert_score_failure_has_no_decision_or_additional_transport(tmp_path, operation)


def test_v1_identity_is_historical_and_v2_score_changes_authority_and_state_namespace() -> None:
    v2 = _score_config()
    payload = yaml.safe_load(
        (Path(__file__).parents[1] / "bench" / "optimization.default.yaml").read_text("utf-8")
    )
    payload["version"] = 1
    payload.pop("search_score")
    payload.pop("gepa_use_merge")
    v1 = OptimizationConfig.model_validate(payload)
    historical_payload = v1.model_dump(mode="json", exclude={"search_score", "gepa_use_merge"})
    assert optimization_config_identity(v1) == digest(historical_payload)
    assert gepa_state_namespace(v1) is None
    assert gepa_state_namespace(v2) is not None
    assert optimization_config_identity(v1) != optimization_config_identity(v2)
    assert optimizer_framework_identity(v1) != optimizer_framework_identity(v2)


def test_observability_imports_are_offline_and_do_not_initialize_provider_modules() -> None:
    code = """
import sys
import bench.optimization.models
import bench.optimization.observability
forbidden = ['google.auth', 'litellm', 'dspy']
loaded = [name for name in forbidden if name in sys.modules]
if loaded:
    raise SystemExit(','.join(loaded))
print('offline-import-ok')
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).parents[1],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "offline-import-ok"
