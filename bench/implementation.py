"""Measured tracked implementation identity for remote generation."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImplementationIdentity:
    commit: str
    dirty_tracked: bool
    tracked_diff_sha256: str | None


def measure_implementation(repository: Path | None = None) -> ImplementationIdentity:
    root = (repository or Path(__file__).resolve().parents[1]).resolve()
    commit = _git(root, "rev-parse", "HEAD").decode().strip()
    status = _git(root, "status", "--porcelain", "--untracked-files=no")
    dirty = bool(status.strip())
    diff_hash = None
    if dirty:
        difference = _git(root, "diff", "--binary", "HEAD")
        diff_hash = hashlib.sha256(difference).hexdigest()
    return ImplementationIdentity(commit, dirty, diff_hash)


def _git(root: Path, *arguments: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("could not measure tracked implementation identity") from exc
