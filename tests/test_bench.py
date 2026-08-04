from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import zipfile
from collections import Counter
from pathlib import Path

import pytest
import yaml
from bench import __main__ as bench_cli
from bench.core import (
    _conversation_identity,
    _manifest_payload,
    _scan_leakage,
    _source_selection_identity,
    _validate_implementation,
    build_authority,
    generate,
    prepare,
    score,
    verify,
)
from bench.implementation import ImplementationIdentity
from bench.io import (
    atomic_json,
    deterministic_zip,
    digest,
    safe_extract,
    verify_checksums,
    write_checksums,
)
from bench.judge import RUBRICS, provider_judge_schema, score_with_judge
from bench.loaders import load_inputs
from bench.models import (
    JUDGE_RATIONALE_MAX_LENGTH,
    EvaluationConfig,
    JudgeResult,
    SelectionManifest,
)
from bench.paths import resolve_member
from pydantic import ValidationError
from typer.testing import CliRunner

from chat_chronicle.ai import CompletionResponse, LLMError, canonical_hash
from chat_chronicle.ai_config import AIConfigError, load_model_catalog, resolve_model


def test_candidate_text_may_use_provenance_words_without_defining_provenance(
    tmp_path: Path,
) -> None:
    (tmp_path / "candidate.json").write_text(
        json.dumps({"result": {"summary": "Credential rotation was discussed."}}),
        encoding="utf-8",
    )
    (tmp_path / "raw.txt").write_text(
        "A credential-related response that contains no secret.", encoding="utf-8"
    )

    _scan_leakage(tmp_path, [])

    (tmp_path / "candidate.json").write_text(
        json.dumps({"credential": "forbidden provenance field"}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="forbidden provenance"):
        _scan_leakage(tmp_path, [])


def test_atomic_json_retries_windows_sharing_violation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "result.json"
    real_replace = os.replace
    calls = 0

    def sharing_violation_once(source: str, target: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            error = PermissionError("synthetic sharing violation")
            error.winerror = 32  # type: ignore[attr-defined]
            raise error
        real_replace(source, target)

    monkeypatch.setattr("bench.io.os.replace", sharing_violation_once)

    atomic_json(destination, {"status": "complete"})

    assert calls == 2
    assert json.loads(destination.read_text(encoding="utf-8")) == {"status": "complete"}


def config_data() -> dict[str, object]:
    return {
        "version": 1,
        "corpus_id": "synthetic-v1",
        "expected_conversations": 2,
        "expected_cases": 8,
        "tasks": [
            "conversation-summary",
            "work-mode-classification",
            "last-activity",
            "title-assessment",
        ],
        "task_catalog": "tasks.yaml",
        "model_catalog": "models.yaml",
        "paths": {
            "root": "private",
            "source": "inputs",
            "references": "references",
            "bundle": "bundle",
            "generation_work": "generation",
            "candidate_package": "package",
            "scoring": "scoring",
        },
        "candidate": {
            "id": "candidate",
            "profile": "local",
            "artifact_sha256": "0" * 64,
            "artifact_file": "model.gguf",
            "expected_provider": "synthetic",
            "expected_model": "candidate",
            "application_commit": "test-commit",
        },
        "judge": {"profile": "judge", "enabled": True},
    }


def test_config_is_strict_and_accounted() -> None:
    assert EvaluationConfig.model_validate(config_data()).expected_cases == 8
    bad = config_data()
    bad["unexpected"] = True
    with pytest.raises(ValidationError):
        EvaluationConfig.model_validate(bad)
    bad = config_data()
    bad["expected_cases"] = 7
    with pytest.raises(ValidationError, match="expected_cases"):
        EvaluationConfig.model_validate(bad)


def test_tracked_templates_pin_primary_judge_policy() -> None:
    repository = Path(__file__).parents[1]
    evaluation_data = yaml.safe_load(
        (repository / "bench" / "evaluation.default.yaml").read_text(encoding="utf-8")
    )
    config = EvaluationConfig.model_validate(evaluation_data)
    models = load_model_catalog(repository / "bench" / "ai-models.evaluation.default.yaml")
    profile = models.profiles[config.judge.profile]

    assert resolve_model(profile)["model"] == "vertex_ai/gemini-3.1-pro-preview"
    assert config.judge.rubric_version == "1"
    assert config.judge.temperature == 0
    assert config.judge.max_tokens == 1000
    assert profile.reasoning_effort == "none"


def test_deterministic_archive_is_path_independent(tmp_path: Path) -> None:
    hashes = []
    for name in ("one", "two"):
        root = tmp_path / name
        root.mkdir()
        (root / "payload.json").write_text('{"private":"synthetic"}\n', encoding="utf-8")
        write_checksums(root)
        verify_checksums(root)
        destination = tmp_path / f"{name}.zip"
        hashes.append(deterministic_zip(root, destination))
    assert hashes[0] == hashes[1]


@pytest.mark.parametrize("name", ["../escape", "/absolute", "C:/absolute"])
def test_safe_extract_rejects_untrusted_names(tmp_path: Path, name: str) -> None:
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr(name, json.dumps({"value": 1}))
    with pytest.raises(ValueError, match="unsafe"):
        safe_extract(archive, tmp_path / "out")


def test_checksum_tampering_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "value.txt").write_text("first", encoding="utf-8")
    write_checksums(tmp_path)
    (tmp_path / "value.txt").write_text("second", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        verify_checksums(tmp_path)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def synthetic_workspace(
    tmp_path: Path, conversation_count: int = 2
) -> tuple[EvaluationConfig, Path]:
    private = tmp_path / "private"
    tasks = Path(__file__).parents[1] / "ai-tasks.default.yaml"
    catalog_hash = hashlib.sha256(tasks.read_bytes()).hexdigest()
    models = tmp_path / "models.yaml"
    models.write_text(
        """version: 1
profiles:
  local:
    model: lm_studio/synthetic
    api_base: http://127.0.0.1:1234/v1
    remote: false
    timeout: 5
    retries: 0
    concurrency: 1
    structured_output: true
    context_window: 8192
    generation: {temperature: 0, max_tokens: 500}
  judge:
    model: gemini/gemini-2.5-flash
    remote: true
    timeout: 5
    retries: 0
    concurrency: 1
    structured_output: true
    generation: {temperature: 0, max_tokens: 500}
""",
        encoding="utf-8",
    )
    contracts = {
        "conversation-summary": ("conversation-summary-v1", "conversation-overview-v1"),
        "work-mode-classification": (
            "work-mode-classification-v1",
            "conversation-overview-v1",
        ),
        "last-activity": ("last-activity-v1", "recent-meaningful-v1"),
        "title-assessment": ("title-assessment-v1", "conversation-overview-v1"),
    }
    for index in range(1, conversation_count + 1):
        envelope = {
            "format_version": 1,
            "corpus_version": "synthetic-v1",
            "case_group_id": f"group-{index}",
            "selection_index": index,
            "source_conversation_id": index,
            "provider": "synthetic",
            "source_content_hash": f"source-{index}",
            "source_title": f"Synthetic title {index}",
            "start_date": "2026-01-01",
            "last_active_date": "2026-01-02",
            "created_at_utc": "2026-01-03T00:00:00Z",
            "snapshot_hash_reference": "snapshot",
            "task_catalog_hash_reference": catalog_hash,
        }
        for key, selector in (
            ("overview", "conversation-overview-v1"),
            ("recent", "recent-meaningful-v1"),
        ):
            envelope[key] = {
                "selector": selector,
                "selector_version": "1",
                "canonical_input_hash": "pending",
                "transcript": f"Synthetic selected content {index} {key}.",
                "selected_message_ids": [index * 10],
                "selection_metadata": {"synthetic": True},
            }
            hash_value = {
                "selector": selector,
                "selector_version": "1",
                "selected_message_ids": [index * 10],
                "transcript": f"Synthetic selected content {index} {key}.",
            }
            if key == "overview":
                hash_value.update(
                    source_title=f"Synthetic title {index}",
                    start_date="2026-01-01",
                    last_active_date="2026-01-02",
                )
            envelope[key]["canonical_input_hash"] = canonical_hash(hash_value)
        write_json(private / "inputs" / f"c{index:03d}.json", envelope)
        outputs = synthetic_outputs(index)
        for task, (schema, selector) in contracts.items():
            selector_key = "recent" if task == "last-activity" else "overview"
            write_json(
                private / "references" / task / f"c{index:03d}.json",
                {
                    "format_version": 1,
                    "corpus_version": "synthetic-v1",
                    "run_id": "synthetic",
                    "case_id": f"case-{index}-{task}",
                    "case_group_id": f"group-{index}",
                    "source_conversation_id": index,
                    "provider": "synthetic",
                    "task_name": task,
                    "task_version": "1",
                    "output_schema": schema,
                    "provider_schema_version": "1",
                    "finalizer_version": (
                        "2" if task in {"conversation-summary", "last-activity"} else "1"
                    ),
                    "input_selector": selector,
                    "selector_version": "1",
                    "input_hash": envelope[selector_key]["canonical_input_hash"],
                    "task_catalog_hash": catalog_hash,
                    "teacher_alias": "teacher",
                    "teacher_model": "teacher-model",
                    "teacher_session_id": "session",
                    "status": "success",
                    "output": outputs[task],
                    "failure": None,
                    "created_at_utc": "2026-01-03T00:00:00Z",
                    "validated_at_utc": "2026-01-03T00:00:00Z",
                },
            )
    data = config_data()
    data["expected_conversations"] = conversation_count
    data["expected_cases"] = conversation_count * 4
    data["task_catalog"] = str(tasks)
    data["model_catalog"] = str(models)
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"synthetic-model-artifact")
    data["candidate"] = {
        **data["candidate"],
        "artifact_path": str(artifact),
        "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "artifact_size": artifact.stat().st_size,
    }
    data["paths"] = {
        "root": str(private),
        "source": "inputs",
        "references": "references",
        "bundle": "work/bundle",
        "generation_work": "work/generation",
        "candidate_package": "work/package-one",
        "scoring": "runs/run-one",
    }
    return EvaluationConfig.model_validate(data), tmp_path / "evaluation.yaml"


def with_selection_manifest(
    config: EvaluationConfig,
    config_path: Path,
    indexes: list[int],
    *,
    role: str = "development",
    configured_role: str | None = None,
    name: str = "selection.json",
) -> tuple[EvaluationConfig, Path, dict[str, object]]:
    inputs = load_inputs(
        Path(config.paths.root) / config.paths.source, config.expected_conversations
    )
    by_index = {item.selection_index: item for item in inputs}
    entries = [
        {
            "authority_index": index,
            "conversation_identity": _conversation_identity(by_index[index]),
            "provider": by_index[index].provider,
            "length_stratum": "short" if ordinal % 2 else "long",
            "date_bin": f"bin-{ordinal % 2}",
        }
        for ordinal, index in enumerate(indexes, 1)
    ]
    value: dict[str, object] = {
        "format_version": 1,
        "algorithm_version": "synthetic-selection-v1",
        "role": role,
        "source_selection_identity": _source_selection_identity(config, inputs),
        "ordered_conversations": entries,
        "conversation_count": len(entries),
        "expected_case_count": len(entries) * 4,
        "provider_counts": dict(Counter(item["provider"] for item in entries)),
        "length_stratum_counts": dict(
            Counter(item["length_stratum"] for item in entries)
        ),
        "date_bin_counts": dict(Counter(item["date_bin"] for item in entries)),
        "created_at_utc": "2026-08-03T00:00:00Z",
        "manifest_sha256": "0" * 64,
    }
    provisional = SelectionManifest.model_validate(value)
    value["manifest_sha256"] = digest(_manifest_payload(provisional))
    path = config_path.parent / name
    write_json(path, value)
    data = config.model_dump(mode="json")
    data["candidate"]["artifact_path"] = config.candidate.artifact_path
    data["selection_manifest"] = {
        "path": name,
        "role": configured_role or role,
        "sha256": value["manifest_sha256"],
        "source_selection_identity": value["source_selection_identity"],
        "expected_conversations": len(entries),
        "expected_cases": len(entries) * 4,
    }
    return EvaluationConfig.model_validate(data), path, value


def rewrite_selection_manifest(
    config: EvaluationConfig,
    path: Path,
    value: dict[str, object],
) -> EvaluationConfig:
    provisional = SelectionManifest.model_validate({**value, "manifest_sha256": "0" * 64})
    value["manifest_sha256"] = digest(_manifest_payload(provisional))
    write_json(path, value)
    data = config.model_dump(mode="json")
    data["candidate"]["artifact_path"] = config.candidate.artifact_path
    data["selection_manifest"]["sha256"] = value["manifest_sha256"]
    return EvaluationConfig.model_validate(data)


def synthetic_outputs(index: int) -> dict[str, dict[str, object]]:
    evidence = [index * 10]
    return {
        "conversation-summary": {
            "summary": "Synthetic work began. Synthetic work completed.",
            "start_date": "2026-01-01",
            "last_active_date": "2026-01-02",
            "evidence_message_ids": evidence,
        },
        "work-mode-classification": {
            "mode": "executor",
            "confidence": 1,
            "reason": "Concrete implementation work dominated.",
            "evidence_message_ids": evidence,
        },
        "last-activity": {
            "recent_work": "Synthetic work completed.",
            "status": "completed",
            "blockers": [],
            "next_action": None,
            "next_action_basis": "unknown",
            "evidence_message_ids": evidence,
        },
        "title-assessment": {
            "title_fits": True,
            "confidence": 1,
            "reason": "The title is specific and accurate.",
            "suggested_title": None,
            "evidence_message_ids": evidence,
        },
    }


def with_run_paths(config: EvaluationConfig, label: str) -> EvaluationConfig:
    paths = config.paths.model_copy(
        update={
            "bundle": f"work/bundle-{label}",
            "generation_work": f"work/generation-{label}",
            "candidate_package": f"work/package-{label}",
            "scoring": f"runs/{label}",
        }
    )
    return config.model_copy(update={"paths": paths})


def with_active_prompt_catalog(
    config: EvaluationConfig,
    config_path: Path,
    label: str,
    mutate,
) -> tuple[EvaluationConfig, Path]:
    authority_path = Path(config.task_catalog)
    if not authority_path.is_absolute():
        authority_path = (config_path.parent / authority_path).resolve()
    active_path = config_path.parent / f"tasks-{label}.yaml"
    active_data = yaml.safe_load(authority_path.read_text(encoding="utf-8"))
    mutate(active_data)
    active_path.write_text(yaml.safe_dump(active_data, sort_keys=False), encoding="utf-8")
    data = config.model_dump(mode="json")
    data["candidate"]["artifact_path"] = config.candidate.artifact_path
    data["task_catalog"] = str(active_path)
    data["task_catalog_authority"] = {
        "path": str(authority_path),
        "sha256": hashlib.sha256(authority_path.read_bytes()).hexdigest(),
        "active_sha256": hashlib.sha256(active_path.read_bytes()).hexdigest(),
        "allowed_changes": "prompts-only",
    }
    return EvaluationConfig.model_validate(data), active_path


def hosted_workspace(
    tmp_path: Path, conversation_count: int = 2
) -> tuple[EvaluationConfig, Path]:
    local, config_path = synthetic_workspace(tmp_path, conversation_count=conversation_count)
    models_path = Path(local.model_catalog)
    model_data = yaml.safe_load(models_path.read_text(encoding="utf-8"))
    model_data["profiles"]["hosted"] = {
        **model_data["profiles"]["local"],
        "model": "vertex_ai/synthetic-candidate",
        "api_base": None,
        "remote": True,
    }
    models_path.write_text(yaml.safe_dump(model_data, sort_keys=False), encoding="utf-8")
    hosted = local.candidate.model_copy(
        update={
            "execution": "hosted-api",
            "profile": "hosted",
            "artifact_sha256": None,
            "artifact_file": None,
            "quantization": None,
            "runtime": None,
            "artifact_repository": None,
            "artifact_size": None,
            "runtime_version": None,
            "execution_device": None,
            "artifact_path": None,
        }
    )
    return local.model_copy(update={"candidate": hosted}), config_path


def test_candidate_provenance_is_strictly_local_or_hosted(tmp_path: Path) -> None:
    hosted, _ = hosted_workspace(tmp_path)
    assert hosted.candidate.execution == "hosted-api"
    assert hosted.candidate.artifact_sha256 is None
    mixed = hosted.candidate.model_dump(mode="json")
    mixed["artifact_file"] = "fake.gguf"
    with pytest.raises(ValidationError, match="hosted-api candidate forbids"):
        type(hosted.candidate).model_validate(mixed)


def test_hosted_generation_requires_both_authorization_flags(tmp_path: Path) -> None:
    hosted, config_path = hosted_workspace(tmp_path)
    client = SyntheticClient()
    for allow_remote, confirm_private_eval in ((False, False), (True, False), (False, True)):
        with pytest.raises(ValueError, match="hosted candidate generation requires"):
            asyncio.run(
                generate(
                    tmp_path / "not-read.zip",
                    hosted,
                    config_path,
                    client=client,
                    allow_remote=allow_remote,
                    confirm_private_eval=confirm_private_eval,
                )
            )
    assert client.calls == 0


def test_hosted_candidate_packages_without_fake_local_provenance(tmp_path: Path) -> None:
    hosted, config_path = hosted_workspace(tmp_path)
    models_path = Path(hosted.model_catalog)
    model_data = yaml.safe_load(models_path.read_text(encoding="utf-8"))
    model_data["profiles"]["hosted"]["reasoning_effort"] = "none"
    models_path.write_text(yaml.safe_dump(model_data, sort_keys=False), encoding="utf-8")
    prepared = prepare(hosted, config_path)
    client = SyntheticClient()
    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            hosted,
            config_path,
            client=client,
            implementation_probe=clean_test_identity,
            allow_remote=True,
            confirm_private_eval=True,
        )
    )
    package = tmp_path / "private" / "work" / "package-one"
    manifest = json.loads((package / "candidate-manifest.json").read_text(encoding="utf-8"))
    assert manifest["candidate"]["execution"] == "hosted-api"
    assert manifest["candidate"]["artifact_sha256"] is None
    assert manifest["api_base_class"] == "hosted-provider"
    assert manifest["runtime"]["kind"] == "hosted-api"
    assert manifest["runtime"]["litellm_version"]
    assert {request.reasoning_effort for request in client.requests} == {"none"}
    assert verify(Path(generated["archive"]), hosted, config_path)["valid"] is True


@pytest.mark.skipif(
    os.environ.get("CHRONICLE_RUN_VERTEX_SYNTHETIC_GATE") != "1",
    reason="explicit opt-in required for synthetic Vertex provider calls",
)
def test_vertex_hosted_candidate_and_pro_judge_synthetic_gate(tmp_path: Path) -> None:
    hosted, config_path = hosted_workspace(tmp_path, conversation_count=1)
    models_path = Path(hosted.model_catalog)
    model_data = yaml.safe_load(models_path.read_text(encoding="utf-8"))
    model_data["profiles"]["hosted"].update(
        model="vertex_ai/gemini-3.5-flash",
        reasoning_effort="none",
        timeout=180,
    )
    model_data["profiles"]["judge"].update(
        model="vertex_ai/gemini-3.1-pro-preview",
        reasoning_effort="none",
        timeout=180,
    )
    models_path.write_text(yaml.safe_dump(model_data, sort_keys=False), encoding="utf-8")
    candidate = hosted.candidate.model_copy(
        update={"expected_provider": "vertex_ai", "expected_model": "gemini-3.5-flash"}
    )
    hosted = hosted.model_copy(update={"candidate": candidate})
    prepared = prepare(hosted, config_path)
    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            hosted,
            config_path,
            implementation_probe=clean_test_identity,
            allow_remote=True,
            confirm_private_eval=True,
        )
    )
    package = Path(generated["archive"])
    candidate_gate = verify(package, hosted, config_path)
    assert candidate_gate["expected"] == 4
    assert candidate_gate["success"] + candidate_gate["failed"] == 4

    judge_candidate = hosted.candidate.model_copy(
        update={"expected_provider": "synthetic", "expected_model": "candidate"}
    )
    judge_config = with_run_paths(
        hosted.model_copy(update={"candidate": judge_candidate}), "vertex-judge-gate"
    )
    judge_prepared = prepare(judge_config, config_path)
    judge_generated = asyncio.run(
        generate(
            Path(judge_prepared["archive"]),
            judge_config,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
            allow_remote=True,
            confirm_private_eval=True,
        )
    )
    judge_package = Path(judge_generated["archive"])
    assert verify(judge_package, judge_config, config_path)["success"] == 4
    score(judge_package, judge_config, config_path)
    judged = asyncio.run(score_with_judge(judge_package, judge_config, config_path))
    assert judged["completed"] == 4
    cached = asyncio.run(
        score_with_judge(
            judge_package,
            judge_config,
            config_path,
            client=NoCallJudge(),
            cache_only=True,
        )
    )
    assert cached == judged


class SyntheticClient:
    def __init__(self, *, invalid_once: bool = False) -> None:
        self.calls = 0
        self.invalid_once = invalid_once
        self.requests = []

    async def complete(self, request):
        self.calls += 1
        self.requests.append(request)
        properties = request.response_schema["properties"]
        evidence = properties["evidence_message_ids"]["items"]["enum"][0]
        if self.invalid_once and "recent_work" in properties:
            self.invalid_once = False
            return CompletionResponse("not-json", "synthetic", "candidate")
        if "summary" in properties:
            value = {
                "summary": ["Synthetic work began.", "Synthetic work completed."],
                "evidence_message_ids": [evidence],
            }
        elif "mode" in properties:
            value = {
                "mode": "executor",
                "confidence": 1,
                "reason": "Concrete implementation work dominated.",
                "evidence_message_ids": [evidence],
            }
        elif "recent_work" in properties:
            value = {
                "recent_work": "Synthetic work completed.",
                "status": "completed",
                "blockers": [],
                "next_action": None,
                "evidence_message_ids": [evidence],
            }
        else:
            value = {
                "title_fits": True,
                "confidence": 1,
                "reason": "The title is specific and accurate.",
                "suggested_title": None,
                "evidence_message_ids": [evidence],
            }
        return CompletionResponse(json.dumps(value), "synthetic", "candidate", {"total_tokens": 10})


class InvalidLastActivityClient(SyntheticClient):
    async def complete(self, request):
        if "recent_work" in request.response_schema["properties"]:
            self.calls += 1
            return CompletionResponse("not-json", "synthetic", "candidate")
        return await super().complete(request)


class SyntheticJudge:
    def __init__(self) -> None:
        self.calls = 0

    async def complete(self, request):
        self.calls += 1
        prompt = json.loads(request.messages[1]["content"])
        assert "candidate_model" not in prompt
        assert "lm_studio" not in request.messages[1]["content"]
        value = {
            "case_alias": prompt["case_alias"],
            "case_fingerprint": prompt["case_fingerprint"],
            "task": prompt["task"],
            "status": "success",
            "scores": {name: 4 for name in prompt["rubric"]["dimensions"]},
            "rationale": "The result is supported and useful.",
            "evidence_message_ids": prompt["allowed_evidence_message_ids"][:1],
            "unsupported_claim_count": 0,
        }
        return CompletionResponse(json.dumps(value), "gemini", "gemini-2.5-flash")


def clean_test_identity() -> ImplementationIdentity:
    return ImplementationIdentity("test-commit", False, None)


def successful_package(tmp_path: Path) -> tuple[EvaluationConfig, Path, Path]:
    config, config_path = synthetic_workspace(tmp_path)
    prepared = prepare(config, config_path)
    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
        )
    )
    score(Path(generated["archive"]), config, config_path)
    return config, config_path, Path(generated["archive"])


class InterruptOnceClient(SyntheticClient):
    async def complete(self, request):
        if self.calls == 0:
            self.calls += 1
            raise RuntimeError("synthetic interruption")
        return await super().complete(request)


class WrongIdentityClient(SyntheticClient):
    def __init__(self, *, wrong_after: int = 0) -> None:
        super().__init__()
        self.wrong_after = wrong_after

    async def complete(self, request):
        response = await super().complete(request)
        if self.calls > self.wrong_after:
            return CompletionResponse(response.content, "unexpected", "wrong-model")
        return response


class TransportFailureClient:
    def __init__(self) -> None:
        self.calls = 0

    async def complete(self, request):
        self.calls += 1
        raise LLMError("timeout", "provider-controlled private text")


class JudgeFailureClient:
    def __init__(self, failure: str) -> None:
        self.failure = failure
        self.calls = 0

    async def complete(self, request):
        self.calls += 1
        if self.failure == "provider":
            raise LLMError("timeout", "provider-controlled private text")
        if self.failure == "schema":
            return CompletionResponse("{}", "gemini", "gemini-2.5-flash")
        raise RuntimeError("programming defect")


class InvalidJsonMetadataJudge(SyntheticJudge):
    async def complete(self, request):
        self.calls += 1
        return CompletionResponse(
            "PRIVATE-MARKER-not-json",
            "gemini",
            "gemini-2.5-flash",
            {
                "prompt_tokens": 20,
                "completion_tokens": 500,
                "completion_tokens_details": {"reasoning_tokens": 450},
                "private_value": "PRIVATE-MARKER",
            },
            finish_reason="length",
        )


class NoCallJudge:
    def __init__(self) -> None:
        self.calls = 0

    async def complete(self, request):
        self.calls += 1
        raise AssertionError("provider call forbidden")


def _schema_keywords(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _schema_keywords(child)
    elif isinstance(value, list):
        for child in value:
            yield from _schema_keywords(child)


@pytest.mark.parametrize("task", RUBRICS)
def test_vertex_provider_judge_schema_is_exact_and_deterministic(task: str) -> None:
    schema = provider_judge_schema(task)
    assert schema == provider_judge_schema(task)
    assert schema["required"] == list(schema["properties"])
    scores = schema["properties"]["scores"]
    assert tuple(scores["properties"]) == RUBRICS[task]
    assert scores["required"] == list(RUBRICS[task])
    assert scores["additionalProperties"] is False
    allowed = {
        "type",
        "properties",
        "required",
        "additionalProperties",
        "enum",
        "items",
        "minimum",
        "maximum",
        "maxLength",
        "description",
        *schema["properties"],
        *RUBRICS[task],
    }
    assert set(_schema_keywords(schema)) <= allowed
    assert not ({"const", "default", "minLength"} & set(_schema_keywords(schema)))
    rationale = schema["properties"]["rationale"]
    assert rationale["maxLength"] == JUDGE_RATIONALE_MAX_LENGTH
    assert "concise" in rationale["description"]
    assert "no chain-of-thought" in rationale["description"]


def test_judge_rationale_bound_is_authoritative_and_never_repaired() -> None:
    base = {
        "case_alias": "synthetic",
        "case_fingerprint": "fingerprint",
        "task": "conversation-summary",
        "status": "success",
        "scores": {name: 4 for name in RUBRICS["conversation-summary"]},
        "evidence_message_ids": [1],
        "unsupported_claim_count": 0,
    }
    accepted = JudgeResult.model_validate(
        {**base, "rationale": "x" * JUDGE_RATIONALE_MAX_LENGTH}
    )
    assert len(accepted.rationale) == JUDGE_RATIONALE_MAX_LENGTH
    with pytest.raises(ValidationError, match="string_too_long"):
        JudgeResult.model_validate(
            {**base, "rationale": "x" * (JUDGE_RATIONALE_MAX_LENGTH + 1)}
        )


def test_six_eligible_two_invalid_judge_accounting(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    prepared = prepare(config, config_path)
    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=InvalidLastActivityClient(),
            implementation_probe=clean_test_identity,
        )
    )
    package = Path(generated["archive"])
    score(package, config, config_path)
    client = SyntheticJudge()
    metrics = asyncio.run(score_with_judge(package, config, config_path, client=client))
    assert metrics["eligible"] == 6
    assert metrics["completed"] == 6
    assert metrics["failed"] == 0
    assert metrics["skipped_invalid"] == 2
    assert client.calls == 6
    assert metrics["dimension_means"]
    resumed = asyncio.run(score_with_judge(package, config, config_path, client=client))
    assert resumed == metrics
    assert client.calls == 6


def test_synthetic_cross_stage_and_append_only_retry(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    assert len(build_authority(config, config_path)) == 8
    prepared = prepare(config, config_path)
    client = SyntheticClient(invalid_once=True)
    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=client,
            implementation_probe=clean_test_identity,
        )
    )
    first_package = tmp_path / "returned" / "candidate.zip"
    first_package.parent.mkdir()
    shutil.copy2(Path(generated["archive"]), first_package)
    assert verify(first_package, config, config_path)["failed"] == 1
    metrics = score(first_package, config, config_path)
    assert metrics["runtime_reliability"]["expected"] == 8
    assert metrics["deterministic_contract"]["no_valid_output"] == 1
    matrices = metrics["deterministic_contract"]["matrices"]
    assert sum(sum(row.values()) for row in matrices["work_mode"].values()) == 2
    assert sum(sum(row.values()) for row in matrices["last_activity"].values()) == 2
    assert sum(sum(row.values()) for row in matrices["title_fit"].values()) == 2
    judge = SyntheticJudge()
    judge_metrics = asyncio.run(score_with_judge(first_package, config, config_path, client=judge))
    assert judge_metrics["completed"] == 7
    assert judge_metrics["skipped_invalid"] == 1
    assert judge.calls == 7
    asyncio.run(score_with_judge(first_package, config, config_path, client=judge))
    assert judge.calls == 7
    changed_judge = config.judge.model_copy(update={"rubric_version": "2"})
    changed = config.model_copy(update={"judge": changed_judge})
    asyncio.run(score_with_judge(first_package, changed, config_path, client=judge))
    assert judge.calls == 14
    second_paths = config.paths.model_copy(
        update={"candidate_package": "work/package-two", "scoring": "runs/run-two"}
    )
    second = config.model_copy(update={"paths": second_paths})
    asyncio.run(
        generate(
            Path(prepared["archive"]),
            second,
            config_path,
            client=client,
            retry_failures=True,
            implementation_probe=clean_test_identity,
        )
    )
    attempts = sorted(
        (tmp_path / "private" / "work" / "generation" / "results").rglob("attempts/*.json")
    )
    assert len(attempts) == 9
    assert any(path.name == "0002.json" for path in attempts)
    retried_package = tmp_path / "private" / "work" / "package-two.zip"
    retried_verification = verify(retried_package, second, config_path)
    assert retried_verification["success"] == 8
    retried_metrics = score(retried_package, second, config_path)
    assert retried_metrics["runtime_reliability"]["valid"] == 8
    retried_judge = SyntheticJudge()
    retried_judge_metrics = asyncio.run(
        score_with_judge(retried_package, second, config_path, client=retried_judge)
    )
    assert retried_judge_metrics["completed"] == 8
    assert retried_judge_metrics["skipped_invalid"] == 0
    assert retried_judge.calls == 8

    legacy_package = tmp_path / "private" / "work" / "package-legacy"
    shutil.copytree(tmp_path / "private" / "work" / "package-two", legacy_package)
    baseline_success = 0
    for index_path in legacy_package.glob("results/*/index.json"):
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index.pop("current_attempt")
        write_json(index_path, index)
        baseline_path = index_path.parent / "attempts" / "0001.json"
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        baseline_success += baseline["status"] == "success"
    legacy_manifest_path = legacy_package / "candidate-manifest.json"
    legacy_manifest = json.loads(legacy_manifest_path.read_text(encoding="utf-8"))
    legacy_manifest["success"] = baseline_success
    legacy_manifest["failed"] = legacy_manifest["completed"] - baseline_success
    write_json(legacy_manifest_path, legacy_manifest)
    write_json(
        legacy_package / "case-accounting.json",
        {
            key: legacy_manifest[key]
            for key in ("expected", "completed", "success", "failed", "total_attempts")
        },
    )
    write_json(
        legacy_package / "generation-summary.json",
        {
            "success": baseline_success,
            "failed": 8 - baseline_success,
            "failure_boundaries": {"invalid_json": 1},
        },
    )
    write_checksums(legacy_package)
    legacy_paths = second.paths.model_copy(update={"scoring": "runs/run-legacy"})
    legacy_config = second.model_copy(update={"paths": legacy_paths})
    legacy_verification = verify(legacy_package, legacy_config, config_path)
    assert legacy_verification["success"] == 7
    assert score(legacy_package, legacy_config, config_path)["runtime_reliability"]["valid"] == 7

    invalid_package = tmp_path / "private" / "work" / "package-invalid-current"
    shutil.copytree(tmp_path / "private" / "work" / "package-two", invalid_package)
    invalid_index_path = next(invalid_package.glob("results/*/index.json"))
    invalid_index = json.loads(invalid_index_path.read_text(encoding="utf-8"))
    invalid_index["current_attempt"] = "not-an-attempt"
    write_json(invalid_index_path, invalid_index)
    write_checksums(invalid_package)
    with pytest.raises(ValueError, match="current pointer is invalid"):
        verify(invalid_package, second, config_path)

    package_dir = tmp_path / "private" / "work" / "package-one"
    attempt_path = next(package_dir.glob("results/*/attempts/0001.json"))
    original_attempt = attempt_path.read_text(encoding="utf-8")
    tampered = json.loads(original_attempt)
    if tampered.get("result") and "confidence" in tampered["result"]:
        tampered["result"]["confidence"] = 2
    else:
        tampered["case_fingerprint"] = "wrong"
    write_json(attempt_path, tampered)
    write_checksums(package_dir)
    with pytest.raises((ValueError, ValidationError)):
        verify(package_dir, config, config_path)
    attempt_path.write_text(original_attempt, encoding="utf-8")
    write_checksums(package_dir)
    (package_dir / "unexpected.txt").write_text("synthetic", encoding="utf-8")
    write_checksums(package_dir)
    with pytest.raises(ValueError, match="unexpected"):
        verify(package_dir, config, config_path)


def test_one_conversation_frozen_prefix_cross_stage(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    scoped = with_run_paths(config, "one")
    prepared = prepare(scoped, config_path, conversation_limit=1)
    assert prepared["conversations"] == 1
    assert prepared["cases"] == 4
    with zipfile.ZipFile(prepared["archive"]) as archive:
        manifest = json.loads(archive.read("bundle-manifest.json"))
    assert manifest["scope"]["requested_conversation_limit"] == 1
    assert manifest["scope"]["effective_conversation_count"] == 1
    assert [item["alias"].split("--", 1)[0] for item in manifest["cases"]] == [
        "c001"
    ] * 4
    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            scoped,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
        )
    )
    package = Path(generated["archive"])
    checked = verify(package, scoped, config_path)
    assert checked["expected"] == 4
    assert checked["scope"]["effective_conversation_count"] == 1
    metrics = score(package, scoped, config_path)
    assert metrics["runtime_reliability"]["expected"] == 4
    for matrix in metrics["deterministic_contract"]["matrices"].values():
        assert sum(sum(row.values()) for row in matrix.values()) == 1
    judge = SyntheticJudge()
    judged = asyncio.run(score_with_judge(package, scoped, config_path, client=judge))
    assert judged["eligible"] == 4
    assert judged["completed"] == 4
    assert judge.calls == 4
    assert len(list((tmp_path / "private" / "inputs").glob("*.json"))) == 3
    assert all(
        len(list((tmp_path / "private" / "references" / task).glob("*.json"))) == 3
        for task in scoped.tasks
    )


def test_intermediate_full_and_unlimited_frozen_prefix_scopes(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    intermediate = prepare(with_run_paths(config, "two"), config_path, conversation_limit=2)
    explicit_full = prepare(with_run_paths(config, "three"), config_path, conversation_limit=3)
    unlimited = prepare(with_run_paths(config, "all"), config_path)
    assert (intermediate["conversations"], intermediate["cases"]) == (2, 8)
    assert (explicit_full["conversations"], explicit_full["cases"]) == (3, 12)
    assert (unlimited["conversations"], unlimited["cases"]) == (3, 12)
    with zipfile.ZipFile(explicit_full["archive"]) as archive:
        explicit_scope = json.loads(archive.read("bundle-manifest.json"))["scope"]
    with zipfile.ZipFile(unlimited["archive"]) as archive:
        unlimited_scope = json.loads(archive.read("bundle-manifest.json"))["scope"]
    assert explicit_scope["requested_conversation_limit"] == 3
    assert unlimited_scope["requested_conversation_limit"] is None
    assert (
        explicit_scope["frozen_prefix_identity"]
        == unlimited_scope["frozen_prefix_identity"]
    )


def test_non_prefix_ordered_selection_cross_stage_and_judge_scope(tmp_path: Path) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=4)
    selected, _, manifest_value = with_selection_manifest(base, config_path, [3, 1])
    config = with_run_paths(selected, "ordered")
    for unselected_index in (2, 4):
        (tmp_path / "private" / "inputs" / f"c{unselected_index:03d}.json").write_text(
            "unselected input must remain unopened", encoding="utf-8"
        )
        for task in config.tasks:
            (
                tmp_path
                / "private"
                / "references"
                / task
                / f"c{unselected_index:03d}.json"
            ).write_text("unselected reference must remain unopened", encoding="utf-8")

    authority = build_authority(config, config_path)
    assert [case.alias.split("--", 1)[0] for case in authority] == ["c003"] * 4 + [
        "c001"
    ] * 4
    prepared = prepare(config, config_path)
    assert (prepared["conversations"], prepared["cases"], prepared["scope"]) == (
        2,
        8,
        "ordered-manifest-v1",
    )
    with zipfile.ZipFile(prepared["archive"]) as archive:
        bundle_manifest = json.loads(archive.read("bundle-manifest.json"))
    scope = bundle_manifest["scope"]
    assert scope["selection_manifest_role"] == "development"
    assert scope["selection_manifest_identity"] == manifest_value["manifest_sha256"]
    assert "selection.json" not in json.dumps(scope)
    assert str(config_path.parent) not in json.dumps(scope)

    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
        )
    )
    package = Path(generated["archive"])
    checked = verify(package, config, config_path)
    assert checked["expected"] == 8
    assert checked["scope"] == scope
    metrics = score(package, config, config_path)
    assert metrics["runtime_reliability"]["expected"] == 8
    judge = SyntheticJudge()
    judged = asyncio.run(score_with_judge(package, config, config_path, client=judge))
    assert (judged["eligible"], judged["completed"], judge.calls) == (8, 8, 8)


def test_prompt_only_catalog_cross_stage_and_selected_reference_authority(
    tmp_path: Path,
) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=4)
    selected, _, _ = with_selection_manifest(base, config_path, [3, 1])

    def mutate(data) -> None:
        for task in data["tasks"].values():
            task["system_prompt"] += "\nReturn the synthetic result concisely."
            task["user_prompt"] += "\nSynthetic prompt-only experiment."

    experimental, _ = with_active_prompt_catalog(selected, config_path, "cross-stage", mutate)
    config = with_run_paths(experimental, "prompt-cross-stage")
    authority_hash = config.task_catalog_authority.sha256
    for index in (1, 3):
        source = json.loads(
            (tmp_path / "private" / "inputs" / f"c{index:03d}.json").read_text(
                encoding="utf-8"
            )
        )
        assert source["task_catalog_hash_reference"] == authority_hash
        for task in config.tasks:
            reference = json.loads(
                (
                    tmp_path
                    / "private"
                    / "references"
                    / task
                    / f"c{index:03d}.json"
                ).read_text(encoding="utf-8")
            )
            assert reference["task_catalog_hash"] == authority_hash
    for unselected in (2, 4):
        (tmp_path / "private" / "inputs" / f"c{unselected:03d}.json").write_text(
            "unselected input must remain unopened", encoding="utf-8"
        )
        for task in config.tasks:
            (
                tmp_path
                / "private"
                / "references"
                / task
                / f"c{unselected:03d}.json"
            ).write_text("unselected reference must remain unopened", encoding="utf-8")

    prepared = prepare(config, config_path)
    with zipfile.ZipFile(prepared["archive"]) as archive:
        bundle_manifest = json.loads(archive.read("bundle-manifest.json"))
        first_case = json.loads(archive.read("cases/c003--conversation-summary.json"))
    identity = bundle_manifest["task_catalog_experiment"]
    assert identity["authority_catalog_sha256"] == authority_hash
    assert identity["active_catalog_sha256"] == config.task_catalog_authority.active_sha256
    assert identity["policy"] == "prompts-only"
    assert identity["policy_version"] == "1"
    assert set(identity["active_prompt_identities"]) == set(config.tasks)
    assert first_case["contract_hashes"]["task_catalog_authority"] == authority_hash
    assert first_case["contract_hashes"]["task_catalog_active"] == identity[
        "active_catalog_sha256"
    ]
    assert "tasks-cross-stage.yaml" not in json.dumps(bundle_manifest)
    assert str(tmp_path) not in json.dumps(bundle_manifest)

    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
        )
    )
    package = Path(generated["archive"])
    work_manifest = json.loads(
        (
            tmp_path
            / "private"
            / "work"
            / "generation-prompt-cross-stage"
            / "work-manifest.json"
        ).read_text(encoding="utf-8")
    )
    assert work_manifest["task_catalog_experiment"] == identity
    with zipfile.ZipFile(package) as archive:
        candidate_manifest = json.loads(archive.read("candidate-manifest.json"))
    assert candidate_manifest["task_catalog_experiment"] == identity
    checked = verify(package, config, config_path)
    assert checked["task_catalog_experiment"] == identity
    metrics = score(package, config, config_path)
    assert metrics["task_catalog_experiment"] == identity
    scoring_root = tmp_path / "private" / "runs" / "prompt-cross-stage"
    run_manifest = json.loads(
        (scoring_root / "run-manifest.json").read_text(encoding="utf-8")
    )
    assert run_manifest["task_catalog_experiment"] == identity
    judge = SyntheticJudge()
    judged = asyncio.run(score_with_judge(package, config, config_path, client=judge))
    assert judged["task_catalog_experiment"] == identity
    judge_metrics = json.loads(
        (scoring_root / "judge" / "metrics.json").read_text(encoding="utf-8")
    )
    assert judge_metrics["task_catalog_experiment"] == identity
    assert (judged["eligible"], judged["completed"], judge.calls) == (8, 8, 8)


@pytest.mark.parametrize("prompt_field", ["system_prompt", "user_prompt"])
def test_single_prompt_field_change_is_accepted(
    tmp_path: Path, prompt_field: str
) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=1)

    def mutate(data) -> None:
        data["tasks"]["conversation-summary"][prompt_field] += "\nSynthetic-only change."

    experimental, _ = with_active_prompt_catalog(base, config_path, prompt_field, mutate)
    prepared = prepare(with_run_paths(experimental, prompt_field), config_path)
    assert prepared["cases"] == 4


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("version", "2"),
        ("input_selector", "recent-meaningful-v1"),
        ("output_schema", "work-mode-classification-v1"),
        ("generation", {"temperature": 0, "max_tokens": 351}),
        ("model_profile", "different-profile"),
        ("max_input_chars", 49999),
        ("recent_message_count", 19),
        ("enabled", False),
        ("depends_on", ["title-assessment"]),
        ("description", "Changed synthetic description."),
    ],
)
def test_prompt_experiment_rejects_non_prompt_changes(
    tmp_path: Path, field: str, value: object
) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=1)

    def mutate(data) -> None:
        data["tasks"]["conversation-summary"][field] = value

    experimental, _ = with_active_prompt_catalog(base, config_path, field, mutate)
    with pytest.raises(AIConfigError, match="non-prompt field"):
        prepare(with_run_paths(experimental, field), config_path)


@pytest.mark.parametrize("catalog", ["authority", "active"])
def test_prompt_experiment_rejects_wrong_configured_hash(
    tmp_path: Path, catalog: str
) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=1)

    def mutate(data) -> None:
        data["tasks"]["conversation-summary"]["system_prompt"] += "\nSynthetic change."

    experimental, _ = with_active_prompt_catalog(base, config_path, catalog, mutate)
    declaration = experimental.task_catalog_authority
    update = {"sha256" if catalog == "authority" else "active_sha256": "f" * 64}
    changed = experimental.model_copy(
        update={"task_catalog_authority": declaration.model_copy(update=update)}
    )
    with pytest.raises(AIConfigError, match=f"{catalog}.*hash mismatch"):
        prepare(with_run_paths(changed, f"wrong-{catalog}"), config_path)


def test_active_catalog_change_after_generation_is_rejected_by_verification(
    tmp_path: Path,
) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=1)

    def mutate(data) -> None:
        data["tasks"]["conversation-summary"]["system_prompt"] += "\nSynthetic change."

    experimental, active_path = with_active_prompt_catalog(base, config_path, "immutable", mutate)
    config = with_run_paths(experimental, "immutable")
    prepared = prepare(config, config_path)
    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
        )
    )
    active_path.write_text(
        active_path.read_text(encoding="utf-8") + "\n# byte-level tamper\n",
        encoding="utf-8",
    )
    with pytest.raises(AIConfigError, match="active prompt catalog file hash mismatch"):
        verify(Path(generated["archive"]), config, config_path)


def test_prompt_catalog_package_identity_tampering_is_rejected(tmp_path: Path) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=1)

    def mutate(data) -> None:
        data["tasks"]["conversation-summary"]["system_prompt"] += "\nSynthetic change."

    experimental, _ = with_active_prompt_catalog(base, config_path, "tamper", mutate)
    config = with_run_paths(experimental, "prompt-tamper")
    prepared = prepare(config, config_path)
    asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
        )
    )
    package = tmp_path / "private" / "work" / "package-prompt-tamper"
    manifest_path = package / "candidate-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["task_catalog_experiment"]["active_catalog_sha256"] = "e" * 64
    write_json(manifest_path, manifest)
    write_checksums(package)
    with pytest.raises(ValueError, match="catalog authority/active identity"):
        verify(package, config, config_path)


def test_distinct_active_catalogs_share_authority_and_contract_identity(
    tmp_path: Path,
) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=1)

    def p1(data) -> None:
        data["tasks"]["conversation-summary"]["system_prompt"] += "\nP1 synthetic."

    def p2(data) -> None:
        data["tasks"]["conversation-summary"]["system_prompt"] += "\nP2 synthetic."

    first, _ = with_active_prompt_catalog(base, config_path, "p1", p1)
    second, _ = with_active_prompt_catalog(base, config_path, "p2", p2)
    first_prepared = prepare(with_run_paths(first, "p1"), config_path)
    second_prepared = prepare(with_run_paths(second, "p2"), config_path)
    with zipfile.ZipFile(first_prepared["archive"]) as archive:
        first_manifest = json.loads(archive.read("bundle-manifest.json"))
    with zipfile.ZipFile(second_prepared["archive"]) as archive:
        second_manifest = json.loads(archive.read("bundle-manifest.json"))
    first_identity = first_manifest["task_catalog_experiment"]
    second_identity = second_manifest["task_catalog_experiment"]
    assert first_identity["authority_catalog_sha256"] == second_identity[
        "authority_catalog_sha256"
    ]
    assert first_identity["non_prompt_contract_sha256"] == second_identity[
        "non_prompt_contract_sha256"
    ]
    assert first_identity["active_catalog_sha256"] != second_identity[
        "active_catalog_sha256"
    ]
    assert first_manifest["content_id"] != second_manifest["content_id"]
    assert first_manifest["cases"] != second_manifest["cases"]


def test_historical_catalog_serialization_remains_unchanged(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path, conversation_count=1)
    prepared = prepare(config, config_path)
    with zipfile.ZipFile(prepared["archive"]) as archive:
        bundle_manifest = json.loads(archive.read("bundle-manifest.json"))
        case = json.loads(archive.read("cases/c001--conversation-summary.json"))
    assert "task_catalog_experiment" not in bundle_manifest
    assert not any(name.startswith("task_catalog_") for name in case["contract_hashes"])
    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
        )
    )
    package = Path(generated["archive"])
    with zipfile.ZipFile(package) as archive:
        candidate_manifest = json.loads(archive.read("candidate-manifest.json"))
    assert "task_catalog_experiment" not in candidate_manifest
    assert "task_catalog_experiment" not in verify(package, config, config_path)
    metrics = score(package, config, config_path)
    assert "task_catalog_experiment" not in metrics
    judged = asyncio.run(score_with_judge(package, config, config_path, client=SyntheticJudge()))
    assert "task_catalog_experiment" not in judged


@pytest.mark.parametrize("role", ["development", "holdout"])
def test_selection_manifest_supports_declared_roles(tmp_path: Path, role: str) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    config, _, _ = with_selection_manifest(base, config_path, [2], role=role)
    assert len(build_authority(config, config_path)) == 4


def test_development_config_rejects_holdout_manifest(tmp_path: Path) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    config, _, _ = with_selection_manifest(
        base,
        config_path,
        [2],
        role="holdout",
        configured_role="development",
    )
    with pytest.raises(ValueError, match="role"):
        build_authority(config, config_path)


def test_selection_manifest_rejects_count_missing_and_duplicate_entries(tmp_path: Path) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    config, path, value = with_selection_manifest(base, config_path, [3, 1])

    bad_count = json.loads(json.dumps(value))
    bad_count["expected_case_count"] = 4
    with pytest.raises(ValidationError, match="case count"):
        SelectionManifest.model_validate(bad_count)

    missing = json.loads(json.dumps(value))
    missing["ordered_conversations"].pop()
    missing["conversation_count"] = 1
    missing["expected_case_count"] = 4
    missing["provider_counts"] = {"synthetic": 1}
    missing["length_stratum_counts"] = {"short": 1}
    missing["date_bin_counts"] = {"bin-1": 1}
    config = rewrite_selection_manifest(config, path, missing)
    with pytest.raises(ValueError, match="count differs"):
        build_authority(config, config_path)

    duplicate = json.loads(json.dumps(value))
    duplicate["ordered_conversations"][1] = duplicate["ordered_conversations"][0]
    config = rewrite_selection_manifest(config, path, duplicate)
    with pytest.raises(ValueError, match="duplicate"):
        build_authority(config, config_path)


def test_selection_manifest_rejects_unknown_and_source_identity_mismatch(
    tmp_path: Path,
) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    config, path, value = with_selection_manifest(base, config_path, [3, 1])

    unknown = json.loads(json.dumps(value))
    unknown["ordered_conversations"][0]["conversation_identity"] = "f" * 64
    config = rewrite_selection_manifest(config, path, unknown)
    with pytest.raises(ValueError, match="unknown|out-of-authority"):
        build_authority(config, config_path)

    source_mismatch = json.loads(json.dumps(value))
    source_mismatch["source_selection_identity"] = "e" * 64
    config = rewrite_selection_manifest(config, path, source_mismatch)
    with pytest.raises(ValueError, match="source-selection"):
        build_authority(config, config_path)


def test_selection_manifest_rejects_hash_and_order_tampering(tmp_path: Path) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    config, path, value = with_selection_manifest(base, config_path, [3, 1])
    tampered = json.loads(json.dumps(value))
    tampered["ordered_conversations"].reverse()
    write_json(path, tampered)
    with pytest.raises(ValueError, match="content/hash"):
        build_authority(config, config_path)


def test_selection_manifest_and_conversation_limit_are_mutually_exclusive(
    tmp_path: Path,
) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    config, _, _ = with_selection_manifest(base, config_path, [3, 1])
    with pytest.raises(ValueError, match="mutually exclusive"):
        prepare(config, config_path, conversation_limit=1)


def test_ordered_package_scope_tampering_is_rejected(tmp_path: Path) -> None:
    base, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    selected, _, _ = with_selection_manifest(base, config_path, [3, 1])
    config = with_run_paths(selected, "ordered-tamper")
    prepared = prepare(config, config_path)
    asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
        )
    )
    package_dir = tmp_path / "private" / "work" / "package-ordered-tamper"
    manifest_path = package_dir / "candidate-manifest.json"
    candidate_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidate_manifest["scope"]["selection_manifest_role"] = "holdout"
    write_json(manifest_path, candidate_manifest)
    write_checksums(package_dir)
    with pytest.raises(ValueError, match="selection manifest identity|scope differs"):
        verify(package_dir, config, config_path)


@pytest.mark.parametrize("limit", [0, -1, 4])
def test_invalid_conversation_limits_are_rejected(tmp_path: Path, limit: int) -> None:
    config, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    with pytest.raises(ValueError, match="conversation limit"):
        prepare(config, config_path, conversation_limit=limit)


def test_tampered_scope_and_non_prefix_package_are_rejected(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path, conversation_count=3)
    scoped = with_run_paths(config, "tamper")
    prepared = prepare(scoped, config_path, conversation_limit=2)
    asyncio.run(
        generate(
            Path(prepared["archive"]),
            scoped,
            config_path,
            client=SyntheticClient(),
            implementation_probe=clean_test_identity,
        )
    )
    package_dir = tmp_path / "private" / "work" / "package-tamper"
    manifest_path = package_dir / "candidate-manifest.json"
    original = json.loads(manifest_path.read_text(encoding="utf-8"))
    tampered = json.loads(json.dumps(original))
    tampered["scope"]["case_count"] = 4
    write_json(manifest_path, tampered)
    write_checksums(package_dir)
    with pytest.raises((ValueError, ValidationError), match="scope|case count"):
        verify(package_dir, scoped, config_path)

    non_prefix = json.loads(json.dumps(original))
    non_prefix["cases"][4]["alias"] = non_prefix["cases"][4]["alias"].replace(
        "c002", "c003"
    )
    write_json(manifest_path, non_prefix)
    write_checksums(package_dir)
    with pytest.raises(ValueError, match="frozen prefix"):
        verify(package_dir, scoped, config_path)


def test_output_path_safety_rejects_escape_and_overlap(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    with pytest.raises(ValueError, match="escapes"):
        resolve_member(config, config_path, "../outside", output=True)
    with pytest.raises(ValueError, match="overlap"):
        resolve_member(config, config_path, "inputs/child", output=True)


def test_interruption_resumes_without_duplicate_attempt(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    prepared = prepare(config, config_path)
    client = InterruptOnceClient()
    with pytest.raises(RuntimeError, match="interruption"):
        asyncio.run(
            generate(
                Path(prepared["archive"]),
                config,
                config_path,
                client=client,
                implementation_probe=clean_test_identity,
            )
        )
    result = asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=client,
            implementation_probe=clean_test_identity,
        )
    )
    assert result["completed"] == 8
    attempts = list(
        (tmp_path / "private" / "work" / "generation" / "results").rglob("attempts/*.json")
    )
    assert len(attempts) == 8


def test_prepare_refuses_existing_destination_without_deleting(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    prepare(config, config_path)
    sentinel = tmp_path / "private" / "work" / "bundle" / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    with pytest.raises(ValueError, match="already exists"):
        prepare(config, config_path)
    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_measured_implementation_identity_policies(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    _validate_implementation(config, clean_test_identity())
    with pytest.raises(ValueError, match="commit"):
        _validate_implementation(config, ImplementationIdentity("wrong-commit", False, None))
    with pytest.raises(ValueError, match="dirty"):
        _validate_implementation(config, ImplementationIdentity("test-commit", True, "diff-hash"))
    candidate = config.candidate.model_copy(
        update={"allow_dirty_tracked": True, "tracked_diff_sha256": "diff-hash"}
    )
    approved = config.model_copy(update={"candidate": candidate})
    _validate_implementation(approved, ImplementationIdentity("test-commit", True, "diff-hash"))
    prepared = prepare(config, config_path)
    client = SyntheticClient()
    with pytest.raises(ValueError, match="commit"):
        asyncio.run(
            generate(
                Path(prepared["archive"]),
                config,
                config_path,
                client=client,
                implementation_probe=lambda: ImplementationIdentity("wrong-commit", False, None),
            )
        )
    assert client.calls == 0


@pytest.mark.parametrize("wrong_after", [0, 1])
def test_candidate_response_identity_mismatch_stops_run(tmp_path: Path, wrong_after: int) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    prepared = prepare(config, config_path)
    client = WrongIdentityClient(wrong_after=wrong_after)
    with pytest.raises(ValueError, match="provider/model"):
        asyncio.run(
            generate(
                Path(prepared["archive"]),
                config,
                config_path,
                client=client,
                implementation_probe=clean_test_identity,
            )
        )
    assert client.calls == wrong_after + 1


def test_providerless_transport_failures_remain_explicit(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    prepared = prepare(config, config_path)
    client = TransportFailureClient()
    generated = asyncio.run(
        generate(
            Path(prepared["archive"]),
            config,
            config_path,
            client=client,
            implementation_probe=clean_test_identity,
        )
    )
    checked = verify(Path(generated["archive"]), config, config_path)
    assert checked["failed"] == 8
    assert client.calls == 8


@pytest.mark.parametrize(
    "flags",
    [
        ["--with-judge"],
        ["--with-judge", "--allow-remote"],
        ["--with-judge", "--confirm-private-eval"],
    ],
)
def test_judge_requires_all_authorization_flags(tmp_path: Path, flags: list[str]) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    config_path.write_text(
        yaml.safe_dump(config.model_dump(mode="json"), sort_keys=False), encoding="utf-8"
    )
    package = tmp_path / "placeholder.zip"
    package.write_bytes(b"placeholder")
    result = CliRunner().invoke(
        bench_cli.app,
        ["score", "--package", str(package), "--config", str(config_path), *flags],
    )
    assert result.exit_code == 2
    assert "requires --with-judge --allow-remote --confirm-private-eval" in result.output


def test_missing_judge_credential_prevents_client_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    models = Path(config.model_catalog)
    text = models.read_text(encoding="utf-8").replace(
        "  judge:\n    model:",
        "  judge:\n    api_key_env: WP52B1_MISSING_TEST_KEY\n    model:",
    )
    models.write_text(text, encoding="utf-8")
    monkeypatch.delenv("WP52B1_MISSING_TEST_KEY", raising=False)
    client = SyntheticJudge()
    with pytest.raises(AIConfigError, match="WP52B1_MISSING_TEST_KEY"):
        asyncio.run(
            score_with_judge(tmp_path / "not-opened.zip", config, config_path, client=client)
        )
    assert client.calls == 0


def test_disabled_judge_fails_before_private_reads(tmp_path: Path) -> None:
    config, config_path = synthetic_workspace(tmp_path)
    disabled = config.model_copy(
        update={"judge": config.judge.model_copy(update={"enabled": False})}
    )
    client = SyntheticJudge()
    with pytest.raises(ValueError, match="disabled"):
        asyncio.run(
            score_with_judge(tmp_path / "not-opened.zip", disabled, config_path, client=client)
        )
    assert client.calls == 0


def test_judge_provider_failure_resume_and_append_only_retry(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    failing = JudgeFailureClient("provider")
    first = asyncio.run(score_with_judge(package, config, config_path, client=failing))
    assert first["failed"] == 8
    assert first["baseline_attempts"] == {"completed": 0, "failed": 8}
    asyncio.run(score_with_judge(package, config, config_path, client=failing))
    assert failing.calls == 8
    succeeding = SyntheticJudge()
    retried = asyncio.run(
        score_with_judge(package, config, config_path, client=succeeding, retry_failures=True)
    )
    assert retried["completed"] == 8
    assert retried["total_attempts"] == 16
    assert retried["current_attempts"] == {"completed": 8, "failed": 0}
    asyncio.run(score_with_judge(package, config, config_path, client=succeeding))
    assert succeeding.calls == 8


def test_judge_schema_failure_is_cached_safely(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    client = JudgeFailureClient("schema")
    metrics = asyncio.run(score_with_judge(package, config, config_path, client=client))
    assert metrics["failure_categories"] == {"output_schema": 8}
    output = (tmp_path / "private" / "runs" / "run-one" / "judge" / "case-scores.jsonl").read_text(
        encoding="utf-8"
    )
    assert "provider-controlled" not in output


def test_invalid_json_failure_retains_only_bounded_response_metadata(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    client = InvalidJsonMetadataJudge()
    metrics = asyncio.run(score_with_judge(package, config, config_path, client=client))
    assert metrics["failure_categories"] == {"provider_invalid_json": 8}
    output = (tmp_path / "private" / "runs" / "run-one" / "judge" / "case-scores.jsonl").read_text(
        encoding="utf-8"
    )
    assert "PRIVATE-MARKER" not in output
    records = [json.loads(line) for line in output.splitlines()]
    assert all(record["response_metadata"] == {
        "finish_reason": "length",
        "response_present": True,
        "response_characters": len("PRIVATE-MARKER-not-json"),
        "usage": {
            "completion_tokens": 500,
            "prompt_tokens": 20,
            "reasoning_tokens": 450,
        },
    } for record in records)


def test_reasoning_setting_change_invalidates_judge_cache(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    first = SyntheticJudge()
    asyncio.run(score_with_judge(package, config, config_path, client=first))
    assert first.calls == 8
    models_path = Path(config.model_catalog)
    model_data = yaml.safe_load(models_path.read_text(encoding="utf-8"))
    model_data["profiles"]["judge"]["reasoning_effort"] = "none"
    models_path.write_text(yaml.safe_dump(model_data, sort_keys=False), encoding="utf-8")
    second = SyntheticJudge()
    asyncio.run(score_with_judge(package, config, config_path, client=second))
    assert second.calls == 8


def test_repeated_scoring_preserves_judge_reports_and_attempts(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    judge = SyntheticJudge()
    first = asyncio.run(score_with_judge(package, config, config_path, client=judge))
    run_root = tmp_path / "private" / "runs" / "run-one"
    attempts = sorted((run_root / "judge" / "attempts").glob("*/*/*.json"))
    before = hashlib.sha256(b"".join(path.read_bytes() for path in attempts)).hexdigest()

    score(package, config, config_path)
    no_call = NoCallJudge()
    second = asyncio.run(
        score_with_judge(package, config, config_path, client=no_call, cache_only=True)
    )

    after_attempts = sorted((run_root / "judge" / "attempts").glob("*/*/*.json"))
    after = hashlib.sha256(b"".join(path.read_bytes() for path in after_attempts)).hexdigest()
    aggregate = json.loads((run_root / "reports" / "aggregate.json").read_text(encoding="utf-8"))
    markdown = (run_root / "reports" / "aggregate.md").read_text(encoding="utf-8")
    manifest = json.loads((run_root / "run-manifest.json").read_text(encoding="utf-8"))
    assert second == first
    assert no_call.calls == 0
    assert len(after_attempts) == len(attempts) == 8
    assert after == before
    assert aggregate["judge_semantic"] == first
    assert markdown.count("## Judge coverage") == 1
    assert manifest["deterministic_only"] is False


def test_interrupted_aggregate_is_rebuilt_without_judge_call(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    judge = SyntheticJudge()
    judged = asyncio.run(score_with_judge(package, config, config_path, client=judge))
    run_root = tmp_path / "private" / "runs" / "run-one"
    deterministic = json.loads(
        (run_root / "deterministic" / "metrics.json").read_text(encoding="utf-8")
    )
    write_json(run_root / "reports" / "aggregate.json", deterministic)
    (run_root / "reports" / "aggregate.md").write_text("interrupted", encoding="utf-8")

    score(package, config, config_path)
    no_call = NoCallJudge()
    resumed = asyncio.run(
        score_with_judge(package, config, config_path, client=no_call, cache_only=True)
    )
    aggregate = json.loads((run_root / "reports" / "aggregate.json").read_text(encoding="utf-8"))
    markdown = (run_root / "reports" / "aggregate.md").read_text(encoding="utf-8")
    assert resumed == judged
    assert no_call.calls == 0
    assert aggregate["judge_semantic"] == judged
    assert markdown.count("## Judge coverage") == 1


def test_interrupted_judge_finalize_repairs_manifest_without_call(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    judge = SyntheticJudge()
    judged = asyncio.run(score_with_judge(package, config, config_path, client=judge))
    run_root = tmp_path / "private" / "runs" / "run-one"
    manifest_path = run_root / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["deterministic_only"] = True
    manifest.pop("judge_profile")
    manifest.pop("rubric_version")
    write_json(manifest_path, manifest)
    deterministic = json.loads(
        (run_root / "deterministic" / "metrics.json").read_text(encoding="utf-8")
    )
    write_json(run_root / "reports" / "aggregate.json", deterministic)

    score(package, config, config_path)
    repaired = json.loads(manifest_path.read_text(encoding="utf-8"))
    aggregate = json.loads((run_root / "reports" / "aggregate.json").read_text(encoding="utf-8"))
    assert repaired["deterministic_only"] is False
    assert repaired["judge_profile"] == config.judge.profile
    assert aggregate["judge_semantic"] == judged
    no_call = NoCallJudge()
    assert asyncio.run(
        score_with_judge(package, config, config_path, client=no_call, cache_only=True)
    ) == judged
    assert no_call.calls == 0


def test_cache_only_miss_stops_before_provider_call(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    no_call = NoCallJudge()
    with pytest.raises(ValueError, match="cache miss"):
        asyncio.run(
            score_with_judge(package, config, config_path, client=no_call, cache_only=True)
        )
    assert no_call.calls == 0


def test_repeated_score_rejects_changed_deterministic_artifact(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    metrics_path = tmp_path / "private" / "runs" / "run-one" / "deterministic" / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["runtime_reliability"]["expected"] += 1
    write_json(metrics_path, metrics)
    with pytest.raises(
        ValueError,
        match=r"metrics\.json semantic at \$\.runtime_reliability\.expected",
    ):
        score(package, config, config_path)


def test_legacy_csv_newlines_are_migrated_without_semantic_change(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    matrix = (
        tmp_path
        / "private"
        / "runs"
        / "run-one"
        / "deterministic"
        / "work-mode-confusion.csv"
    )
    original = matrix.read_bytes()
    matrix.write_bytes(original.replace(b"\r\n", b"\n"))
    score(package, config, config_path)
    assert matrix.read_bytes() == original


def test_unexpected_judge_programming_error_aborts_without_cache(tmp_path: Path) -> None:
    config, config_path, package = successful_package(tmp_path)
    client = JudgeFailureClient("programming")
    with pytest.raises(RuntimeError, match="programming defect"):
        asyncio.run(score_with_judge(package, config, config_path, client=client))
    attempts = tmp_path / "private" / "runs" / "run-one" / "judge" / "attempts"
    assert not list(attempts.rglob("*.json"))


def test_cli_default_output_and_errors_redact_private_markers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    marker = "PRIVATE-MARKER-DO-NOT-PRINT"
    private_dir = tmp_path / marker
    private_dir.mkdir()
    config_path = private_dir / "evaluation.yaml"
    bundle = private_dir / "bundle.zip"
    package = private_dir / "package.zip"
    for path in (config_path, bundle, package):
        path.write_text("placeholder", encoding="utf-8")
    loaded = type("Loaded", (), {"judge": type("Judge", (), {"enabled": True})()})()
    monkeypatch.setattr(bench_cli, "load_config", lambda path: loaded)
    monkeypatch.setattr(
        bench_cli,
        "prepare_bundle",
        lambda *args, **kwargs: {
            "archive": rf"C:\private\{marker}\bundle.zip",
            "cases": 8,
        },
    )

    async def fake_generate(*args, **kwargs):
        return {"archive": rf"C:\private\{marker}\package.zip", "completed": 8}

    monkeypatch.setattr(bench_cli, "generate_cases", fake_generate)
    monkeypatch.setattr(bench_cli, "verify_package", lambda *args: {"valid": True})
    monkeypatch.setattr(
        bench_cli, "score_package", lambda *args: {"runtime_reliability": {"expected": 8}}
    )

    async def fake_judge(*args, **kwargs):
        return {"eligible": 8, "completed": 8}

    monkeypatch.setattr(bench_cli, "score_with_judge", fake_judge)
    runner = CliRunner()
    commands = [
        ["prepare", "--config", str(config_path)],
        [
            "prepare",
            "--config",
            str(config_path),
            "--conversation-limit",
            "1",
        ],
        ["generate", "--bundle", str(bundle), "--config", str(config_path)],
        ["verify", "--package", str(package), "--config", str(config_path)],
        [
            "score",
            "--package",
            str(package),
            "--config",
            str(config_path),
            "--deterministic-only",
        ],
    ]
    for command in commands:
        result = runner.invoke(bench_cli.app, command)
        assert result.exit_code == 0
        assert marker not in result.output
        assert r"C:\private" not in result.output
    assert "candidate-input-archive" in runner.invoke(bench_cli.app, commands[0]).output
    authorized = runner.invoke(
        bench_cli.app,
        [
            "score",
            "--package",
            str(package),
            "--config",
            str(config_path),
            "--with-judge",
            "--allow-remote",
            "--confirm-private-eval",
        ],
    )
    assert authorized.exit_code == 0
    assert '"completed": 8' in authorized.output

    monkeypatch.setattr(
        bench_cli,
        "prepare_bundle",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ValueError(rf"failure at C:\private\{marker}\source.json")
        ),
    )
    failed = runner.invoke(bench_cli.app, commands[0])
    assert failed.exit_code == 2
    assert marker not in failed.output
    assert "private evaluation validation failed" in failed.output


def test_missing_config_path_is_not_echoed_by_cli() -> None:
    marker = "PRIVATE-MARKER-MISSING-CONFIG"
    path = rf"C:\private\{marker}\evaluation.yaml"
    result = CliRunner().invoke(bench_cli.app, ["prepare", "--config", path])
    assert result.exit_code == 2
    assert marker not in result.output
    assert "invalid evaluation or model configuration" in result.output


@pytest.mark.parametrize("name", [r"..\escape", r"C:\absolute", r"\\server\share\file"])
def test_safe_extract_rejects_windows_unsafe_names(tmp_path: Path, name: str) -> None:
    archive = tmp_path / "unsafe-windows.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr(name, "value")
    with pytest.raises(ValueError, match="unsafe"):
        safe_extract(archive, tmp_path / "out")


def test_safe_extract_rejects_case_collision(tmp_path: Path) -> None:
    archive = tmp_path / "collision.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("results/A.json", "one")
        handle.writestr("results/a.json", "two")
    with pytest.raises(ValueError, match="colliding"):
        safe_extract(archive, tmp_path / "out")


def test_safe_extract_rejects_symlink_and_size_limit(tmp_path: Path) -> None:
    symlink_archive = tmp_path / "symlink.zip"
    with zipfile.ZipFile(symlink_archive, "w") as handle:
        info = zipfile.ZipInfo("results/link")
        info.external_attr = 0o120777 << 16
        handle.writestr(info, "target")
    with pytest.raises(ValueError, match="unsafe"):
        safe_extract(symlink_archive, tmp_path / "link-out")

    large_archive = tmp_path / "large.zip"
    with zipfile.ZipFile(large_archive, "w") as handle:
        handle.writestr("results/value", "1234")
    with pytest.raises(ValueError, match="unsafe"):
        safe_extract(large_archive, tmp_path / "large-out", max_file_size=3)


def test_safe_extract_rejects_entries_outside_allowlist(tmp_path: Path) -> None:
    archive = tmp_path / "unexpected.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("source/private.json", "{}")
    with pytest.raises(ValueError, match="unexpected"):
        safe_extract(archive, tmp_path / "out", allowed_prefixes=("results",))
