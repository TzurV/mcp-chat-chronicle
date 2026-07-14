"""Tests for the read-only ``chronicle scan-local`` inventory command."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from typer.testing import CliRunner

from chat_chronicle.cli import app

runner = CliRunner()


@pytest.fixture
def scan_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "profile"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.delenv("CHAT_CHRONICLE_DB", raising=False)
    yield tmp_path


def _run_scan(project: Path):
    return runner.invoke(app, ["scan-local", "--root", str(project / "exports")])


def test_scan_local_lists_expected_providers_and_missing_paths(
    scan_project: Path,
) -> None:
    result = _run_scan(scan_project)

    assert result.exit_code == 0, result.stdout
    for provider in (
        "chatgpt",
        "claude",
        "openai_codex",
        "claude_code",
        "cursor",
        "copilot_vscode",
    ):
        assert provider in result.stdout
    assert "missing" in result.stdout
    assert not (scan_project / ".chronicle" / "chronicle.db").exists()


def test_scan_local_detects_chatgpt_export_signature(scan_project: Path) -> None:
    export_dir = scan_project / "exports" / "openai"
    export_dir.mkdir(parents=True)
    (export_dir / "conversations-000.json").write_text("[]\n", encoding="utf-8")

    result = _run_scan(scan_project)

    assert result.exit_code == 0, result.stdout
    assert "chatgpt" in result.stdout
    assert "found" in result.stdout
    assert "chronicle ingest" in result.stdout


def test_scan_local_detects_claude_export_signature(scan_project: Path) -> None:
    export_dir = scan_project / "exports" / "claude"
    export_dir.mkdir(parents=True)
    (export_dir / "conversations.json").write_text("[]\n", encoding="utf-8")

    result = _run_scan(scan_project)

    assert result.exit_code == 0, result.stdout
    assert "claude" in result.stdout
    assert "found" in result.stdout


def test_scan_local_detects_openai_codex_store(scan_project: Path) -> None:
    codex_home = scan_project / "profile" / ".codex"
    (codex_home / "sessions" / "2026" / "07" / "14").mkdir(parents=True)
    (codex_home / "session_index.jsonl").write_text("{}\n", encoding="utf-8")

    result = _run_scan(scan_project)

    assert result.exit_code == 0, result.stdout
    assert "openai_codex" in result.stdout
    assert "found" in result.stdout
    assert "--provider openai_codex" in result.stdout


def test_scan_local_detects_claude_code_store(scan_project: Path) -> None:
    projects = scan_project / "profile" / ".claude" / "projects" / "synthetic-project"
    projects.mkdir(parents=True)
    (projects / "session.jsonl").write_text("{}\n", encoding="utf-8")

    result = _run_scan(scan_project)

    assert result.exit_code == 0, result.stdout
    assert "claude_code" in result.stdout
    assert "found" in result.stdout
    assert "--provider claude_code" in result.stdout


def test_scan_local_marks_cursor_and_copilot_paths_experimental(
    scan_project: Path,
) -> None:
    (scan_project / "appdata" / "Cursor" / "User" / "workspaceStorage").mkdir(
        parents=True
    )
    (scan_project / "appdata" / "Code" / "User" / "workspaceStorage").mkdir(
        parents=True
    )

    result = _run_scan(scan_project)

    assert result.exit_code == 0, result.stdout
    assert "cursor" in result.stdout
    assert "copilot_vscode" in result.stdout
    assert "experimental" in result.stdout
    assert "planned extractor" in result.stdout


def test_scan_local_does_not_modify_source_files(scan_project: Path) -> None:
    export_dir = scan_project / "exports" / "openai"
    export_dir.mkdir(parents=True)
    source_file = export_dir / "conversations.json"
    source_file.write_text("[]\n", encoding="utf-8")
    before_text = source_file.read_text(encoding="utf-8")
    before_mtime = source_file.stat().st_mtime_ns

    result = _run_scan(scan_project)

    assert result.exit_code == 0, result.stdout
    assert source_file.read_text(encoding="utf-8") == before_text
    assert source_file.stat().st_mtime_ns == before_mtime
