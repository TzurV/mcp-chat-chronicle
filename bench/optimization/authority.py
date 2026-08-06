"""Read-only development authority validation for optimizer execution."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from bench.core import _conversation_identity, _manifest_payload, _schema_spec
from bench.io import digest
from bench.loaders import _validate_inputs
from bench.models import (
    TASK_ORDER,
    InputEnvelope,
    ReferenceEnvelope,
    SelectionManifest,
)

from .models import OptimizationConfig, resolve_config_path
from .split import OptimizationSplitManifest, build_split_manifest, expected_split


class VerifiedAuthority:
    def __init__(
        self,
        development: SelectionManifest,
        train: OptimizationSplitManifest,
        validation: OptimizationSplitManifest,
        inputs: list[InputEnvelope],
        references: dict[str, ReferenceEnvelope],
    ) -> None:
        self.development = development
        self.train = train
        self.validation = validation
        self.inputs = inputs
        self.references = references


def verify_authority(config: OptimizationConfig, config_path: Path) -> VerifiedAuthority:
    development_path = resolve_config_path(config_path, config.paths.development_manifest)
    development = SelectionManifest.model_validate_json(
        development_path.read_text(encoding="utf-8")
    )
    calculated = digest(_manifest_payload(development))
    if (
        development.role != "development"
        or development.conversation_count != 10
        or development.expected_case_count != 40
        or development.manifest_sha256 != calculated
        or config.development_manifest_sha256 != calculated
    ):
        raise ValueError("accepted development manifest identity mismatch")
    indexes = [item.authority_index for item in development.ordered_conversations]
    identities = [item.conversation_identity for item in development.ordered_conversations]
    if len(indexes) != len(set(indexes)) or len(identities) != len(set(identities)):
        raise ValueError("accepted development manifest contains duplicate conversations")

    train = _load_split(config, config_path, config.train_manifest.path)
    validation = _load_split(config, config_path, config.validation_manifest.path)
    if train.manifest_sha256 != config.train_manifest.sha256:
        raise ValueError("optimizer train manifest binding mismatch")
    if validation.manifest_sha256 != config.validation_manifest.sha256:
        raise ValueError("optimizer validation manifest binding mismatch")
    if (
        train.parent_development_manifest_sha256 != calculated
        or validation.parent_development_manifest_sha256 != calculated
    ):
        raise ValueError("optimizer split has a foreign development parent")
    train_ids = [item.conversation_identity for item in train.ordered_conversations]
    validation_ids = [item.conversation_identity for item in validation.ordered_conversations]
    if set(train_ids) & set(validation_ids):
        raise ValueError("optimizer train and validation manifests overlap")
    if train_ids + validation_ids and set(train_ids + validation_ids) != set(identities):
        raise ValueError("optimizer split union differs from accepted development authority")
    expected_train, expected_validation = expected_split(development)
    expected_manifests = (
        build_split_manifest(
            development, "optimizer-train", expected_train, development.created_at_utc
        ),
        build_split_manifest(
            development,
            "optimizer-validation",
            expected_validation,
            development.created_at_utc,
        ),
    )
    if train != expected_manifests[0] or validation != expected_manifests[1]:
        raise ValueError("optimizer split order or deterministic selection is invalid")

    inputs = _load_selected_inputs(
        resolve_config_path(config_path, config.paths.inputs), development
    )
    references = _load_selected_references(
        resolve_config_path(config_path, config.paths.references),
        inputs,
        config.accepted_task_catalog_sha256,
    )
    return VerifiedAuthority(development, train, validation, inputs, references)


def _load_split(
    config: OptimizationConfig, config_path: Path, value: str
) -> OptimizationSplitManifest:
    return OptimizationSplitManifest.model_validate_json(
        resolve_config_path(config_path, value).read_text(encoding="utf-8")
    )


def _load_selected_inputs(root: Path, manifest: SelectionManifest) -> list[InputEnvelope]:
    expected_names = [
        f"c{item.authority_index:03d}.json" for item in manifest.ordered_conversations
    ]
    files = sorted(root.glob("*.json")) if root.is_dir() else []
    if sorted(path.name for path in files) != sorted(expected_names):
        raise ValueError("optimizer development inputs are missing, extra, or substituted")
    inputs = [
        InputEnvelope.model_validate_json(
            (root / f"c{entry.authority_index:03d}.json").read_text(encoding="utf-8")
        )
        for entry in manifest.ordered_conversations
    ]
    _validate_inputs(inputs, [entry.authority_index for entry in manifest.ordered_conversations])
    for entry, source in zip(manifest.ordered_conversations, inputs, strict=True):
        if _conversation_identity(source) != entry.conversation_identity:
            raise ValueError("optimizer input is outside accepted development authority")
        if source.provider != entry.provider:
            raise ValueError("optimizer input provider metadata mismatch")
    return inputs


def _load_selected_references(
    root: Path,
    inputs: list[InputEnvelope],
    task_catalog_sha256: str,
) -> dict[str, ReferenceEnvelope]:
    expected_names = sorted(f"c{source.selection_index:03d}.json" for source in inputs)
    task_dirs = (
        sorted(path.name for path in root.iterdir() if path.is_dir()) if root.is_dir() else []
    )
    if task_dirs != sorted(TASK_ORDER):
        raise ValueError("optimizer reference task directories are missing or extra")
    references: dict[str, ReferenceEnvelope] = {}
    for task in TASK_ORDER:
        files = sorted((root / task).glob("*.json"))
        if sorted(path.name for path in files) != expected_names:
            raise ValueError("optimizer references are missing, extra, or substituted")
        for source in inputs:
            alias = f"c{source.selection_index:03d}--{task}"
            reference = ReferenceEnvelope.model_validate_json(
                (root / task / f"c{source.selection_index:03d}.json").read_text(encoding="utf-8")
            )
            selector = source.recent if task == "last-activity" else source.overview
            spec = _schema_spec(reference.output_schema)
            if (
                reference.task_name != task
                or reference.case_group_id != source.case_group_id
                or reference.source_conversation_id != source.source_conversation_id
                or reference.input_selector != selector.selector
                or reference.selector_version != selector.selector_version
                or reference.input_hash != selector.canonical_input_hash
                or reference.task_catalog_hash != task_catalog_sha256
                or source.task_catalog_hash_reference != task_catalog_sha256
                or reference.provider_schema_version != spec.version
                or reference.finalizer_version != spec.finalizer_version
                or reference.status != "success"
            ):
                raise ValueError("optimizer reference authority identity mismatch")
            canonical = spec.final_model.model_validate(reference.output).model_dump(mode="json")
            if canonical != reference.output:
                raise ValueError("optimizer reference output is not canonical")
            if not set(canonical.get("evidence_message_ids", [])) <= set(
                selector.selected_message_ids
            ):
                raise ValueError("optimizer reference evidence is outside selected input")
            references[alias] = reference
    if Counter(reference.task_name for reference in references.values()) != Counter(
        {task: len(inputs) for task in TASK_ORDER}
    ):
        raise ValueError("optimizer reference case counts do not reconcile")
    return references
