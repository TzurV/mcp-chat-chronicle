"""Strict read-only loaders for accepted WP-5.1.2B directory envelopes."""

from __future__ import annotations

import re
from pathlib import Path

from chat_chronicle.ai import canonical_hash

from .models import TASK_ORDER, InputEnvelope, ReferenceEnvelope

_CASE_NAME = re.compile(r"c([0-9]{3})\.json")


def load_inputs(root: Path, expected: int) -> list[InputEnvelope]:
    if not root.is_dir():
        raise ValueError("accepted input directory is missing")
    files = sorted(root.glob("*.json"))
    expected_names = [f"c{index:03d}.json" for index in range(1, expected + 1)]
    if [item.name for item in files] != expected_names:
        raise ValueError("accepted inputs are missing, extra, or misordered")
    values = [InputEnvelope.model_validate_json(path.read_text(encoding="utf-8")) for path in files]
    if [item.selection_index for item in values] != list(range(1, expected + 1)):
        raise ValueError("accepted input selection order mismatch")
    if len({item.case_group_id for item in values}) != expected:
        raise ValueError("duplicate accepted input case group")
    for attribute in (
        "format_version",
        "corpus_version",
        "snapshot_hash_reference",
        "task_catalog_hash_reference",
    ):
        if len({getattr(item, attribute) for item in values}) != 1:
            raise ValueError("accepted input corpus authority is inconsistent")
    for value in values:
        overview_hash = canonical_hash(
            {
                "selector": value.overview.selector,
                "selector_version": value.overview.selector_version,
                "selected_message_ids": value.overview.selected_message_ids,
                "transcript": value.overview.transcript,
                "source_title": value.source_title,
                "start_date": value.start_date,
                "last_active_date": value.last_active_date,
            }
        )
        recent_hash = canonical_hash(
            {
                "selector": value.recent.selector,
                "selector_version": value.recent.selector_version,
                "selected_message_ids": value.recent.selected_message_ids,
                "transcript": value.recent.transcript,
            }
        )
        if (
            overview_hash != value.overview.canonical_input_hash
            or recent_hash != value.recent.canonical_input_hash
        ):
            raise ValueError("accepted selector canonical input hash mismatch")
        for selector in (value.overview, value.recent):
            if len(selector.selected_message_ids) != len(set(selector.selected_message_ids)):
                raise ValueError("accepted selector contains duplicate evidence IDs")
    return values


def load_references(root: Path, inputs: list[InputEnvelope]) -> dict[str, ReferenceEnvelope]:
    expected_names = [f"c{index:03d}.json" for index in range(1, len(inputs) + 1)]
    result: dict[str, ReferenceEnvelope] = {}
    task_dirs = (
        sorted(item.name for item in root.iterdir() if item.is_dir()) if root.is_dir() else []
    )
    if task_dirs != sorted(TASK_ORDER):
        raise ValueError("reference task directories are missing or extra")
    for task in TASK_ORDER:
        files = sorted((root / task).glob("*.json"))
        if [item.name for item in files] != expected_names:
            raise ValueError("references are missing, extra, or misordered")
        for index, path in enumerate(files):
            value = ReferenceEnvelope.model_validate_json(path.read_text(encoding="utf-8"))
            source = inputs[index]
            selector = source.recent if task == "last-activity" else source.overview
            if (
                value.task_name != task
                or value.case_group_id != source.case_group_id
                or value.source_conversation_id != source.source_conversation_id
                or value.input_selector != selector.selector
                or value.selector_version != selector.selector_version
                or value.input_hash != selector.canonical_input_hash
                or value.status != "success"
            ):
                raise ValueError("reference authority identity mismatch")
            result[f"c{index + 1:03d}--{task}"] = value
    return result
