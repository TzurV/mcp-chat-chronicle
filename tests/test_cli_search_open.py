from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import chat_chronicle.cli as cli_module
from chat_chronicle.cli import app
from chat_chronicle.db import connect

runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


def _db_path(tmp_path: Path) -> Path:
    return tmp_path / "chronicle.db"


def _ingest(db_path: Path, source: Path) -> None:
    result = runner.invoke(
        app,
        [
            "ingest",
            str(source),
            "--db-path",
            str(db_path),
        ],
    )
    assert result.exit_code == 0, result.stdout


def _conversation_id(db_path: Path, provider: str) -> int:
    with connect(db_path) as conn:
        return int(
            conn.execute(
                "SELECT id FROM conversations WHERE provider = ?",
                (provider,),
            ).fetchone()[0]
        )


def test_search_finds_terms_from_ingested_chatgpt_claude_and_codex_fixtures(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    _ingest(db_path, FIXTURES / "chatgpt" / "minimal" / "conversations.json")
    _ingest(db_path, FIXTURES / "claude" / "minimal" / "conversations.json")
    _ingest(db_path, FIXTURES / "openai_codex" / "minimal" / "rollout-minimal.jsonl")

    chatgpt = runner.invoke(app, ["search", "docker", "--db-path", str(db_path)])
    claude = runner.invoke(app, ["search", "bm25", "--db-path", str(db_path)])
    codex = runner.invoke(app, ["search", "rollout", "--db-path", str(db_path)])

    assert chatgpt.exit_code == 0, chatgpt.stdout
    assert "chatgpt" in chatgpt.stdout
    assert "Docker networking notes" in chatgpt.stdout
    assert "chronicle open" in chatgpt.stdout
    assert "docker bridge network" in chatgpt.stdout
    assert claude.exit_code == 0, claude.stdout
    assert "claude" in claude.stdout
    assert "SQLite FTS5 ranking" in claude.stdout
    assert "bm25" in claude.stdout
    assert codex.exit_code == 0, codex.stdout
    assert "openai_codex" in codex.stdout
    assert "Each rollout file is JSONL" in codex.stdout


def test_search_no_results_and_empty_database_exit_zero(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)

    empty = runner.invoke(app, ["search", "nothing", "--db-path", str(db_path)])
    assert empty.exit_code == 0, empty.stdout
    assert "No results" in empty.stdout
    assert db_path.exists()

    _ingest(db_path, FIXTURES / "chatgpt" / "minimal" / "conversations.json")
    no_match = runner.invoke(app, ["search", "zzznomatch", "--db-path", str(db_path)])
    assert no_match.exit_code == 0, no_match.stdout
    assert "No results" in no_match.stdout


def test_search_cli_filters_and_limit_validation(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _ingest(db_path, FIXTURES / "chatgpt" / "minimal" / "conversations.json")
    _ingest(db_path, FIXTURES / "claude" / "minimal" / "conversations.json")
    with connect(db_path) as conn:
        chatgpt_id = int(
            conn.execute("SELECT id FROM conversations WHERE provider = 'chatgpt'").fetchone()[0]
        )
        conn.execute(
            "INSERT INTO enrichments (conversation_id, tags_json) VALUES (?, ?)",
            (chatgpt_id, '["networking"]'),
        )

    provider = runner.invoke(
        app,
        ["search", "docker", "--provider", "chatgpt", "--db-path", str(db_path)],
    )
    since = runner.invoke(
        app,
        ["search", "bm25", "--since", "2026-01-01", "--db-path", str(db_path)],
    )
    until = runner.invoke(
        app,
        ["search", "docker", "--until", "2026-01-01", "--db-path", str(db_path)],
    )
    tag = runner.invoke(
        app,
        ["search", "docker", "--tag", "networking", "--db-path", str(db_path)],
    )
    limited = runner.invoke(app, ["search", "docker", "--limit", "1", "--db-path", str(db_path)])
    invalid_limit = runner.invoke(
        app,
        ["search", "docker", "--limit", "0", "--db-path", str(db_path)],
    )

    assert provider.exit_code == 0, provider.stdout
    assert "chatgpt" in provider.stdout
    assert since.exit_code == 0, since.stdout
    assert "SQLite FTS5 ranking" in since.stdout
    assert until.exit_code == 0, until.stdout
    assert "Docker networking notes" in until.stdout
    assert tag.exit_code == 0, tag.stdout
    assert str(chatgpt_id) in tag.stdout
    assert limited.exit_code == 0, limited.stdout
    assert "Search results" in limited.stdout
    assert invalid_limit.exit_code != 0
    assert "Limit must be between 1 and 100" in invalid_limit.stderr


def test_search_empty_query_exits_nonzero(tmp_path: Path) -> None:
    result = runner.invoke(app, ["search", "   ", "--db-path", str(_db_path(tmp_path))])

    assert result.exit_code != 0
    assert "Search query cannot be empty" in result.stderr


def test_open_web_row_prints_url_and_calls_browser_helper(monkeypatch, tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _ingest(db_path, FIXTURES / "chatgpt" / "minimal" / "conversations.json")
    conversation_id = _conversation_id(db_path, "chatgpt")
    opened_urls: list[str] = []

    def fake_open(url: str) -> bool:
        opened_urls.append(url)
        return True

    monkeypatch.setattr(cli_module, "_open_url_in_browser", fake_open)

    result = runner.invoke(app, ["open", str(conversation_id), "--db-path", str(db_path)])

    assert result.exit_code == 0, result.stdout
    assert "provider: chatgpt" in result.stdout
    assert "Docker networking notes" in result.stdout
    assert "https://chatgpt.com/c/conv-minimal-1" in result.stdout
    assert opened_urls == ["https://chatgpt.com/c/conv-minimal-1"]


def test_open_local_row_prints_transcript_origin_path_and_resume_hint(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    _ingest(db_path, FIXTURES / "openai_codex" / "minimal" / "rollout-minimal.jsonl")
    conversation_id = _conversation_id(db_path, "openai_codex")
    with connect(db_path) as conn:
        conn.execute(
            "UPDATE conversations SET resume_hint = ? WHERE id = ?",
            ("codex resume codex-minimal-1", conversation_id),
        )

    result = runner.invoke(app, ["open", str(conversation_id), "--db-path", str(db_path)])

    assert result.exit_code == 0, result.stdout
    assert "provider: openai_codex" in result.stdout
    assert "origin_path:" in result.stdout
    assert "rollout-minimal.jsonl" in result.stdout
    assert "resume_hint: codex resume codex-minimal-1" in result.stdout
    assert "transcript:" in result.stdout
    assert "How do I list Codex session files?" in result.stdout
    assert "Each rollout file is JSONL" in result.stdout


def test_open_missing_id_and_unknown_id_exit_nonzero(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)

    missing = runner.invoke(app, ["open", "--db-path", str(db_path)])
    unknown = runner.invoke(app, ["open", "999", "--db-path", str(db_path)])

    assert missing.exit_code != 0
    assert "Missing argument" in missing.stderr
    assert unknown.exit_code != 0
    assert "Conversation not found: 999" in unknown.stderr
