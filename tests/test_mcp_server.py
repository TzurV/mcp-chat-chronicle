from __future__ import annotations

import asyncio
import hashlib
import json
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from typer.testing import CliRunner

from chat_chronicle.cli import app
from chat_chronicle.db import connect, initialize_database
from chat_chronicle.mcp_server import (
    _OMISSION_MARKER,
    create_server,
    open_read_only_database,
)


def _archive(tmp_path: Path) -> tuple[Path, int, int, int]:
    path = tmp_path / "archive # recall.db"
    initialize_database(path)
    now = datetime.now(UTC)
    active_created = (now - timedelta(days=2)).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )
    active_updated = (now - timedelta(days=1)).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )
    old_activity = (now - timedelta(days=400)).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )
    with connect(path) as conn:
        conn.execute(
            """
            INSERT INTO conversations (
                provider, provider_conv_id, title, url, origin_path, resume_hint,
                created_at, updated_at, message_count, content_hash
            ) VALUES
                ('chatgpt', 'one', 'Alpha topic', 'https://example.test/one', NULL, NULL,
                 ?, ?, 2, 'a'),
                ('claude', 'two', '', NULL, 'C:/archive/two.json', 'claude --resume two',
                 ?, ?, 1, 'b'),
                ('chatgpt', 'old', 'Old topic', NULL, NULL, NULL,
                 ?, ?, 1, 'c')
            """,
            (
                active_created,
                active_updated,
                active_created,
                active_updated,
                old_activity,
                old_activity,
            ),
        )
        ids = [
            int(row[0])
            for row in conn.execute("SELECT id FROM conversations ORDER BY id").fetchall()
        ]
        conn.executemany(
            "INSERT INTO messages (conversation_id, role, created_at, body, seq) "
            "VALUES (?, ?, ?, ?, ?)",
            [
                (ids[0], "user", "2026-07-25T10:00:00Z", "scan-local alpha/body", 1),
                (ids[0], "assistant", "2026-07-25T10:01:00Z", "Z" * 1200, 2),
                (ids[1], "user", None, "provider:openai_codex alpha", 1),
                (ids[2], "user", None, "alpha old", 1),
            ],
        )
        valid = {
            "summary": "Alpha work was completed. The archive remains useful.",
            "start_date": "2026-07-25",
            "last_active_date": "2026-07-26",
            "evidence_message_ids": [],
        }
        common = (
            "conversation-summary",
            "1",
            "input",
            "prompt",
            "task",
            "ConversationSummaryResult",
            "1",
            "default",
            "model",
            "success",
            "2026-07-26T11:00:00Z",
            "2026-07-26T11:01:00Z",
            1,
            "{}",
            "{}",
        )
        conn.execute(
            """
            INSERT INTO ai_task_results (
                conversation_id, task_name, task_version, conversation_input_hash,
                prompt_hash, task_config_hash, output_schema_name, output_schema_version,
                model_profile, model_config_hash, status, started_at, completed_at,
                latency_ms, usage_json, selection_json, result_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ids[0], *common, json.dumps(valid)),
        )
        conn.execute(
            """
            INSERT INTO ai_task_results (
                conversation_id, task_name, task_version, conversation_input_hash,
                prompt_hash, task_config_hash, output_schema_name, output_schema_version,
                model_profile, model_config_hash, status, started_at, completed_at,
                latency_ms, usage_json, selection_json, result_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ids[1], *common, "{bad"),
        )
        conn.commit()
        from chat_chronicle.db import rebuild_fts

        rebuild_fts(conn)
    return path, ids[0], ids[1], ids[2]


def _run(coro):
    return asyncio.run(coro)


async def _tools(server):
    async with Client(server) as client:
        return await client.list_tools()


async def _call(server, name: str, arguments: dict):
    async with Client(server) as client:
        result = await client.call_tool(name, arguments)
        return _plain(result.structured_content)


def _plain(value):
    if hasattr(value, "root"):
        return _plain(value.root)
    if hasattr(value, "model_dump"):
        return _plain(value.model_dump(mode="json"))
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        if set(value) == {"result"}:
            return _plain(value["result"])
        return {key: _plain(item) for key, item in value.items()}
    return value


def test_registration_and_discovery_schema(tmp_path: Path) -> None:
    path, *_ = _archive(tmp_path)
    tools = _run(_tools(create_server(path)))
    assert [tool.name for tool in tools] == [
        "search_chats",
        "get_conversation",
        "list_recent_topics",
    ]
    assert all(tool.description for tool in tools)
    schemas = {tool.name: tool.inputSchema for tool in tools}
    search_schema = schemas["search_chats"]
    assert set(search_schema["properties"]) == {
        "query",
        "provider",
        "after",
        "before",
        "limit",
    }
    assert search_schema["required"] == ["query"]
    assert search_schema["properties"]["limit"] == {
        "default": 10,
        "description": "Maximum ranked results.",
        "maximum": 100,
        "minimum": 1,
        "type": "integer",
    }
    detail_schema = schemas["get_conversation"]
    assert set(detail_schema["properties"]) == {"id", "max_chars"}
    assert detail_schema["required"] == ["id"]
    assert detail_schema["properties"]["id"]["exclusiveMinimum"] == 0
    assert detail_schema["properties"]["max_chars"]["default"] == 8000
    assert detail_schema["properties"]["max_chars"]["minimum"] == 500
    assert detail_schema["properties"]["max_chars"]["maximum"] == 50_000
    recent_schema = schemas["list_recent_topics"]
    assert set(recent_schema["properties"]) == {"days", "limit"}
    assert recent_schema.get("required", []) == []
    assert recent_schema["properties"]["days"]["default"] == 7
    assert recent_schema["properties"]["days"]["minimum"] == 1
    assert recent_schema["properties"]["days"]["maximum"] == 365
    assert recent_schema["properties"]["limit"]["default"] == 20
    assert recent_schema["properties"]["limit"]["minimum"] == 1
    assert recent_schema["properties"]["limit"]["maximum"] == 100


@pytest.mark.parametrize(
    "query", ["scan-local", "provider:openai_codex", "alpha/body", '"alpha"', "(alpha)"]
)
def test_search_is_ranked_safe_and_structured(tmp_path: Path, query: str) -> None:
    path, first, *_ = _archive(tmp_path)
    rows = _run(_call(create_server(path), "search_chats", {"query": query}))
    if query != "provider:openai_codex":
        assert rows
    if query == "scan-local":
        assert rows[0]["id"] == first
        assert rows[0]["summary"].startswith("Alpha work")
        assert set(rows[0]) == {
            "id",
            "provider",
            "title",
            "last_activity_at",
            "snippet",
            "score",
            "summary",
            "url",
        }


def test_search_filters_empty_and_validation(tmp_path: Path) -> None:
    path, first, *_ = _archive(tmp_path)
    server = create_server(path)
    now = datetime.now(UTC)
    after = (now - timedelta(days=30)).date().isoformat()
    before = (now + timedelta(days=1)).date().isoformat()
    rows = _run(
        _call(
            server,
            "search_chats",
            {
                "query": "alpha",
                "provider": "chatgpt",
                "after": after,
                "before": before,
                "limit": 1,
            },
        )
    )
    assert [row["id"] for row in rows] == [first]
    assert _run(_call(server, "search_chats", {"query": "no-such-token"})) == []
    with pytest.raises(ToolError, match="whitespace"):
        _run(_call(server, "search_chats", {"query": "   "}))
    with pytest.raises(ToolError):
        _run(_call(server, "search_chats", {"query": "alpha", "limit": 0}))
    for field in ("after", "before"):
        with pytest.raises(ToolError, match="Invalid date filter"):
            _run(_call(server, "search_chats", {"query": "alpha", field: "not-a-date"}))
    assert _run(_call(server, "search_chats", {"query": "alpha"}))


def test_search_uses_newest_valid_stored_summary(tmp_path: Path) -> None:
    path, first, second, *_ = _archive(tmp_path)
    newer_valid = {
        "summary": "The newest valid summary wins. It remains deterministic.",
        "start_date": "2026-07-25",
        "last_active_date": "2026-07-26",
        "evidence_message_ids": [],
    }
    with connect(path) as conn:
        for suffix, status, completed_at, result_json in (
            ("new-valid", "success", "2026-07-26T12:00:00Z", json.dumps(newer_valid)),
            ("malformed", "success", "2026-07-26T13:00:00Z", "{bad"),
            ("failed", "failed", "2026-07-26T14:00:00Z", json.dumps(newer_valid)),
        ):
            conn.execute(
                """
                INSERT INTO ai_task_results (
                    conversation_id, task_name, task_version, conversation_input_hash,
                    prompt_hash, task_config_hash, output_schema_name, output_schema_version,
                    model_profile, model_config_hash, status, started_at, completed_at,
                    latency_ms, usage_json, selection_json, result_json
                )
                SELECT conversation_id, task_name, task_version, ?,
                       prompt_hash, task_config_hash, output_schema_name, output_schema_version,
                       model_profile, model_config_hash, ?, started_at, ?,
                       latency_ms, usage_json, selection_json, ?
                FROM ai_task_results
                WHERE conversation_id = ?
                ORDER BY id
                LIMIT 1
                """,
                (suffix, status, completed_at, result_json, first),
            )
        conn.commit()

    rows = _run(_call(create_server(path), "search_chats", {"query": "alpha"}))
    by_id = {row["id"]: row for row in rows}
    assert by_id[first]["summary"] == newer_valid["summary"]
    assert by_id[second]["summary"] is None


def test_conversation_metadata_ordering_and_truncation(tmp_path: Path) -> None:
    path, first, second, *_ = _archive(tmp_path)
    server = create_server(path)
    full = _run(_call(server, "get_conversation", {"id": second, "max_chars": 8000}))
    assert full["origin_path"] == "C:/archive/two.json"
    assert full["resume_hint"] == "claude --resume two"
    assert full["truncated"] is False
    unbounded = _run(_call(server, "get_conversation", {"id": first, "max_chars": 8000}))
    exact = _run(
        _call(
            server,
            "get_conversation",
            {"id": first, "max_chars": unbounded["total_chars"]},
        )
    )
    assert exact["transcript"] == unbounded["transcript"]
    assert exact["truncated"] is False
    assert exact["total_chars"] == exact["returned_chars"] == unbounded["total_chars"]
    assert _OMISSION_MARKER.strip() not in exact["transcript"]
    short = _run(_call(server, "get_conversation", {"id": first, "max_chars": 500}))
    assert short["truncated"] is True
    assert _OMISSION_MARKER.strip() in short["transcript"]
    assert short["returned_chars"] == len(short["transcript"]) == 500
    assert short["transcript"].startswith("[message 1")
    assert short["transcript"].endswith("Z" * 20)
    with pytest.raises(ToolError, match="not found"):
        _run(_call(server, "get_conversation", {"id": 999}))
    with pytest.raises(ToolError):
        _run(_call(server, "get_conversation", {"id": first, "max_chars": 499}))


def test_recent_topics_summary_and_fallbacks(tmp_path: Path) -> None:
    path, first, second, *_ = _archive(tmp_path)
    rows = _run(_call(create_server(path), "list_recent_topics", {"days": 365, "limit": 20}))
    assert [row["id"] for row in rows[:2]] == [second, first]
    assert all(row["title"] != "Old topic" for row in rows)
    assert rows[0]["topic"] == "(untitled)"
    assert rows[0]["topic_source"] == "title"
    assert rows[1]["topic_source"] == "conversation-summary"
    with pytest.raises(ToolError):
        _run(_call(create_server(path), "list_recent_topics", {"days": 0}))
    with pytest.raises(ToolError):
        _run(_call(create_server(path), "list_recent_topics", {"limit": 101}))


def test_read_only_open_and_calls_do_not_mutate(tmp_path: Path) -> None:
    path, first, *_ = _archive(tmp_path)
    before = (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
    with open_read_only_database(path) as conn:
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("DELETE FROM conversations")
        version_before = conn.execute("PRAGMA user_version").fetchone()[0]
        counts_before = {
            table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            for table in ("conversations", "messages", "ai_task_results")
        }
    server = create_server(path)
    _run(_call(server, "search_chats", {"query": "alpha"}))
    _run(_call(server, "get_conversation", {"id": first}))
    _run(_call(server, "list_recent_topics", {"days": 365}))
    after = (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
    with open_read_only_database(path) as conn:
        version_after = conn.execute("PRAGMA user_version").fetchone()[0]
        counts_after = {
            table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            for table in ("conversations", "messages", "ai_task_results")
        }
    assert before == after
    assert version_before == version_after == 3
    assert counts_before == counts_after == {
        "conversations": 3,
        "messages": 4,
        "ai_task_results": 2,
    }
    assert not Path(f"{path}-wal").exists()
    assert not Path(f"{path}-shm").exists()


def test_database_failures_are_actionable_and_non_mutating(tmp_path: Path) -> None:
    missing = tmp_path / "missing.db"
    with pytest.raises(RuntimeError, match="chronicle init"):
        open_read_only_database(missing)
    assert not missing.exists()
    with pytest.raises(RuntimeError, match="not a file"):
        open_read_only_database(tmp_path)
    corrupt = tmp_path / "corrupt.db"
    corrupt.write_text("not sqlite", encoding="utf-8")
    with pytest.raises(RuntimeError, match="valid, readable"):
        open_read_only_database(corrupt)
    newer = tmp_path / "newer.db"
    conn = sqlite3.connect(newer)
    conn.execute("PRAGMA user_version = 99")
    conn.close()
    with pytest.raises(RuntimeError, match="newer"):
        open_read_only_database(newer)
    older = tmp_path / "older.db"
    initialize_database(older)
    conn = sqlite3.connect(older)
    conn.execute("PRAGMA user_version = 2")
    conn.close()
    with pytest.raises(RuntimeError, match="older"):
        open_read_only_database(older)
    incomplete = tmp_path / "incomplete.db"
    conn = sqlite3.connect(incomplete)
    conn.execute("PRAGMA user_version = 3")
    conn.close()
    with pytest.raises(RuntimeError, match="incomplete"):
        open_read_only_database(incomplete)


def test_cli_help_and_lazy_import(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    help_result = runner.invoke(app, ["serve", "--help"])
    assert help_result.exit_code == 0
    assert "stdio" in help_result.stdout
    assert "read-only" in help_result.stdout
    assert "CHAT_CHRONICLE_DB" in help_result.stdout

    import builtins

    real_import = builtins.__import__

    def missing(name, *args, **kwargs):
        if name == "chat_chronicle.mcp_server":
            exc = ModuleNotFoundError("No module named 'fastmcp'")
            exc.name = "fastmcp"
            raise exc
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing)
    result = runner.invoke(app, ["serve", "--db-path", str(tmp_path / "none.db")])
    assert result.exit_code == 1
    assert "poetry install -E mcp" in result.stderr
    assert "Traceback" not in result.stderr


def test_real_stdio_subprocess_protocol(tmp_path: Path) -> None:
    path, first, *_ = _archive(tmp_path)
    config = {
        "mcpServers": {
            "chronicle": {
                "command": sys.executable,
                "args": [
                    "-c",
                    "from chat_chronicle.cli import app; app()",
                    "serve",
                    "--db-path",
                    str(path),
                ],
            }
        }
    }

    async def smoke() -> None:
        async with Client(config, timeout=20) as client:
            tools = await client.list_tools()
            assert [tool.name for tool in tools] == [
                "search_chats",
                "get_conversation",
                "list_recent_topics",
            ]
            assert not (
                await client.call_tool("search_chats", {"query": "no-such-token"})
            ).is_error
            assert not (
                await client.call_tool("search_chats", {"query": "alpha"})
            ).is_error
            assert not (
                await client.call_tool("get_conversation", {"id": first})
            ).is_error
            assert not (
                await client.call_tool("list_recent_topics", {"days": 365})
            ).is_error
            invalid = await client.call_tool(
                "search_chats", {"query": "   "}, raise_on_error=False
            )
            assert invalid.is_error

    _run(smoke())
