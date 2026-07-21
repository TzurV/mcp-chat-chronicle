"""Fail-closed path resolution for private evaluation outputs."""

from __future__ import annotations

from pathlib import Path

from .models import EvaluationConfig


def resolve_root(config: EvaluationConfig, config_path: Path) -> Path:
    value = Path(config.paths.root)
    root = (value if value.is_absolute() else config_path.parent / value).resolve()
    repository_root = Path(__file__).resolve().parents[1]
    git_root = repository_root / ".git"
    if (
        root == Path(root.anchor)
        or root == config_path.parent.resolve()
        or root == repository_root
        or root == git_root
        or git_root in root.parents
    ):
        raise ValueError("evaluation root cannot be a drive, filesystem, or repository root")
    if root.name.lower() in {".git", "inputs", "references", "source"}:
        raise ValueError("evaluation root targets a protected directory")
    return root


def resolve_member(
    config: EvaluationConfig, config_path: Path, value: str, *, output: bool
) -> Path:
    root = resolve_root(config, config_path)
    raw = Path(value)
    path = (raw if raw.is_absolute() else root / raw).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("evaluation path escapes configured private root") from exc
    if path == root or path.name.lower() == ".git":
        raise ValueError("evaluation output cannot target a protected root")
    source = (root / config.paths.source).resolve()
    references = (root / config.paths.references).resolve()
    if output and any(
        path == item or path in item.parents or item in path.parents
        for item in (source, references)
    ):
        raise ValueError("evaluation input/output paths overlap")
    return path
