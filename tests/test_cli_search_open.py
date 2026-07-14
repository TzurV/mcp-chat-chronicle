from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import chat_chronicle.cli as cli_module
from chat_chronicle.cli import app
from chat_chronicle.db import connect, rebuild_fts, upsert_conversation
from chat_chronicle.models import Conversation, Message

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


def _insert_search_conversation(
    db_path: Path,
    provider_conv_id: str,
    body: str,
    *,
    provider: str = "chatgpt",
    title: str = "Synthetic Search Chat",
) -> int:
    with connect(db_path) as conn:
        inserted = upsert_conversation(
            conn,
            None,
            Conversation(
                provider=provider,
                provider_conv_id=provider_conv_id,
                title=title,
                url="https://chatgpt.com/c/synthetic"
                if provider == "chatgpt"
                else None,
                messages=[
                    Message(
                        role="user",
                        body=body,
                        seq=0,
                    )
                ],
            ),
        )
        rebuild_fts(conn)
        return inserted.conversation_id


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


def test_search_phrase_cli_returns_exact_phrase_without_broad_hint(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    exact_id = _insert_search_conversation(
        db_path,
        "cli-phrase-exact",
        "The instruction says YOU are the MANAGER for this review.",
        provider="openai_codex",
    )
    _insert_search_conversation(
        db_path,
        "cli-phrase-partial",
        "YOU are reviewing unrelated filler before the MANAGER arrives.",
        provider="openai_codex",
    )

    result = runner.invoke(
        app,
        [
            "search",
            "--phrase",
            "YOU are the MANAGER",
            "--provider",
            "openai_codex",
            "--db-path",
            str(db_path),
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert str(exact_id) in result.stdout
    assert "cli-phrase-partial" not in result.stdout
    assert "Hint: this was a broad token search" not in result.stdout


def test_search_broad_query_guidance_hint_and_one_word_suppression(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    _insert_search_conversation(
        db_path,
        "cli-broad-hint",
        "YOU are reviewing unrelated filler before the MANAGER arrives.",
    )

    broad = runner.invoke(
        app,
        ["search", "YOU are the MANAGER", "--db-path", str(db_path)],
    )
    one_word = runner.invoke(app, ["search", "MANAGER", "--db-path", str(db_path)])
    advanced = runner.invoke(app, ["search", '"YOU are the MANAGER"', "--db-path", str(db_path)])

    assert broad.exit_code == 0, broad.stdout
    assert "Hint: this was a broad token search" in broad.stdout
    assert one_word.exit_code == 0, one_word.stdout
    assert "Hint: this was a broad token search" not in one_word.stdout
    assert advanced.exit_code == 0, advanced.stdout
    assert "Hint: this was a broad token search" not in advanced.stdout


def test_search_broad_query_guidance_hint_after_no_results(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)

    result = runner.invoke(
        app,
        ["search", "YOU are the MANAGER", "--db-path", str(db_path)],
    )

    assert result.exit_code == 0, result.stdout
    assert "No results" in result.stdout
    assert "Hint: this was a broad token search" in result.stdout


def test_recent_cli_lists_url_and_local_rows_with_filters(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _ingest(db_path, FIXTURES / "chatgpt" / "minimal" / "conversations.json")
    _ingest(db_path, FIXTURES / "openai_codex" / "minimal" / "rollout-minimal.jsonl")
    with connect(db_path) as conn:
        conn.execute(
            """
            UPDATE conversations
            SET created_at = ?, updated_at = ?
            WHERE provider = 'chatgpt'
            """,
            ("2026-01-01T00:00:00.000000Z", "2026-03-01T00:00:00.000000Z"),
        )
        conn.execute(
            """
            UPDATE conversations
            SET created_at = ?, updated_at = ?, resume_hint = ?
            WHERE provider = 'openai_codex'
            """,
            (
                "2026-02-01T00:00:00.000000Z",
                None,
                "codex resume codex-minimal-1",
            ),
        )

    all_recent = runner.invoke(app, ["recent", "-n", "5", "--db-path", str(db_path)])
    provider_recent = runner.invoke(
        app,
        ["recent", "-n", "5", "--provider", "chatgpt", "--db-path", str(db_path)],
    )
    window_recent = runner.invoke(
        app,
        [
            "recent",
            "-n",
            "5",
            "--since",
            "2026-02-01",
            "--until",
            "2026-02-28",
            "--db-path",
            str(db_path),
        ],
    )

    assert all_recent.exit_code == 0, all_recent.stdout
    assert "Recent conversations" in all_recent.stdout
    assert "ID" in all_recent.stdout
    assert "Date" in all_recent.stdout
    assert "Provider" in all_recent.stdout
    assert "Title" in all_recent.stdout
    assert "URL" in all_recent.stdout
    assert "https://chatgpt." in all_recent.stdout
    assert "com/c/conv-minim" in all_recent.stdout
    assert "al-1" in all_recent.stdout
    assert "local:" in all_recent.stdout
    assert "rollout-minimal." in all_recent.stdout
    assert "jsonl" in all_recent.stdout
    assert all_recent.stdout.index("chatgpt") < all_recent.stdout.index("openai_codex")
    assert "recent " not in all_recent.stdout
    assert "default maximum is 10" not in all_recent.stdout

    assert provider_recent.exit_code == 0, provider_recent.stdout
    assert "chatgpt" in provider_recent.stdout
    assert "openai_codex" not in provider_recent.stdout

    assert window_recent.exit_code == 0, window_recent.stdout
    assert "openai_codex" in window_recent.stdout
    assert "chatgpt" not in window_recent.stdout


def test_recent_cli_default_limit_prints_hint(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _ingest(db_path, FIXTURES / "chatgpt" / "minimal" / "conversations.json")

    result = runner.invoke(app, ["recent", "--db-path", str(db_path)])

    assert result.exit_code == 0, result.stdout
    assert "Recent conversations" in result.stdout
    assert "default maximum is 10" in result.stdout
    assert "Use -n/--limit to increase" in result.stdout


def test_recent_cli_empty_db_and_limit_validation(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)

    empty = runner.invoke(app, ["recent", "--db-path", str(db_path)])
    invalid_limit = runner.invoke(app, ["recent", "-n", "0", "--db-path", str(db_path)])

    assert empty.exit_code == 0, empty.stdout
    assert "No conversations" in empty.stdout
    assert db_path.exists()
    assert invalid_limit.exit_code != 0
    assert "Limit must be between 1 and 100" in invalid_limit.stderr


def test_chronicle_help_includes_recent_command() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0, result.stdout
    assert "recent" in result.stdout
    assert "List the most recently active conversations" in result.stdout


def test_search_help_documents_phrase_option() -> None:
    # Typer/Rich renders --help through its own console; on a narrow terminal
    # (the 80-col fallback used under CI) option names wrap and break substring
    # checks. Pin a wide width via COLUMNS so the help text is stable.
    result = runner.invoke(app, ["search", "--help"], env={"COLUMNS": "200"})

    assert result.exit_code == 0, result.stdout
    assert "--phrase" in result.stdout
    assert "exact phrase" in result.stdout


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
