"""Typer CLI entrypoint."""

from __future__ import annotations

import json
import sqlite3
import zipfile
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

from chat_chronicle import __version__
from chat_chronicle.adapters import chatgpt_export, claude_export, openai_codex
from chat_chronicle.db import (
    begin_ingest_run,
    connect,
    default_db_path,
    finish_ingest_run,
    get_or_create_source,
    mark_source_ingested,
    rebuild_fts,
    upsert_conversation,
)
from chat_chronicle.models import IngestRunSummary

app = typer.Typer(
    name="chronicle",
    help="A local-first, searchable archive of your AI conversations.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
error_console = Console(stderr=True)

_PROVIDER_CHATGPT = "chatgpt"
_PROVIDER_CLAUDE = "claude"
_PROVIDER_OPENAI_CODEX = "openai_codex"
_PROVIDER_AUTO = "auto"
_SUPPORTED_PROVIDERS = {
    _PROVIDER_AUTO,
    _PROVIDER_CHATGPT,
    _PROVIDER_CLAUDE,
    _PROVIDER_OPENAI_CODEX,
}
_CONVERSATIONS_FILENAME = "conversations.json"


def _not_implemented(command: str, work_package: str) -> None:
    console.print(
        f"[yellow]`chronicle {command}` is not implemented yet[/] (lands in {work_package})."
    )


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"chat-chronicle {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """A local-first, searchable archive of your AI conversations."""


@app.command()
def ingest(
    path: Annotated[Path, typer.Argument(help="Export archive or file to ingest.")],
    provider: Annotated[
        str, typer.Option(help="Source provider, or 'auto' to detect by signature.")
    ] = "auto",
    db_path: Annotated[
        Path | None,
        typer.Option(help="SQLite database path. Defaults to CHAT_CHRONICLE_DB or .chronicle."),
    ] = None,
) -> None:
    """Ingest a single official export or supported local session source."""
    requested_provider = provider.lower()
    if requested_provider not in _SUPPORTED_PROVIDERS:
        _fail(
            f"Unsupported provider '{provider}'. "
            "Use auto, chatgpt, claude, or openai_codex."
        )

    source_path = path.expanduser()
    if not source_path.exists():
        _fail(f"Source path does not exist: {source_path}")
    resolved_source = source_path.resolve()

    effective_provider = (
        _detect_provider(resolved_source)
        if requested_provider == _PROVIDER_AUTO
        else requested_provider
    )
    source_type = (
        "local_store"
        if effective_provider == _PROVIDER_OPENAI_CODEX
        else "official_export"
    )

    with connect(db_path) as conn:
        source_id = get_or_create_source(
            conn,
            source_type=source_type,
            provider=effective_provider,
            path_or_config=str(resolved_source),
        )
        run_id = begin_ingest_run(conn, source_id)

        result = _load_conversations(effective_provider, resolved_source)
        errors = _serializable_errors(result.errors)
        summary = IngestRunSummary(
            conversations_seen=len(result.conversations),
            errors=errors,
        )

        for conversation in result.conversations:
            upsert_result = upsert_conversation(conn, source_id, conversation)
            if upsert_result.status == "added":
                summary.added += 1
            elif upsert_result.status == "updated":
                summary.updated += 1
            else:
                summary.skipped += 1

        finish_ingest_run(conn, run_id, summary)
        mark_source_ingested(conn, source_id)
        rebuild_fts(conn)

    console.print(f"provider: {effective_provider}")
    console.print(f"db path: {_connect_db_display_path(db_path)}")
    console.print(f"source path: {resolved_source}")
    console.print(f"conversations seen: {summary.conversations_seen}")
    console.print(
        f"added: {summary.added}  updated: {summary.updated}  skipped: {summary.skipped}"
    )
    console.print(f"parse errors: {len(summary.errors)}")
    console.print(f"ingest run id: {run_id}")


@app.command("ingest-folder")
def ingest_folder(
    path: Annotated[Path, typer.Argument(help="Drop folder to sweep for exports.")],
) -> None:
    """Sweep a drop folder for export archives and ingest each one."""
    _not_implemented("ingest-folder", "WP-1.6")


@app.command()
def collect() -> None:
    """Run every enabled source through its adapter."""
    _not_implemented("collect", "WP-1.6")


@app.command("scan-local")
def scan_local() -> None:
    """Report, read-only, which AI-tool data stores exist on this machine."""
    _not_implemented("scan-local", "WP-1.5")


@app.command()
def stats(
    db_path: Annotated[
        Path | None,
        typer.Option(help="SQLite database path. Defaults to CHAT_CHRONICLE_DB or .chronicle."),
    ] = None,
) -> None:
    """Show per-source counts and the most recent ingest runs."""
    display_path = _connect_db_display_path(db_path)
    with connect(db_path) as conn:
        totals = _fetch_totals(conn)
        provider_counts = _fetch_provider_counts(conn)
        source_rows = _fetch_source_summaries(conn)
        run_rows = _fetch_recent_runs(conn)

    console.print(f"db path: {display_path}")
    console.print(f"total conversations: {totals['conversations']}")
    console.print(f"total messages: {totals['messages']}")

    provider_table = Table(title="Counts by provider")
    provider_table.add_column("Provider")
    provider_table.add_column("Conversations", justify="right")
    if provider_counts:
        for row in provider_counts:
            provider_table.add_row(row["provider"], str(row["conversation_count"]))
    else:
        provider_table.add_row("(none)", "0")
    console.print(provider_table)

    source_table = Table(title="Sources")
    source_table.add_column("ID", justify="right")
    source_table.add_column("Provider")
    source_table.add_column("Path", overflow="fold")
    source_table.add_column("Enabled")
    source_table.add_column("Last ingested")
    if source_rows:
        for row in source_rows:
            source_table.add_row(
                str(row["id"]),
                row["provider"],
                row["path_or_config"] or "",
                str(row["enabled"]),
                row["last_ingested_at"] or "",
            )
    else:
        source_table.add_row("-", "(none)", "", "", "")
    console.print(source_table)

    runs_table = Table(title="Recent ingest runs")
    runs_table.add_column("Run ID", justify="right")
    runs_table.add_column("Provider", overflow="fold")
    runs_table.add_column("Source ID", justify="right")
    runs_table.add_column("Status")
    runs_table.add_column("Seen", justify="right")
    runs_table.add_column("Added", justify="right")
    runs_table.add_column("Updated", justify="right")
    runs_table.add_column("Skipped", justify="right")
    runs_table.add_column("Errors", justify="right")
    if run_rows:
        for row in run_rows:
            runs_table.add_row(
                str(row["id"]),
                row["provider"] or "",
                str(row["source_id"] or ""),
                row["status"] or "",
                str(row["conversations_seen"] or 0),
                str(row["added"] or 0),
                str(row["updated"] or 0),
                str(row["skipped"] or 0),
                str(row["error_count"]),
            )
    else:
        runs_table.add_row("-", "", "", "(none)", "0", "0", "0", "0", "0")
    console.print(runs_table)


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Full-text search query.")],
    provider: Annotated[str | None, typer.Option(help="Filter by provider.")] = None,
    since: Annotated[
        str | None, typer.Option(help="Only results on or after this ISO date.")
    ] = None,
    until: Annotated[
        str | None, typer.Option(help="Only results on or before this ISO date.")
    ] = None,
    tag: Annotated[str | None, typer.Option(help="Filter by enrichment tag.")] = None,
    limit: Annotated[int, typer.Option(help="Maximum number of results.")] = 10,
) -> None:
    """Search the archive with FTS5 ranking and snippets."""
    _not_implemented("search", "WP-2.1")


@app.command("open")
def open_result(
    result_id: Annotated[int, typer.Argument(help="Conversation id from a search result.")],
) -> None:
    """Open a result: deep link for web chats, transcript view otherwise."""
    _not_implemented("open", "WP-2.1")


def _connect_db_display_path(db_path: Path | None) -> Path:
    if db_path is None:
        return default_db_path()
    return db_path.expanduser().resolve()


def _fail(message: str) -> None:
    error_console.print(f"[red]{message}[/]")
    raise typer.Exit(code=1)


def _detect_provider(path: Path) -> str:
    detected: list[str] = []
    if _looks_like_codex_source(path):
        detected.append(_PROVIDER_OPENAI_CODEX)

    conversations_json = _load_conversations_json_for_detection(path)
    if conversations_json is not None:
        if _looks_like_chatgpt_export(conversations_json):
            detected.append(_PROVIDER_CHATGPT)
        if _looks_like_claude_export(conversations_json):
            detected.append(_PROVIDER_CLAUDE)

    unique = sorted(set(detected))
    if len(unique) == 1:
        return unique[0]
    if len(unique) > 1:
        _fail(f"Ambiguous provider detection for {path}: {', '.join(unique)}")
    _fail(
        f"Unsupported source format for {path}. "
        "Expected ChatGPT/Claude conversations.json or OpenAI Codex JSONL sessions."
    )
    raise AssertionError("unreachable")


def _load_conversations_json_for_detection(path: Path) -> object | None:
    candidate: Path | None = None
    if path.is_dir():
        candidate = path / _CONVERSATIONS_FILENAME
        if not candidate.is_file():
            return None
        try:
            return json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return None

    if path.is_file() and zipfile.is_zipfile(path):
        try:
            with zipfile.ZipFile(path) as archive:
                members = [
                    name
                    for name in archive.namelist()
                    if not name.endswith("/") and Path(name).name == _CONVERSATIONS_FILENAME
                ]
                if not members:
                    return None
                member = min(members, key=lambda name: (name.count("/"), name))
                return json.loads(archive.read(member).decode("utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError, zipfile.BadZipFile):
            return None

    if path.is_file() and path.name == _CONVERSATIONS_FILENAME:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return None

    return None


def _looks_like_chatgpt_export(data: object) -> bool:
    if not isinstance(data, list):
        return False
    return any(
        isinstance(record, dict)
        and (
            isinstance(record.get("mapping"), dict)
            or isinstance(record.get("current_node"), str)
        )
        for record in data
    )


def _looks_like_claude_export(data: object) -> bool:
    if not isinstance(data, list):
        return False
    return any(
        isinstance(record, dict)
        and isinstance(record.get("uuid"), str)
        and isinstance(record.get("chat_messages"), list)
        for record in data
    )


def _looks_like_codex_source(path: Path) -> bool:
    if path.is_file():
        return path.suffix.lower() == ".jsonl" and _jsonl_has_codex_signature(path)

    sessions_dir = path / "sessions"
    if (path / openai_codex.SESSION_INDEX_FILENAME).is_file() and sessions_dir.is_dir():
        return True
    if sessions_dir.is_dir() and any(sessions_dir.rglob("rollout-*.jsonl")):
        return True
    if path.name == "sessions" and any(path.rglob("rollout-*.jsonl")):
        return True
    return False


def _jsonl_has_codex_signature(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as handle:
            inspected = 0
            for line in handle:
                if not line.strip():
                    continue
                inspected += 1
                if inspected > 100:
                    return False
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(record, dict):
                    continue
                if not isinstance(record.get("payload"), dict):
                    continue
                if record.get("type") in {"session_meta", "response_item"}:
                    return True
    except OSError:
        return False
    return False


def _load_conversations(provider: str, path: Path) -> Any:
    if provider == _PROVIDER_CHATGPT:
        return chatgpt_export.load_conversations(path)
    if provider == _PROVIDER_CLAUDE:
        return claude_export.load_conversations(path)
    if provider == _PROVIDER_OPENAI_CODEX:
        return openai_codex.load_conversations(path)
    raise ValueError(f"unsupported provider: {provider}")


def _serializable_errors(errors: list[Any]) -> list[dict[str, Any]]:
    serialized: list[dict[str, Any]] = []
    for error in errors:
        if hasattr(error, "model_dump"):
            serialized.append(error.model_dump())
        elif isinstance(error, dict):
            serialized.append(error)
        else:
            serialized.append({"error": type(error).__name__, "detail": str(error)})
    return serialized


def _fetch_totals(conn: sqlite3.Connection) -> dict[str, int]:
    conversations = conn.execute("SELECT count(*) FROM conversations").fetchone()[0]
    messages = conn.execute("SELECT count(*) FROM messages").fetchone()[0]
    return {"conversations": int(conversations), "messages": int(messages)}


def _fetch_provider_counts(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT provider, count(*) AS conversation_count
        FROM conversations
        GROUP BY provider
        ORDER BY provider
        """
    ).fetchall()


def _fetch_source_summaries(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT id, provider, path_or_config, enabled, last_ingested_at
        FROM sources
        ORDER BY id
        """
    ).fetchall()


def _fetch_recent_runs(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            r.id,
            r.source_id,
            s.provider,
            r.status,
            r.conversations_seen,
            r.added,
            r.updated,
            r.skipped,
            CASE
                WHEN r.errors_json IS NULL OR r.errors_json = '' THEN 0
                ELSE json_array_length(r.errors_json)
            END AS error_count
        FROM ingest_runs AS r
        LEFT JOIN sources AS s ON s.id = r.source_id
        ORDER BY r.id DESC
        LIMIT 10
        """
    ).fetchall()


if __name__ == "__main__":  # pragma: no cover
    app()
