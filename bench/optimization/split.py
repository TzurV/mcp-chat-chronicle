"""Outcome-blind deterministic 6/4 development split."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import Field, StrictInt, model_validator

from bench.io import atomic_json, digest
from bench.models import SelectionManifest, SelectionManifestConversation, StrictModel

from .models import OPTIMIZER_SPLIT_SEED

TRAIN_PROVIDER_COUNTS = {
    "chatgpt": 2,
    "openai_codex": 2,
    "claude": 1,
    "claude_code": 1,
}
TRAIN_LENGTH_COUNTS = {"short": 2, "medium": 2, "long": 2}


class OptimizationSplitManifest(StrictModel):
    format_version: Literal[1] = 1
    algorithm_version: Literal[OPTIMIZER_SPLIT_SEED] = OPTIMIZER_SPLIT_SEED
    role: Literal["optimizer-train", "optimizer-validation"]
    parent_development_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    ordered_conversations: list[SelectionManifestConversation]
    conversation_count: StrictInt
    expected_case_count: StrictInt
    provider_counts: dict[str, StrictInt]
    length_stratum_counts: dict[str, StrictInt]
    created_at_utc: str
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def accounting(self) -> OptimizationSplitManifest:
        expected = 6 if self.role == "optimizer-train" else 4
        if self.conversation_count != expected or len(self.ordered_conversations) != expected:
            raise ValueError("optimizer split conversation count mismatch")
        if self.expected_case_count != expected * 4:
            raise ValueError("optimizer split case count mismatch")
        if sum(self.provider_counts.values()) != expected:
            raise ValueError("optimizer split provider counts do not reconcile")
        if sum(self.length_stratum_counts.values()) != expected:
            raise ValueError("optimizer split length counts do not reconcile")
        payload = self.model_dump(mode="json", exclude={"manifest_sha256"})
        if digest(payload) != self.manifest_sha256:
            raise ValueError("optimizer split manifest hash mismatch")
        return self


def freeze_split(source: Path, destination: Path) -> tuple[Path, Path]:
    development = SelectionManifest.model_validate_json(source.read_text(encoding="utf-8"))
    train, validation = expected_split(development)
    destination.mkdir(parents=True, exist_ok=True)
    created = development.created_at_utc
    paths = []
    for role, entries in (("optimizer-train", train), ("optimizer-validation", validation)):
        manifest = build_split_manifest(development, role, entries, created)
        path = destination / f"{role}.json"
        if path.exists():
            existing = OptimizationSplitManifest.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            if existing != manifest:
                raise ValueError("frozen optimizer split already exists with different content")
        else:
            atomic_json(path, manifest.model_dump(mode="json"))
        paths.append(path)
    return paths[0], paths[1]


def expected_split(
    development: SelectionManifest,
) -> tuple[list[SelectionManifestConversation], list[SelectionManifestConversation]]:
    if development.role != "development" or development.conversation_count != 10:
        raise ValueError(
            "optimizer split requires the accepted ten-conversation development manifest"
        )
    feasible = []
    for indexes in itertools.combinations(range(10), 6):
        entries = [development.ordered_conversations[index] for index in indexes]
        if Counter(entry.provider for entry in entries) != TRAIN_PROVIDER_COUNTS:
            continue
        if Counter(entry.length_stratum for entry in entries) != TRAIN_LENGTH_COUNTS:
            continue
        identities = [entry.conversation_identity for entry in entries]
        choice = hashlib.sha256(
            (OPTIMIZER_SPLIT_SEED + "\n" + json.dumps(identities, separators=(",", ":"))).encode()
        ).hexdigest()
        feasible.append((choice, indexes))
    if not feasible:
        raise ValueError("no split satisfies the predeclared provider and length quotas")
    train_indexes = set(min(feasible)[1])
    train = [
        item
        for index, item in enumerate(development.ordered_conversations)
        if index in train_indexes
    ]
    validation = [
        item
        for index, item in enumerate(development.ordered_conversations)
        if index not in train_indexes
    ]
    return train, validation


def build_split_manifest(
    development: SelectionManifest,
    role: Literal["optimizer-train", "optimizer-validation"],
    entries: list[SelectionManifestConversation],
    created_at_utc: str,
) -> OptimizationSplitManifest:
    payload = {
        "format_version": 1,
        "algorithm_version": OPTIMIZER_SPLIT_SEED,
        "role": role,
        "parent_development_manifest_sha256": development.manifest_sha256,
        "ordered_conversations": [item.model_dump(mode="json") for item in entries],
        "conversation_count": len(entries),
        "expected_case_count": len(entries) * 4,
        "provider_counts": dict(sorted(Counter(item.provider for item in entries).items())),
        "length_stratum_counts": dict(
            sorted(Counter(item.length_stratum for item in entries).items())
        ),
        "created_at_utc": created_at_utc,
    }
    return OptimizationSplitManifest.model_validate({**payload, "manifest_sha256": digest(payload)})
