"""Collect workflow: ingest all enabled configured sources (WP-1.6).

This is an orchestration layer over accepted adapters and the directory-sweep
behavior already implemented for ``chronicle ingest``. It does not parse
transcripts itself; it decides which configured sources to look at, resolves
their paths, and delegates ingestion.

To keep this module free of a circular import with the CLI, the concrete
ingest primitives (single-source ingest, directory discovery, and directory
ingest) are injected by the caller via ``CollectHooks``.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from chat_chronicle.config import (
    SUPPORTED_KINDS,
    SUPPORTED_PROVIDERS,
    ChronicleConfig,
    SourceConfig,
    resolve_path,
)
from chat_chronicle.models import IngestRunSummary

_KIND_OFFICIAL_EXPORT = "official_export"
_KIND_LOCAL_STORE = "local_store"


@dataclass
class SourceCollectResult:
    """Outcome of collecting one configured source entry."""

    name: str
    provider: str
    kind: str
    path: Path
    status: str
    note: str = ""
    seen: int = 0
    added: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0


@dataclass
class CollectReport:
    """Aggregate outcome across every configured source considered."""

    results: list[SourceCollectResult] = field(default_factory=list)

    @property
    def collected(self) -> list[SourceCollectResult]:
        return [r for r in self.results if r.status == "collected"]

    @property
    def total_seen(self) -> int:
        return sum(r.seen for r in self.collected)

    @property
    def total_added(self) -> int:
        return sum(r.added for r in self.collected)

    @property
    def total_updated(self) -> int:
        return sum(r.updated for r in self.collected)

    @property
    def total_skipped(self) -> int:
        return sum(r.skipped for r in self.collected)

    @property
    def total_errors(self) -> int:
        return sum(r.errors for r in self.collected)


# (provider, resolved_path) -> IngestRunSummary. Raises on hard adapter failure.
IngestOneFn = Callable[[sqlite3.Connection, str, Path], IngestRunSummary]
# resolved_dir -> list[IngestRunSummary] for each discovered child source.
IngestDirFn = Callable[[sqlite3.Connection, Path], list[IngestRunSummary]]


@dataclass
class CollectHooks:
    ingest_one: IngestOneFn
    ingest_directory: IngestDirFn
    rebuild_fts: Callable[[sqlite3.Connection], None]


def enabled_engine(config: ChronicleConfig, name: str) -> bool:
    """Return whether an engine is enabled; unknown engines default to enabled."""
    engine = config.engines.get(name)
    return True if engine is None else engine.enabled


def iter_enabled_sources(config: ChronicleConfig) -> Iterable[tuple[str, SourceConfig]]:
    """Yield ``(name, source)`` for sources whose engine is enabled.

    Sources are ordered by name for stable, predictable output.
    """
    for name in sorted(config.sources):
        if enabled_engine(config, name):
            yield name, config.sources[name]


def collect(
    conn: sqlite3.Connection,
    config: ChronicleConfig,
    hooks: CollectHooks,
    *,
    base_dir: Path | None = None,
) -> CollectReport:
    """Ingest every enabled configured source and return an aggregate report.

    Missing paths and unsupported providers/kinds are reported and skipped, not
    fatal. FTS is rebuilt once if at least one source was collected.
    """
    report = CollectReport()
    any_collected = False

    for name, source in iter_enabled_sources(config):
        result = _collect_one(conn, name, source, hooks, base_dir=base_dir)
        report.results.append(result)
        if result.status == "collected":
            any_collected = True

    if any_collected:
        hooks.rebuild_fts(conn)

    return report


def _collect_one(
    conn: sqlite3.Connection,
    name: str,
    source: SourceConfig,
    hooks: CollectHooks,
    *,
    base_dir: Path | None,
) -> SourceCollectResult:
    resolved = resolve_path(source.path, base_dir)
    base = SourceCollectResult(
        name=name,
        provider=source.provider,
        kind=source.kind,
        path=resolved,
        status="skipped",
    )

    if source.provider not in SUPPORTED_PROVIDERS:
        base.status = "unsupported"
        base.note = f"no importer/extractor for provider '{source.provider}' yet"
        return base

    if source.kind not in SUPPORTED_KINDS:
        base.status = "unsupported"
        base.note = f"unsupported source kind '{source.kind}'"
        return base

    if not resolved.exists():
        base.status = "missing"
        base.note = _missing_note(source, resolved)
        return base

    try:
        if source.kind == _KIND_OFFICIAL_EXPORT:
            summaries = hooks.ingest_directory(conn, resolved)
            if not summaries:
                base.status = "empty"
                base.note = "no supported sources found under this path"
                return base
            _apply_summaries(base, summaries)
        else:  # local_store: ingest the configured store as one source
            summary = hooks.ingest_one(conn, source.provider, resolved)
            _apply_summaries(base, [summary])
    except Exception as exc:  # adapter/discovery hard failure — report, don't crash
        base.status = "error"
        base.note = f"{type(exc).__name__}: {exc}"
        return base

    base.status = "collected"
    return base


def _apply_summaries(result: SourceCollectResult, summaries: list[IngestRunSummary]) -> None:
    for summary in summaries:
        result.seen += summary.conversations_seen
        result.added += summary.added
        result.updated += summary.updated
        result.skipped += summary.skipped
        result.errors += len(summary.errors)


def _missing_note(source: SourceConfig, resolved: Path) -> str:
    if source.kind == _KIND_OFFICIAL_EXPORT:
        return f"missing; export/download history into {resolved}"
    return f"missing; local store not found at {resolved}"
