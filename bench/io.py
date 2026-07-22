"""Canonical serialization, atomic writes, and safe deterministic archives."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return digest_bytes(canonical_bytes(value))


def atomic_json(path: Path, value: Any) -> None:
    payload = canonical_bytes(value)
    if path.exists() and path.read_bytes() == payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        _replace_with_retry(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_text(path: Path, value: str) -> None:
    payload = value.encode("utf-8")
    if path.exists() and path.read_bytes() == payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        _replace_with_retry(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _replace_with_retry(source: str, destination: Path) -> None:
    """Tolerate brief Windows sharing violations during atomic finalization."""
    for attempt in range(5):
        try:
            os.replace(source, destination)
            return
        except OSError as exc:
            if getattr(exc, "winerror", None) not in {5, 32} or attempt == 4:
                raise
            time.sleep(0.05 * (attempt + 1))


def checksums(root: Path, *, excluded: set[str] | None = None) -> dict[str, str]:
    excluded = excluded or {"checksums.json"}
    return {
        path.relative_to(root).as_posix(): digest_bytes(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.relative_to(root).as_posix() not in excluded
    }


def write_checksums(root: Path) -> str:
    values = checksums(root)
    atomic_json(root / "checksums.json", values)
    return digest(values)


def verify_checksums(root: Path) -> str:
    expected = json.loads((root / "checksums.json").read_text(encoding="utf-8"))
    actual = checksums(root)
    if expected != actual:
        raise ValueError("package checksum validation failed")
    return digest(expected)


def deterministic_zip(root: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o100600 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
    return digest_bytes(destination.read_bytes())


def safe_extract(
    archive_path: Path,
    destination: Path,
    *,
    allowed_prefixes: tuple[str, ...] | None = None,
    max_files: int = 2_000,
    max_file_size: int = 2_000_000,
    max_total_size: int = 100_000_000,
) -> Path:
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("archive destination must be a fresh empty directory")
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        if len(infos) > max_files or sum(item.file_size for item in infos) > max_total_size:
            raise ValueError("archive size limits exceeded")
        seen: set[str] = set()
        files: set[str] = set()
        for info in archive.infolist():
            normalized_text = info.filename.replace("\\", "/")
            name = PurePosixPath(normalized_text)
            mode = info.external_attr >> 16
            lowered = normalized_text.casefold().rstrip("/")
            windows_absolute = bool(
                name.parts and ":" in name.parts[0]
            ) or normalized_text.startswith("//")
            if (
                name.is_absolute()
                or windows_absolute
                or ".." in name.parts
                or (mode & 0o170000) not in {0, 0o040000, 0o100000}
                or info.file_size > max_file_size
            ):
                raise ValueError("unsafe archive entry rejected")
            if lowered in seen:
                raise ValueError("duplicate or case-colliding archive entry rejected")
            seen.add(lowered)
            if not info.is_dir():
                if any(item.startswith(lowered + "/") for item in seen):
                    raise ValueError("archive file/directory collision rejected")
                files.add(lowered)
            parts = lowered.split("/")
            if any("/".join(parts[:index]) in files for index in range(1, len(parts))):
                raise ValueError("archive file/directory collision rejected")
            if allowed_prefixes and not any(
                normalized_text == prefix or normalized_text.startswith(prefix.rstrip("/") + "/")
                for prefix in allowed_prefixes
            ):
                raise ValueError("unexpected archive entry rejected")
        archive.extractall(destination)
    return destination
