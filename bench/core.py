"""Split preparation, candidate generation, verification, and local scoring."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import platform
import re
import shutil
import tempfile
import time
from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from chat_chronicle import __version__ as application_version
from chat_chronicle.ai import (
    CompletionRequest,
    LiteLLMClient,
    LLMClient,
    LLMError,
    PreparedAttempt,
    SelectedInput,
    _schema_spec,
    _validate_and_finalize,
)
from chat_chronicle.ai_config import (
    interpolate_prompt,
    load_model_catalog,
    load_task_catalog,
    resolve_generation,
    resolve_model,
)

from .config import _relative
from .implementation import ImplementationIdentity, measure_implementation
from .io import (
    atomic_json,
    atomic_text,
    deterministic_zip,
    digest,
    digest_bytes,
    safe_extract,
    verify_checksums,
    write_checksums,
)
from .loaders import load_inputs, load_references
from .models import (
    Attempt,
    BundleCase,
    ConversationScope,
    EvaluationConfig,
    InputEnvelope,
    ReferenceEnvelope,
)
from .paths import resolve_member

PACKAGE_PREFIXES = (
    "candidate-manifest.json",
    "checksums.json",
    "case-accounting.json",
    "generation-summary.json",
    "README-private.txt",
    "results",
    "raw-invalid",
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _selector(source: InputEnvelope, task: str):
    return source.recent if task == "last-activity" else source.overview


def build_authority(
    config: EvaluationConfig,
    config_path: Path,
    conversation_limit: int | None = None,
) -> list[BundleCase]:
    inputs = load_inputs(
        resolve_member(config, config_path, config.paths.source, output=False),
        config.expected_conversations,
    )
    if any(item.corpus_version != config.corpus_id for item in inputs):
        raise ValueError("accepted corpus identity mismatch")
    effective_limit = _effective_conversation_limit(config, conversation_limit)
    task_path = _relative(config_path, config.task_catalog)
    tasks = load_task_catalog(task_path)
    task_hash = digest_bytes(task_path.read_bytes())
    if any(item.task_catalog_hash_reference != task_hash for item in inputs):
        raise ValueError("accepted input task catalog hash mismatch")
    models = load_model_catalog(_relative(config_path, config.model_catalog))
    profile = models.profiles[config.candidate.profile]
    cases: list[BundleCase] = []
    for index, source in enumerate(inputs[:effective_limit], 1):
        for task_name in config.tasks:
            task = tasks.tasks[task_name]
            selected = _selector(source, task_name)
            if selected.selector != task.input_selector:
                raise ValueError("accepted selector does not match task contract")
            values = {
                "conversation_id": str(source.source_conversation_id),
                "provider": source.provider,
                "title": source.source_title,
                "start_date": source.start_date,
                "last_active_date": source.last_active_date,
                "transcript": selected.transcript,
            }
            messages = [
                {"role": "system", "content": interpolate_prompt(task.system_prompt, values)},
                {"role": "user", "content": interpolate_prompt(task.user_prompt, values)},
            ]
            spec = _schema_spec(task.output_schema)
            response_schema = spec.provider_model.model_json_schema()
            evidence = response_schema.get("properties", {}).get("evidence_message_ids", {})
            if selected.selected_message_ids and isinstance(evidence, dict):
                evidence.setdefault("items", {"type": "integer"})["enum"] = (
                    selected.selected_message_ids
                )
            generation = resolve_generation(task, profile).model_dump(mode="json")
            identities = {
                "input": selected.canonical_input_hash,
                "dates": digest({"start": source.start_date, "last": source.last_active_date}),
                "task": digest(task.model_dump(mode="json")),
                "selector": digest(
                    {"name": selected.selector, "version": selected.selector_version}
                ),
                "prompt": digest(messages),
                "provider_schema": digest(response_schema),
                "application_schema": f"{task.output_schema}:{spec.identity_version}",
                "finalizer": f"{task.output_schema}:{spec.identity_version}",
                "generation": digest(generation),
                "request_construction": "1",
            }
            alias = f"c{index:03d}--{task_name}"
            cases.append(
                BundleCase(
                    alias=alias,
                    fingerprint=digest(identities),
                    task=task_name,
                    task_version=task.version,
                    schema_name=task.output_schema,
                    schema_version=spec.identity_version,
                    selector=selected.selector,
                    selector_version=selected.selector_version,
                    messages=messages,
                    response_schema=response_schema,
                    selected={
                        "provider": source.provider,
                        "title": source.source_title,
                        "start_date": source.start_date,
                        "last_active_date": source.last_active_date,
                        "transcript": selected.transcript,
                        "selected_message_ids": selected.selected_message_ids,
                        "selection_metadata": selected.selection_metadata,
                    },
                    generation=generation,
                    contract_hashes=identities,
                )
            )
    if len(cases) != effective_limit * len(config.tasks):
        raise ValueError("authoritative case accounting mismatch")
    return cases


def _effective_conversation_limit(config: EvaluationConfig, conversation_limit: int | None) -> int:
    if conversation_limit is None:
        return config.expected_conversations
    if not 1 <= conversation_limit <= config.expected_conversations:
        raise ValueError("conversation limit must be between 1 and configured frozen count")
    return conversation_limit


def _scope(
    config: EvaluationConfig,
    cases: list[BundleCase],
    requested_limit: int | None,
) -> ConversationScope:
    effective = _effective_conversation_limit(config, requested_limit)
    return ConversationScope(
        requested_conversation_limit=requested_limit,
        effective_conversation_count=effective,
        case_count=len(cases),
        frozen_prefix_identity=digest(
            {
                "selection": "frozen-prefix-v1",
                "corpus": config.corpus_id,
                "effective_conversation_count": effective,
                "case_fingerprints": [case.fingerprint for case in cases],
            }
        ),
    )


def _validate_scope_manifest(
    config: EvaluationConfig,
    entries: list[dict[str, Any]],
    raw_scope: Any,
) -> ConversationScope:
    scope = ConversationScope.model_validate(raw_scope)
    if scope.effective_conversation_count > config.expected_conversations:
        raise ValueError("bundle conversation scope exceeds configured frozen count")
    if (
        scope.requested_conversation_limit is None
        and scope.effective_conversation_count != config.expected_conversations
    ):
        raise ValueError("unlimited scope must use the complete frozen conversation count")
    expected_order = [
        (f"c{index:03d}--{task}", task)
        for index in range(1, scope.effective_conversation_count + 1)
        for task in config.tasks
    ]
    actual_order = [(item.get("alias"), item.get("task")) for item in entries]
    if actual_order != expected_order or len(entries) != scope.case_count:
        raise ValueError("bundle cases are not the declared frozen prefix")
    expected_identity = digest(
        {
            "selection": scope.selection,
            "corpus": config.corpus_id,
            "effective_conversation_count": scope.effective_conversation_count,
            "case_fingerprints": [item.get("fingerprint") for item in entries],
        }
    )
    if scope.frozen_prefix_identity != expected_identity:
        raise ValueError("bundle frozen-prefix identity mismatch")
    return scope


def prepare(
    config: EvaluationConfig,
    config_path: Path,
    conversation_limit: int | None = None,
) -> dict[str, Any]:
    cases = build_authority(config, config_path, conversation_limit)
    scope = _scope(config, cases, conversation_limit)
    profile = load_model_catalog(_relative(config_path, config.model_catalog)).profiles[
        config.candidate.profile
    ]
    root = resolve_member(config, config_path, config.paths.bundle, output=True)
    archive = root.with_suffix(".zip")
    if root.exists() or archive.exists():
        raise ValueError("bundle destination already exists; choose a unique output path")
    (root / "cases").mkdir(parents=True)
    (root / "contracts").mkdir()
    for case in cases:
        atomic_json(root / "cases" / f"{case.alias}.json", case.model_dump(mode="json"))
    atomic_json(root / "bundle-manifest.json", _bundle_manifest(config, cases, profile, scope))
    (root / "README-private.txt").write_text(
        "PRIVATE: selected conversation content. Transfer only by an owner-approved method.\n",
        encoding="utf-8",
    )
    content_id = write_checksums(root)
    return {
        "cases": len(cases),
        "conversations": scope.effective_conversation_count,
        "scope": scope.selection,
        "content_id": content_id,
        "archive": str(archive),
        "transfer_hash": deterministic_zip(root, archive),
    }


def _profile_identity(profile: Any) -> dict[str, Any]:
    identity = profile.model_dump(mode="json")
    if identity.get("reasoning_effort") is None:
        identity.pop("reasoning_effort", None)
    return identity


def _bundle_manifest(
    config: EvaluationConfig,
    cases: list[BundleCase],
    profile: Any,
    scope: ConversationScope,
) -> dict[str, Any]:
    entries = [
        {"alias": case.alias, "fingerprint": case.fingerprint, "task": case.task} for case in cases
    ]
    return {
        "version": 1,
        "corpus_id": config.corpus_id,
        "expected_cases": scope.case_count,
        "scope": scope.model_dump(mode="json"),
        "cases": entries,
        "application_version": application_version,
        "required_candidate": config.candidate.model_dump(mode="json"),
        "required_profile": _profile_identity(profile),
        "content_id": digest(
            {"scope": scope.model_dump(mode="json"), "cases": entries}
        ),
    }


def _authority_bundle_content_id(
    config: EvaluationConfig,
    config_path: Path,
    cases: list[BundleCase],
    scope: ConversationScope,
) -> str:
    profile = load_model_catalog(_relative(config_path, config.model_catalog)).profiles[
        config.candidate.profile
    ]
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "cases").mkdir()
        (root / "contracts").mkdir()
        for case in cases:
            atomic_json(root / "cases" / f"{case.alias}.json", case.model_dump(mode="json"))
        atomic_json(root / "bundle-manifest.json", _bundle_manifest(config, cases, profile, scope))
        (root / "README-private.txt").write_text(
            "PRIVATE: selected conversation content. Transfer only by an owner-approved method.\n",
            encoding="utf-8",
        )
        return write_checksums(root)


def _open_package(path: Path, temporary: Path, *, candidate: bool = False) -> Path:
    prefixes = PACKAGE_PREFIXES if candidate else None
    return safe_extract(path, temporary, allowed_prefixes=prefixes) if path.is_file() else path


def _attempts(case_dir: Path) -> list[Attempt]:
    return [
        Attempt.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted((case_dir / "attempts").glob("*.json"))
    ]


async def generate(
    bundle_path: Path,
    config: EvaluationConfig,
    config_path: Path,
    client: LLMClient | None = None,
    retry_failures: bool = False,
    implementation_probe: Callable[[], ImplementationIdentity] | None = None,
) -> dict[str, Any]:
    client = client or LiteLLMClient()
    with tempfile.TemporaryDirectory() as temporary:
        bundle = _open_package(bundle_path, Path(temporary))
        verify_checksums(bundle)
        manifest = json.loads((bundle / "bundle-manifest.json").read_text(encoding="utf-8"))
        scope = _validate_scope_manifest(config, manifest["cases"], manifest.get("scope"))
        if (
            len(manifest["cases"]) != scope.case_count
            or manifest.get("expected_cases") != scope.case_count
        ):
            raise ValueError("bundle case accounting mismatch")
        if manifest.get("content_id") != digest(
            {"scope": scope.model_dump(mode="json"), "cases": manifest["cases"]}
        ):
            raise ValueError("bundle scope/case content identity mismatch")
        models = load_model_catalog(_relative(config_path, config.model_catalog))
        profile = models.profiles[config.candidate.profile]
        resolved = resolve_model(profile)
        if manifest.get("required_candidate") != config.candidate.model_dump(
            mode="json"
        ) or manifest.get("required_profile") != _profile_identity(profile):
            raise ValueError("candidate configuration does not match prepared bundle")
        _validate_artifact(config, config_path)
        measured = (implementation_probe or measure_implementation)()
        _validate_implementation(config, measured)
        work = resolve_member(config, config_path, config.paths.generation_work, output=True)
        work.mkdir(parents=True, exist_ok=True)
        work_identity = {
            "source_bundle_content_id": digest(
                json.loads((bundle / "checksums.json").read_text(encoding="utf-8"))
            ),
            "scope": scope.model_dump(mode="json"),
        }
        work_manifest = work / "work-manifest.json"
        if work_manifest.exists():
            if json.loads(work_manifest.read_text(encoding="utf-8")) != work_identity:
                raise ValueError("generation work belongs to a different bundle scope")
        else:
            atomic_json(work_manifest, work_identity)
        run_started = utc_now()
        for entry in manifest["cases"]:
            case = BundleCase.model_validate_json(
                (bundle / "cases" / f"{entry['alias']}.json").read_text(encoding="utf-8")
            )
            case_dir = work / "results" / case.alias
            prior = _attempts(case_dir) if case_dir.exists() else []
            base_identity = digest(
                {
                    "case": case.fingerprint,
                    "candidate": config.candidate.model_dump(mode="json"),
                    "profile": _profile_identity(profile),
                }
            )
            matching = [item for item in prior if item.attempt_id.startswith(base_identity)]
            if prior and not matching:
                raise ValueError(
                    "generation work belongs to a different candidate identity; "
                    "choose a unique generation work directory"
                )
            if matching and (matching[-1].status == "success" or not retry_failures):
                continue
            ordinal = len(prior) + 1
            attempt_id = f"{base_identity}-{ordinal:04d}"
            attempt_dir = case_dir / "attempts"
            attempt_dir.mkdir(parents=True, exist_ok=True)
            running = case_dir / "running.json"
            atomic_json(running, {"attempt_id": attempt_id, "started_at": utc_now()})
            started = utc_now()
            clock = time.monotonic()
            response = None
            result = None
            raw_file = None
            boundary = None
            try:
                request = CompletionRequest(
                    model=resolved["model"],
                    messages=case.messages,
                    response_schema=case.response_schema,
                    enforce_schema=profile.structured_output,
                    temperature=case.generation["temperature"],
                    max_tokens=case.generation["max_tokens"],
                    timeout=profile.timeout,
                    retries=0,
                    api_base=profile.api_base,
                    api_key=resolved.get("api_key"),
                    context_window=profile.context_window,
                )
                response = await client.complete(request)
                if (
                    response.provider != config.candidate.expected_provider
                    or response.model != config.candidate.expected_model
                ):
                    raise ValueError("candidate response provider/model identity mismatch")
                try:
                    parsed = json.loads(response.content)
                except json.JSONDecodeError as exc:
                    raise LLMError("invalid_json", "invalid JSON") from exc
                result = _validate_case_result(case, parsed, request)
                status = "success"
            except (LLMError, ValidationError) as exc:
                status = "failed"
                boundary = exc.kind if isinstance(exc, LLMError) else "schema_validation"
                if response is not None:
                    raw_file = f"raw-invalid/{case.alias}/{attempt_id}.txt"
                    raw_path = work / raw_file
                    raw_path.parent.mkdir(parents=True, exist_ok=True)
                    raw_path.write_text(response.content[:100_000], encoding="utf-8")
            record = Attempt(
                alias=case.alias,
                case_fingerprint=case.fingerprint,
                attempt_id=attempt_id,
                status=status,
                failure_boundary=boundary,
                result=result,
                raw_invalid_file=raw_file,
                provider=response.provider if response else None,
                model=response.model if response else None,
                latency_ms=int((time.monotonic() - clock) * 1000),
                usage=response.usage if response else None,
                started_at=started,
                completed_at=utc_now(),
            )
            atomic_json(attempt_dir / f"{ordinal:04d}.json", record.model_dump(mode="json"))
            atomic_json(
                case_dir / "index.json",
                {
                    "baseline_attempt": prior[0].attempt_id if prior else attempt_id,
                    "attempts": [item.attempt_id for item in prior] + [attempt_id],
                },
            )
            running.unlink(missing_ok=True)
        return package_candidate(bundle, work, config, config_path, run_started, measured)


def _validate_artifact(config: EvaluationConfig, config_path: Path) -> None:
    if not config.candidate.artifact_path:
        raise ValueError("candidate artifact_path is required for generation preflight")
    raw = Path(config.candidate.artifact_path)
    path = (raw if raw.is_absolute() else config_path.parent / raw).resolve()
    if not path.is_file() or path.name != config.candidate.artifact_file:
        raise ValueError("candidate artifact file identity mismatch")
    size = path.stat().st_size
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    value = hasher.hexdigest()
    if size != config.candidate.artifact_size or value != config.candidate.artifact_sha256:
        raise ValueError("candidate artifact size/hash mismatch")


def _validate_implementation(config: EvaluationConfig, measured: ImplementationIdentity) -> None:
    if (
        config.candidate.application_commit == "unknown"
        or measured.commit != config.candidate.application_commit
    ):
        raise ValueError("measured application commit does not match pinned identity")
    if measured.dirty_tracked:
        if (
            not config.candidate.allow_dirty_tracked
            or measured.tracked_diff_sha256 != config.candidate.tracked_diff_sha256
        ):
            raise ValueError("tracked implementation is dirty or has an unapproved diff")
    elif config.candidate.allow_dirty_tracked:
        raise ValueError("configured dirty-development policy does not match clean checkout")


def _validate_case_result(
    case: BundleCase,
    parsed: Any,
    request: CompletionRequest | None = None,
    *,
    finalized: bool = False,
) -> dict[str, Any]:
    if finalized:
        result = (
            _schema_spec(case.schema_name)
            .final_model.model_validate(parsed)
            .model_dump(mode="json")
        )
        if not set(result.get("evidence_message_ids", [])) <= set(
            case.selected["selected_message_ids"]
        ):
            raise ValueError("candidate evidence is outside selected input")
        if case.task == "conversation-summary" and (
            result["start_date"] != case.selected["start_date"]
            or result["last_active_date"] != case.selected["last_active_date"]
        ):
            raise ValueError("candidate deterministic dates mismatch")
        return result
    selected = SelectedInput(
        0,
        str(case.selected["provider"]),
        str(case.selected["title"]),
        str(case.selected["start_date"]),
        str(case.selected["last_active_date"]),
        str(case.selected["transcript"]),
        {"selected_message_ids": case.selected["selected_message_ids"]},
    )
    request = request or CompletionRequest(
        model="verification-only",
        messages=case.messages,
        response_schema=case.response_schema,
        enforce_schema=True,
        temperature=case.generation["temperature"],
        max_tokens=case.generation["max_tokens"],
        timeout=1,
        retries=0,
    )
    prepared = PreparedAttempt(
        selected, request, "", "", "", "", case.schema_name, case.schema_version
    )
    return _validate_and_finalize(parsed, prepared)


def package_candidate(
    bundle: Path,
    work: Path,
    config: EvaluationConfig,
    config_path: Path,
    run_started: str,
    measured: ImplementationIdentity,
) -> dict[str, Any]:
    destination = resolve_member(config, config_path, config.paths.candidate_package, output=True)
    archive = destination.with_suffix(".zip")
    if destination.exists() or archive.exists():
        raise ValueError("candidate package destination already exists")
    destination.mkdir(parents=True)
    bundle_manifest = json.loads((bundle / "bundle-manifest.json").read_text(encoding="utf-8"))
    (destination / "results").mkdir()
    for item in bundle_manifest["cases"]:
        alias = item["alias"]
        shutil.copytree(work / "results" / alias, destination / "results" / alias)
        raw_source = work / "raw-invalid" / alias
        if raw_source.exists():
            shutil.copytree(raw_source, destination / "raw-invalid" / alias)
    baseline = [_attempts(path)[0] for path in sorted((destination / "results").iterdir())]
    all_attempts = [
        item for path in sorted((destination / "results").iterdir()) for item in _attempts(path)
    ]
    success = sum(item.status == "success" for item in baseline)
    models = load_model_catalog(_relative(config_path, config.model_catalog))
    profile = models.profiles[config.candidate.profile]
    resolved = resolve_model(profile)
    manifest = {
        "version": 1,
        "source_bundle_content_id": digest(
            json.loads((bundle / "checksums.json").read_text(encoding="utf-8"))
        ),
        "expected": len(bundle_manifest["cases"]),
        "completed": len(baseline),
        "success": success,
        "failed": len(baseline) - success,
        "total_attempts": len(all_attempts),
        "cases": bundle_manifest["cases"],
        "scope": bundle_manifest["scope"],
        "application": {
            "version": application_version,
            "commit": measured.commit,
            "dirty_tracked": measured.dirty_tracked,
            "tracked_diff_sha256": measured.tracked_diff_sha256,
        },
        "candidate": config.candidate.model_dump(mode="json"),
        "resolved_model": resolved["model"],
        "resolved_providers": sorted(
            {item.provider for item in baseline if item.provider is not None}
        ),
        "actual_models": sorted({item.model for item in baseline if item.model is not None}),
        "api_base_class": "loopback",
        "runtime": {
            "os": platform.system(),
            "architecture": platform.machine(),
            "structured_output": profile.structured_output,
            "configured_context": profile.context_window,
            "timeout": profile.timeout,
            "retries": 0,
            "concurrency": profile.concurrency,
        },
        "generation_by_task": {
            item["task"]: BundleCase.model_validate_json(
                (bundle / "cases" / f"{item['alias']}.json").read_text(encoding="utf-8")
            ).generation
            for item in bundle_manifest["cases"]
        },
        "run_started_utc": run_started,
        "run_completed_utc": utc_now(),
        "usage_available": sum(item.usage is not None for item in baseline),
        "no_references_or_judge_results": True,
    }
    atomic_json(destination / "candidate-manifest.json", manifest)
    atomic_json(
        destination / "case-accounting.json",
        {
            key: manifest[key]
            for key in ("expected", "completed", "success", "failed", "total_attempts")
        },
    )
    atomic_json(
        destination / "generation-summary.json",
        {
            "success": success,
            "failed": len(baseline) - success,
            "failure_boundaries": dict(
                Counter(item.failure_boundary for item in baseline if item.failure_boundary)
            ),
        },
    )
    (destination / "README-private.txt").write_text(
        "PRIVATE: derived candidate output. Contains no source bundle or reference.\n",
        encoding="utf-8",
    )
    content_id = write_checksums(destination)
    return {
        "completed": len(baseline),
        "content_id": content_id,
        "archive": str(archive),
        "transfer_hash": deterministic_zip(destination, archive),
    }


def verify(package_path: Path, config: EvaluationConfig, config_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temporary:
        root = _open_package(package_path, Path(temporary), candidate=True)
        content_id = verify_checksums(root)
        manifest = json.loads((root / "candidate-manifest.json").read_text(encoding="utf-8"))
        scope = _validate_scope_manifest(config, manifest["cases"], manifest.get("scope"))
        authority = build_authority(config, config_path, scope.effective_conversation_count)
        authoritative_scope = _scope(config, authority, scope.requested_conversation_limit)
        if scope != authoritative_scope:
            raise ValueError("candidate scope differs from local frozen-prefix authority")
        expected = {item.alias: item for item in authority}
        _verify_file_allowlist(root, set(expected))
        aliases = [item["alias"] for item in manifest["cases"]]
        if aliases != list(expected) or len(set(aliases)) != len(aliases):
            raise ValueError("candidate cases do not match local authority")
        for item in manifest["cases"]:
            case = expected[item["alias"]]
            if item != {"alias": case.alias, "fingerprint": case.fingerprint, "task": case.task}:
                raise ValueError("candidate case identity differs from local authority")
        baseline: list[Attempt] = []
        all_attempts: list[Attempt] = []
        referenced_raw: set[str] = set()
        for alias, case in expected.items():
            case_dir = root / "results" / alias
            index = json.loads((case_dir / "index.json").read_text(encoding="utf-8"))
            attempts = _attempts(case_dir)
            if not attempts or index["attempts"] != [item.attempt_id for item in attempts]:
                raise ValueError("candidate attempt index mismatch")
            if index["baseline_attempt"] != attempts[0].attempt_id:
                raise ValueError("candidate baseline pointer mismatch")
            for attempt in attempts:
                if attempt.alias != alias or attempt.case_fingerprint != case.fingerprint:
                    raise ValueError("candidate attempt authority mismatch")
                if (attempt.provider is None) != (attempt.model is None):
                    raise ValueError("candidate response provenance is incomplete")
                if attempt.provider is not None and (
                    attempt.provider != config.candidate.expected_provider
                    or attempt.model != config.candidate.expected_model
                ):
                    raise ValueError("candidate response provider/model identity mismatch")
                raw = root / attempt.raw_invalid_file if attempt.raw_invalid_file else None
                if attempt.raw_invalid_file:
                    referenced_raw.add(attempt.raw_invalid_file)
                if attempt.status == "success":
                    if attempt.result is None or raw is not None:
                        raise ValueError("successful candidate result is malformed")
                    if (
                        _validate_case_result(case, attempt.result, finalized=True)
                        != attempt.result
                    ):
                        raise ValueError("candidate result failed local application validation")
                elif attempt.result is not None or not attempt.failure_boundary:
                    raise ValueError("failed candidate attempt is malformed")
                elif (
                    attempt.failure_boundary
                    in {"invalid_json", "schema_validation", "evidence_validation"}
                    and raw is None
                ):
                    raise ValueError("invalid candidate output is missing raw evidence")
                if raw is not None and not raw.is_file():
                    raise ValueError("candidate raw evidence is missing")
            baseline.append(attempts[0])
            all_attempts.extend(attempts)
        actual_raw = (
            {path.relative_to(root).as_posix() for path in (root / "raw-invalid").rglob("*.txt")}
            if (root / "raw-invalid").exists()
            else set()
        )
        if actual_raw != referenced_raw:
            raise ValueError("candidate raw evidence accounting mismatch")
        success = sum(item.status == "success" for item in baseline)
        accounting = (len(baseline), success, len(baseline) - success, len(all_attempts))
        if manifest.get("expected") != scope.case_count:
            raise ValueError("candidate expected count differs from declared scope")
        if accounting != (
            manifest["completed"],
            manifest["success"],
            manifest["failed"],
            manifest["total_attempts"],
        ):
            raise ValueError("candidate package accounting mismatch")
        accounting_file = json.loads(
            (root / "case-accounting.json").read_text(encoding="utf-8")
        )
        expected_accounting = {
            key: manifest[key]
            for key in ("expected", "completed", "success", "failed", "total_attempts")
        }
        if accounting_file != expected_accounting:
            raise ValueError("candidate case-accounting file differs from manifest")
        if manifest["candidate"] != config.candidate.model_dump(mode="json"):
            raise ValueError("candidate artifact/config identity mismatch")
        expected_application = {
            "version": application_version,
            "commit": config.candidate.application_commit,
            "dirty_tracked": config.candidate.allow_dirty_tracked,
            "tracked_diff_sha256": config.candidate.tracked_diff_sha256,
        }
        if manifest.get("application") != expected_application:
            raise ValueError("measured application provenance mismatch")
        if manifest.get("source_bundle_content_id") != _authority_bundle_content_id(
            config, config_path, authority, authoritative_scope
        ):
            raise ValueError("candidate source bundle identity differs from local authority")
        models = load_model_catalog(_relative(config_path, config.model_catalog))
        profile = models.profiles[config.candidate.profile]
        resolved = resolve_model(profile)
        expected_runtime = {
            "structured_output": profile.structured_output,
            "configured_context": profile.context_window,
            "timeout": profile.timeout,
            "retries": 0,
            "concurrency": profile.concurrency,
        }
        if manifest.get("resolved_model") != resolved["model"] or any(
            manifest.get("runtime", {}).get(key) != value for key, value in expected_runtime.items()
        ):
            raise ValueError("candidate resolved model/runtime provenance mismatch")
        _scan_leakage(root, authority)
        return {
            "valid": True,
            "content_id": content_id,
            "expected": len(baseline),
            "success": success,
            "failed": len(baseline) - success,
            "total_attempts": len(all_attempts),
            "scope": scope.model_dump(mode="json"),
        }


def _verify_file_allowlist(root: Path, aliases: set[str]) -> None:
    root_files = {
        "candidate-manifest.json",
        "checksums.json",
        "case-accounting.json",
        "generation-summary.json",
        "README-private.txt",
    }
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        parts = relative.split("/")
        allowed_result = (
            len(parts) == 3
            and parts[0] == "results"
            and parts[1] in aliases
            and parts[2] == "index.json"
        ) or (
            len(parts) == 4
            and parts[0] == "results"
            and parts[1] in aliases
            and parts[2] == "attempts"
            and re.fullmatch(r"[0-9]{4}\.json", parts[3]) is not None
        )
        allowed_raw = (
            len(parts) == 3
            and parts[0] == "raw-invalid"
            and parts[1] in aliases
            and parts[2].endswith(".txt")
        )
        allowed = relative in root_files or allowed_result or allowed_raw
        if not allowed:
            raise ValueError("candidate package contains an unexpected file")


def _scan_leakage(root: Path, authority: list[BundleCase]) -> None:
    text_files = [path for path in root.rglob("*") if path.is_file() and path.suffix != ".json"]
    json_files = [path for path in root.rglob("*.json") if path.name != "checksums.json"]
    all_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in [*text_files, *json_files]
    )
    lowered = all_text.lower()
    forbidden_keys = ("api_key", "credential", "password", "teacher_model", "fable")
    if any(key in lowered for key in forbidden_keys):
        raise ValueError("candidate package contains forbidden provenance")
    if re.search(r"(?i)(bearer\s+[A-Za-z0-9._~+/=-]{12,}|api[_-]?key\s*[:=])", all_text):
        raise ValueError("candidate package contains secret-shaped content")
    if any(str(case.selected["transcript"]) in all_text for case in authority):
        raise ValueError("candidate package contains a complete source transcript")
    for path in json_files:
        _reject_absolute_values(json.loads(path.read_text(encoding="utf-8")))


def _reject_absolute_values(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in {"api_key", "password", "credential", "secret"}:
                raise ValueError("candidate package contains a secret-shaped field")
            _reject_absolute_values(item)
    elif isinstance(value, list):
        for item in value:
            _reject_absolute_values(item)
    elif isinstance(value, str) and (
        value.startswith(("/", "\\\\")) or re.match(r"^[A-Za-z]:[\\/]", value)
    ):
        raise ValueError("candidate package contains an absolute path")


def validate_reference_authority(
    authority: list[BundleCase],
    inputs: list[InputEnvelope],
    references: dict[str, ReferenceEnvelope],
) -> None:
    for case in authority:
        reference = references[case.alias]
        source = inputs[int(case.alias[1:4]) - 1]
        spec = _schema_spec(case.schema_name)
        if (
            reference.task_version != case.task_version
            or reference.output_schema != case.schema_name
            or reference.provider_schema_version != spec.version
            or reference.finalizer_version != spec.finalizer_version
            or reference.task_catalog_hash != source.task_catalog_hash_reference
        ):
            raise ValueError("reference task/schema/finalizer/catalog identity mismatch")
        validated = spec.final_model.model_validate(reference.output).model_dump(mode="json")
        if validated != reference.output:
            raise ValueError("reference output is not canonical")
        if not set(validated.get("evidence_message_ids", [])) <= set(
            case.selected["selected_message_ids"]
        ):
            raise ValueError("reference evidence is outside accepted selected input")
        if case.task == "conversation-summary" and (
            validated["start_date"] != source.start_date
            or validated["last_active_date"] != source.last_active_date
        ):
            raise ValueError("reference deterministic dates mismatch")


def _matrix(
    rows: list[tuple[str, str]], expected: list[str], actual: list[str]
) -> dict[str, dict[str, int]]:
    return {
        label: {
            value: sum(1 for left, right in rows if left == label and right == value)
            for value in actual
        }
        for label in expected
    }


def _percentile(values: list[int], fraction: float) -> int | None:
    values = sorted(values)
    return values[min(len(values) - 1, int((len(values) - 1) * fraction))] if values else None


def _classification_stats(rows: list[tuple[str, str]], labels: list[str]) -> dict[str, Any]:
    total = len(rows)
    per_label = {}
    for label in labels:
        true_positive = sum(left == label and right == label for left, right in rows)
        support = sum(left == label for left, _ in rows)
        predicted = sum(right == label for _, right in rows)
        per_label[label] = {
            "support": support,
            "precision": true_positive / predicted if predicted else None,
            "recall": true_positive / support if support else None,
        }
    return {
        "total": total,
        "exact_agreement": sum(left == right for left, right in rows) / total if total else None,
        "per_label": per_label,
    }


def _usage_totals(attempts: list[Attempt]) -> dict[str, int]:
    result: Counter[str] = Counter()
    for attempt in attempts:
        for key, value in (attempt.usage or {}).items():
            if isinstance(value, int) and not isinstance(value, bool):
                result[key] += value
    return dict(result)


def score(package_path: Path, config: EvaluationConfig, config_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temporary:
        root = _open_package(package_path, Path(temporary), candidate=True)
        verification = verify(root, config, config_path)
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
            for path in root.glob("results/*/index.json")
        }
        case_scores: list[dict[str, Any]] = []
        rows: dict[str, list[tuple[str, str]]] = {name: [] for name in config.tasks}
        for case in authority:
            attempt = baselines[case.alias]
            reference = references[case.alias].output
            output = attempt.result or {}
            row: dict[str, Any] = {
                "alias": case.alias,
                "task": case.task,
                "valid": attempt.status == "success",
                "failure_boundary": attempt.failure_boundary,
                "evidence_valid": bool(output)
                and set(output.get("evidence_message_ids", []))
                <= set(case.selected["selected_message_ids"]),
            }
            if case.task == "conversation-summary":
                row.update(
                    date_valid=bool(output)
                    and output.get("start_date") == reference.get("start_date")
                    and output.get("last_active_date") == reference.get("last_active_date"),
                    word_count=len(str(output.get("summary", "")).split()),
                )
            elif case.task == "work-mode-classification":
                rows[case.task].append((reference["mode"], output.get("mode", "no_valid_output")))
            elif case.task == "last-activity":
                rows[case.task].append(
                    (reference["status"], output.get("status", "no_valid_output"))
                )
            else:
                expected = str(reference["title_fits"]).lower()
                actual = str(output["title_fits"]).lower() if output else "no_valid_output"
                rows[case.task].append((expected, actual))
                suggestion = output.get("suggested_title")
                row["suggestion_valid"] = (
                    output.get("title_fits") is True and suggestion is None
                ) or (
                    output.get("title_fits") is False
                    and isinstance(suggestion, str)
                    and 3 <= len(suggestion.split()) <= 10
                )
            case_scores.append(row)
        work_labels = ["manager", "executor", "one_off", "mixed", "unknown"]
        activity_labels = ["in_progress", "completed", "blocked", "awaiting_input", "unknown"]
        binary_labels = ["true", "false"]
        actual_suffix = ["no_valid_output"]
        matrices = {
            "work_mode": _matrix(
                rows["work-mode-classification"], work_labels, work_labels + actual_suffix
            ),
            "last_activity": _matrix(
                rows["last-activity"], activity_labels, activity_labels + actual_suffix
            ),
            "title_fit": _matrix(
                rows["title-assessment"], binary_labels, binary_labels + actual_suffix
            ),
        }
        matrix_stats = {
            "work_mode": _classification_stats(rows["work-mode-classification"], work_labels),
            "last_activity": _classification_stats(rows["last-activity"], activity_labels),
            "title_fit": _classification_stats(rows["title-assessment"], binary_labels),
        }
        by_task = {}
        for task in config.tasks:
            task_attempts = [baselines[item.alias] for item in authority if item.task == task]
            by_task[task] = {
                "expected": len(task_attempts),
                "valid": sum(item.status == "success" for item in task_attempts),
                "failed": sum(item.status == "failed" for item in task_attempts),
                "latency_ms": {
                    "p50": _percentile([item.latency_ms for item in task_attempts], 0.5),
                    "p95": _percentile([item.latency_ms for item in task_attempts], 0.95),
                },
                "usage_available": sum(item.usage is not None for item in task_attempts),
                "usage_missing": sum(item.usage is None for item in task_attempts),
                "usage_totals": _usage_totals(task_attempts),
                "schema_valid_rate": (
                    sum(item.status == "success" for item in task_attempts) / len(task_attempts)
                    if task_attempts
                    else None
                ),
            }
        metrics = {
            "scope": verification["scope"],
            "runtime_reliability": {
                "expected": len(authority),
                "valid": sum(item.status == "success" for item in baselines.values()),
                "failed": sum(item.status == "failed" for item in baselines.values()),
                "failure_boundaries": dict(
                    Counter(
                        item.failure_boundary
                        for item in baselines.values()
                        if item.failure_boundary
                    )
                ),
                "by_task": by_task,
            },
            "deterministic_contract": {
                "matrices": matrices,
                "matrix_statistics": matrix_stats,
                "evidence_valid": sum(item["evidence_valid"] for item in case_scores),
                "cross_field_valid": sum(item["valid"] for item in case_scores),
                "summary_date_valid": sum(item.get("date_valid", False) for item in case_scores),
                "summary_length_valid": sum(
                    item["task"] == "conversation-summary"
                    and item["valid"]
                    and item.get("word_count", 0) <= 120
                    for item in case_scores
                ),
                "title_suggestion_valid": sum(
                    item.get("suggestion_valid", False) for item in case_scores
                ),
                "no_valid_output": sum(not item["valid"] for item in case_scores),
            },
        }
        output_root = resolve_member(config, config_path, config.paths.scoring, output=True)
        run_manifest_path = output_root / "run-manifest.json"
        if run_manifest_path.exists():
            prior_run = json.loads(run_manifest_path.read_text(encoding="utf-8"))
            if prior_run.get("package_content_id") != verification["content_id"]:
                raise ValueError("scoring directory belongs to a different candidate package")
        deterministic = output_root / "deterministic"
        deterministic.mkdir(parents=True, exist_ok=True)
        case_scores_text = "".join(json.dumps(item, sort_keys=True) + "\n" for item in case_scores)
        _require_matching_artifact(deterministic / "metrics.json", metrics)
        _require_matching_text(deterministic / "case-scores.jsonl", case_scores_text)
        atomic_text(deterministic / "case-scores.jsonl", case_scores_text)
        atomic_json(output_root / "verification.json", verification)
        atomic_json(deterministic / "metrics.json", metrics)
        _write_matrices(deterministic, matrices)
        judge_metrics_path = output_root / "judge" / "metrics.json"
        judge_metrics = (
            json.loads(judge_metrics_path.read_text(encoding="utf-8"))
            if judge_metrics_path.exists()
            else None
        )
        if run_manifest_path.exists() and judge_metrics is not None:
            if prior_run.get("deterministic_only") is not False:
                raise ValueError("judged scoring manifest is inconsistent")
        write_aggregate_reports(output_root, metrics, judge_metrics)
        if not run_manifest_path.exists():
            atomic_json(
                run_manifest_path,
                {
                    "version": 1,
                    "deterministic_only": True,
                    "package_content_id": verification["content_id"],
                    "scope": verification["scope"],
                    "created_at_utc": utc_now(),
                },
            )
        return metrics


def _require_matching_artifact(path: Path, value: Any) -> None:
    if not path.exists():
        return
    existing = json.loads(path.read_text(encoding="utf-8"))
    if existing != value:
        location = _first_difference_path(existing, value)
        raise ValueError(
            f"deterministic artifact mismatch: {path.name} semantic at {location}"
        )


def _require_matching_text(path: Path, value: str) -> None:
    if not path.exists() or path.read_bytes() == value.encode("utf-8"):
        return
    existing = path.read_text(encoding="utf-8")
    if existing.replace("\r\n", "\n") == value.replace("\r\n", "\n"):
        return  # Accepted newline-only legacy serialization; caller migrates atomically.
    if path.suffix == ".jsonl":
        try:
            old_rows = [json.loads(line) for line in existing.splitlines()]
            new_rows = [json.loads(line) for line in value.splitlines()]
        except json.JSONDecodeError:
            pass
        else:
            if old_rows == new_rows:
                return  # Accepted canonical-format-only legacy serialization.
    if path.suffix == ".csv":
        if list(csv.reader(io.StringIO(existing))) == list(csv.reader(io.StringIO(value))):
            return  # Accepted CSV serialization-only legacy representation.
    raise ValueError(f"deterministic artifact mismatch: {path.name} semantic")


def _first_difference_path(existing: Any, expected: Any, path: str = "$") -> str:
    if type(existing) is not type(expected):
        return path
    if isinstance(existing, dict):
        for key in sorted(set(existing) | set(expected)):
            child = f"{path}.{key}"
            if key not in existing or key not in expected:
                return child
            if existing[key] != expected[key]:
                return _first_difference_path(existing[key], expected[key], child)
    elif isinstance(existing, list):
        for index, (old, new) in enumerate(zip(existing, expected, strict=False)):
            if old != new:
                return _first_difference_path(old, new, f"{path}[{index}]")
        if len(existing) != len(expected):
            return f"{path}.length"
    return path


def write_aggregate_reports(
    output_root: Path,
    deterministic_metrics: dict[str, Any],
    judge_metrics: dict[str, Any] | None,
) -> None:
    aggregate = dict(deterministic_metrics)
    markdown = _aggregate_markdown(deterministic_metrics)
    if judge_metrics is not None:
        aggregate["judge_semantic"] = judge_metrics
        markdown += _judge_markdown(judge_metrics)
    reports = output_root / "reports"
    atomic_json(reports / "aggregate.json", aggregate)
    atomic_text(reports / "aggregate.md", markdown)


def _judge_markdown(metrics: dict[str, Any]) -> str:
    return (
        "\n## Judge coverage\n\n"
        f"Eligible: {metrics['eligible']}  \nCompleted: {metrics['completed']}  \n"
        f"Failed: {metrics['failed']}  \nSkipped invalid: {metrics['skipped_invalid']}\n"
    )


def _write_matrices(root: Path, matrices: dict[str, dict[str, dict[str, int]]]) -> None:
    names = {
        "work_mode": "work-mode-confusion.csv",
        "last_activity": "last-activity-status-confusion.csv",
        "title_fit": "title-fit-confusion.csv",
    }
    for key, matrix in matrices.items():
        buffer = io.StringIO(newline="")
        columns = list(next(iter(matrix.values())))
        writer = csv.writer(buffer)
        writer.writerow(["expected\\actual", *columns])
        for label, counts in matrix.items():
            writer.writerow([label, *(counts[column] for column in columns)])
        value = buffer.getvalue()
        path = root / names[key]
        _require_matching_text(path, value)
        atomic_text(path, value)


def _aggregate_markdown(metrics: dict[str, Any]) -> str:
    runtime = metrics["runtime_reliability"]
    return (
        "# Private Development Evaluation\n\n"
        f"Expected: {runtime['expected']}  \nValid: {runtime['valid']}  \n"
        f"Failed: {runtime['failed']}\n\nNo composite score is produced.\n"
    )
