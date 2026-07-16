"""Read-only local source inventory for ``chronicle scan-local``.

The scanner intentionally performs shallow filesystem checks only. It reports
whether expected export folders or local stores appear to contain recognizable
source files, but it does not parse transcripts, create directories, or touch
the database.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from chat_chronicle.config import ChronicleConfig, default_config, resolve_path

STATUS_FOUND = "found"
STATUS_MISSING = "missing"
STATUS_EMPTY = "empty"
STATUS_EXPERIMENTAL = "experimental"
STATUS_ERROR = "error"

KIND_OFFICIAL_EXPORT = "official_export"
KIND_LOCAL_STORE = "local_store"
KIND_PLANNED_LOCAL_STORE = "planned_local_store"


@dataclass(frozen=True)
class SourceInventoryRow:
    provider: str
    kind: str
    path: Path
    status: str
    notes: str


@dataclass(frozen=True)
class _SourceDefinition:
    provider: str
    kind: str
    path: Path
    detector: Callable[[Path], bool] | None
    planned: bool = False


def scan_sources(
    *,
    config: ChronicleConfig | None = None,
    base_dir: Path | None = None,
    exports_root: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> list[SourceInventoryRow]:
    """Return source inventory rows for supported and planned defaults.

    ``exports_root`` overrides the ChatGPT/Claude export folder root. Other
    paths come from config when present, otherwise from built-in defaults.
    """

    base = (base_dir or Path.cwd()).resolve()
    effective_config = config or default_config()
    definitions = _build_definitions(
        effective_config,
        base_dir=base,
        exports_root=exports_root,
        env=os.environ if env is None else env,
    )
    return [_inspect_source(definition) for definition in definitions]


def _build_definitions(
    config: ChronicleConfig,
    *,
    base_dir: Path,
    exports_root: Path | None,
    env: Mapping[str, str],
) -> list[_SourceDefinition]:
    root = _resolve_optional_root(exports_root, base_dir)
    chatgpt_path = (
        root / "openai"
        if root is not None
        else _configured_source_path(config, "chatgpt", base_dir, fallback="exports/openai")
    )
    claude_path = (
        root / "claude"
        if root is not None
        else _configured_source_path(config, "claude", base_dir, fallback="exports/claude")
    )

    return [
        _SourceDefinition(
            provider="chatgpt",
            kind=KIND_OFFICIAL_EXPORT,
            path=chatgpt_path,
            detector=_has_openai_export_signature,
        ),
        _SourceDefinition(
            provider="claude",
            kind=KIND_OFFICIAL_EXPORT,
            path=claude_path,
            detector=_has_claude_export_signature,
        ),
        _SourceDefinition(
            provider="openai_codex",
            kind=KIND_LOCAL_STORE,
            path=_configured_source_path(
                config, "openai_codex", base_dir, fallback="${USERPROFILE}/.codex"
            ),
            detector=_has_codex_signature,
        ),
        _SourceDefinition(
            provider="claude_code",
            kind=KIND_LOCAL_STORE,
            path=_configured_source_path(
                config,
                "claude_code",
                base_dir,
                fallback="${USERPROFILE}/.claude/projects",
            ),
            detector=_has_claude_code_signature,
        ),
        _SourceDefinition(
            provider="cursor",
            kind=KIND_PLANNED_LOCAL_STORE,
            path=_env_path(env, "APPDATA", "Cursor/User/workspaceStorage"),
            detector=None,
            planned=True,
        ),
        _SourceDefinition(
            provider="copilot_vscode",
            kind=KIND_PLANNED_LOCAL_STORE,
            path=_env_path(env, "APPDATA", "Code/User/workspaceStorage"),
            detector=None,
            planned=True,
        ),
    ]


def _inspect_source(definition: _SourceDefinition) -> SourceInventoryRow:
    try:
        if not definition.path.exists():
            return SourceInventoryRow(
                provider=definition.provider,
                kind=definition.kind,
                path=definition.path,
                status=STATUS_MISSING,
                notes=_missing_note(definition),
            )
        if definition.planned:
            return SourceInventoryRow(
                provider=definition.provider,
                kind=definition.kind,
                path=definition.path,
                status=STATUS_EXPERIMENTAL,
                notes="planned extractor; not ingested by collect yet",
            )
        detector = definition.detector
        if detector is not None and detector(definition.path):
            return SourceInventoryRow(
                provider=definition.provider,
                kind=definition.kind,
                path=definition.path,
                status=STATUS_FOUND,
                notes=_found_note(definition),
            )
        return SourceInventoryRow(
            provider=definition.provider,
            kind=definition.kind,
            path=definition.path,
            status=STATUS_EMPTY,
            notes=_empty_note(definition),
        )
    except OSError as exc:
        return SourceInventoryRow(
            provider=definition.provider,
            kind=definition.kind,
            path=definition.path,
            status=STATUS_ERROR,
            notes=f"{type(exc).__name__}: {exc}",
        )


def _configured_source_path(
    config: ChronicleConfig,
    provider: str,
    base_dir: Path,
    *,
    fallback: str,
) -> Path:
    for source in config.sources.values():
        if source.provider == provider:
            return resolve_path(source.path, base_dir).resolve()
    return resolve_path(fallback, base_dir).resolve()


def _resolve_optional_root(root: Path | None, base_dir: Path) -> Path | None:
    if root is None:
        return None
    candidate = root.expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    return candidate.resolve()


def _env_path(env: Mapping[str, str], var_name: str, suffix: str) -> Path:
    root = env.get(var_name)
    if not root and var_name == "APPDATA":
        user_profile = env.get("USERPROFILE") or env.get("HOME")
        if user_profile:
            root = str(Path(user_profile) / "AppData" / "Roaming")
    if not root:
        root = str(Path.home())
    return (Path(root).expanduser() / Path(suffix)).resolve()


def _has_openai_export_signature(path: Path) -> bool:
    return _has_export_signature(path, split_files=True)


def _has_claude_export_signature(path: Path) -> bool:
    return _has_export_signature(path, split_files=False)


def _has_export_signature(path: Path, *, split_files: bool) -> bool:
    if path.is_file():
        return _is_export_file(path, split_files=split_files)

    for candidate in _iter_shallow(path):
        if candidate.is_file() and _is_export_file(candidate, split_files=split_files):
            return True
        if candidate.is_dir():
            for nested in _iter_shallow(candidate):
                if nested.is_file() and _is_export_file(nested, split_files=split_files):
                    return True
    return False


def _is_export_file(path: Path, *, split_files: bool) -> bool:
    name = path.name.lower()
    if path.suffix.lower() == ".zip":
        return True
    if name == "conversations.json":
        return True
    return split_files and name.startswith("conversations-") and name.endswith(".json")


def _has_codex_signature(path: Path) -> bool:
    if path.is_file():
        return path.suffix.lower() == ".jsonl" and path.name.startswith("rollout-")

    if (path / "session_index.jsonl").is_file():
        return True
    if (path / "sessions").is_dir():
        return True
    if any(candidate.name.startswith("rollout-") for candidate in _iter_limited(path, "*.jsonl")):
        return True
    sessions = path / "sessions"
    return sessions.is_dir() and any(
        candidate.name.startswith("rollout-") for candidate in _iter_limited(sessions, "*.jsonl")
    )


def _has_claude_code_signature(path: Path) -> bool:
    if path.is_file():
        return path.suffix.lower() == ".jsonl"
    return any(True for _ in _iter_limited(path, "*.jsonl"))


def _iter_shallow(path: Path) -> list[Path]:
    try:
        return list(path.iterdir())
    except OSError:
        return []


def _iter_limited(path: Path, pattern: str, *, limit: int = 200) -> list[Path]:
    try:
        results: list[Path] = []
        for candidate in path.rglob(pattern):
            results.append(candidate)
            if len(results) >= limit:
                break
        return results
    except OSError:
        return []


def _missing_note(definition: _SourceDefinition) -> str:
    if definition.kind == KIND_OFFICIAL_EXPORT:
        return "missing; request/export history from provider"
    if definition.planned:
        return "missing; planned source not found"
    return "missing; local store not found"


def _found_note(definition: _SourceDefinition) -> str:
    if definition.kind == KIND_OFFICIAL_EXPORT:
        return f"ingest: chronicle ingest {definition.path} --provider {definition.provider}"
    return f"ingest: chronicle ingest {definition.path} --provider {definition.provider}"


def _empty_note(definition: _SourceDefinition) -> str:
    if definition.kind == KIND_OFFICIAL_EXPORT:
        return "folder exists; add export ZIP or conversations JSON"
    return "path exists; no shallow local-store signature found"
