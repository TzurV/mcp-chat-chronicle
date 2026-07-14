"""Typer CLI entrypoint."""

from __future__ import annotations

import json
import os
import sqlite3
import webbrowser
import zipfile
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from chat_chronicle import __version__
from chat_chronicle.adapters import chatgpt_export, claude_code, claude_export, openai_codex
from chat_chronicle.db import (
    begin_ingest_run,
    connect,
    default_db_path,
    finish_ingest_run,
    get_or_create_project,
    get_or_create_source,
    mark_source_ingested,
    rebuild_fts,
    upsert_conversation,
)
from chat_chronicle.models import IngestRunSummary
from chat_chronicle.search import (
    ConversationDetail,
    RecentConversation,
    SearchResult,
    get_conversation_detail,
    list_recent_conversations,
    search_conversations,
    should_show_broad_search_hint,
)

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
_PROVIDER_CLAUDE_CODE = "claude_code"
_PROVIDER_OPENAI_CODEX = "openai_codex"
_PROVIDER_AUTO = "auto"
_SUPPORTED_PROVIDERS = {
    _PROVIDER_AUTO,
    _PROVIDER_CHATGPT,
    _PROVIDER_CLAUDE,
    _PROVIDER_CLAUDE_CODE,
    _PROVIDER_OPENAI_CODEX,
}
_CONVERSATIONS_FILENAME = "conversations.json"
_SPLIT_CONVERSATIONS_GLOB = "conversations-*.json"


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
            "Use auto, chatgpt, claude, claude_code, or openai_codex."
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
        if effective_provider in {_PROVIDER_OPENAI_CODEX, _PROVIDER_CLAUDE_CODE}
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

        _assign_project_ids(conn, result)
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
def recent(
    limit: Annotated[
        int | None,
        typer.Option(
            "-n",
            "--limit",
            help="Maximum number of conversations to show.",
        ),
    ] = None,
    provider: Annotated[str | None, typer.Option(help="Filter by provider.")] = None,
    since: Annotated[
        str | None,
        typer.Option(help="Only conversations active on or after this ISO date."),
    ] = None,
    until: Annotated[
        str | None,
        typer.Option(help="Only conversations active on or before this ISO date."),
    ] = None,
    db_path: Annotated[
        Path | None,
        typer.Option(help="SQLite database path. Defaults to CHAT_CHRONICLE_DB or .chronicle."),
    ] = None,
) -> None:
    """List the most recently active conversations."""
    effective_limit = limit if limit is not None else 10
    try:
        with connect(db_path) as conn:
            rows = list_recent_conversations(
                conn,
                provider=provider,
                since=since,
                until=until,
                limit=effective_limit,
            )
    except ValueError as exc:
        _fail(str(exc))

    console.print(f"db path: {_connect_db_display_path(db_path)}")
    if not rows:
        console.print("No conversations")
        return

    table = Table(title="Recent conversations")
    table.add_column("ID", justify="right")
    table.add_column("Date")
    table.add_column("Provider")
    table.add_column("Title", overflow="fold")
    table.add_column("URL", overflow="fold")
    for row in rows:
        table.add_row(
            Text(str(row.conversation_id)),
            Text(row.last_activity_at or ""),
            Text(row.provider),
            Text(row.title or "(untitled)"),
            Text(_recent_link_hint(row)),
        )
    console.print(table)
    if limit is None:
        console.print(
            f"Showing {len(rows)} conversation(s); default maximum is 10. "
            "Use -n/--limit to increase the number shown, up to 100."
        )


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Full-text search query.")],
    phrase: Annotated[
        bool,
        typer.Option(
            "--phrase",
            help="Treat QUERY as an exact phrase instead of broad FTS terms.",
        ),
    ] = False,
    provider: Annotated[str | None, typer.Option(help="Filter by provider.")] = None,
    since: Annotated[
        str | None, typer.Option(help="Only results on or after this ISO date.")
    ] = None,
    until: Annotated[
        str | None, typer.Option(help="Only results on or before this ISO date.")
    ] = None,
    tag: Annotated[str | None, typer.Option(help="Filter by enrichment tag.")] = None,
    limit: Annotated[int, typer.Option(help="Maximum number of results.")] = 10,
    db_path: Annotated[
        Path | None,
        typer.Option(help="SQLite database path. Defaults to CHAT_CHRONICLE_DB or .chronicle."),
    ] = None,
) -> None:
    """Search the archive with FTS5 ranking and snippets."""
    if not query.strip():
        _fail("Search query cannot be empty.")
    if limit < 1 or limit > 100:
        _fail("Limit must be between 1 and 100.")

    try:
        with connect(db_path) as conn:
            results = search_conversations(
                conn,
                query,
                provider=provider,
                since=since,
                until=until,
                tag=tag,
                limit=limit,
                phrase=phrase,
            )
    except ValueError as exc:
        _fail(str(exc))
    except sqlite3.OperationalError as exc:
        _fail(f"Invalid search query: {exc}")

    console.print(f"db path: {_connect_db_display_path(db_path)}")
    if not results:
        console.print("No results")
        _print_broad_search_hint(query, phrase=phrase)
        return

    table = Table(title="Search results")
    table.add_column("ID", justify="right")
    table.add_column("Date")
    table.add_column("Provider")
    table.add_column("Title", overflow="fold")
    table.add_column("Snippet", overflow="fold")
    table.add_column("Open hint", overflow="fold")
    for result in results:
        table.add_row(
            Text(str(result.conversation_id)),
            Text(_result_date(result)),
            Text(result.provider),
            Text(result.title or "(untitled)"),
            Text(result.snippet),
            Text(_open_hint(result)),
        )
    console.print(table)
    for result in results:
        console.print(
            Text(
                "result "
                f"{result.conversation_id} | {_result_date(result)} | "
                f"{result.provider} | {result.title or '(untitled)'} | "
                f"{result.snippet} | {_open_hint(result)}"
            )
        )
    _print_broad_search_hint(query, phrase=phrase)


@app.command("open")
def open_result(
    result_id: Annotated[int, typer.Argument(help="Conversation id from a search result.")],
    db_path: Annotated[
        Path | None,
        typer.Option(help="SQLite database path. Defaults to CHAT_CHRONICLE_DB or .chronicle."),
    ] = None,
) -> None:
    """Open a result: deep link for web chats, transcript view otherwise."""
    with connect(db_path) as conn:
        detail = get_conversation_detail(conn, result_id)
    if detail is None:
        _fail(f"Conversation not found: {result_id}")

    _print_conversation_header(detail)
    if detail.url:
        console.print(f"url: {detail.url}")
        opened = _open_url_in_browser(detail.url)
        if opened:
            console.print("browser launch: attempted")
        else:
            console.print("browser launch: unavailable; use the printed URL")
        return

    if detail.origin_path:
        console.print(f"origin_path: {detail.origin_path}")
        console.print(f"origin_file: {Path(detail.origin_path).name}")
    else:
        console.print("source link: no URL or origin_path available")
    if detail.resume_hint:
        console.print(f"resume_hint: {detail.resume_hint}")
    _render_transcript(detail)


def _connect_db_display_path(db_path: Path | None) -> Path:
    if db_path is None:
        return default_db_path()
    return db_path.expanduser().resolve()


def _fail(message: str) -> None:
    error_console.print(f"[red]{message}[/]")
    raise typer.Exit(code=1)


def _print_broad_search_hint(query: str, *, phrase: bool) -> None:
    if should_show_broad_search_hint(query, phrase=phrase):
        console.print(
            'Hint: this was a broad token search. For exact phrase matching, use --phrase "..."'
        )


def _result_date(result: SearchResult) -> str:
    return result.updated_at or ""


def _open_hint(result: SearchResult) -> str:
    if result.url:
        return f"chronicle open {result.conversation_id} (web URL)"
    if result.origin_path:
        return f"chronicle open {result.conversation_id} (local transcript)"
    return f"chronicle open {result.conversation_id} (stored transcript)"


def _recent_link_hint(result: RecentConversation) -> str:
    if result.url:
        return result.url
    if result.origin_path:
        return f"local: {Path(result.origin_path).name}"
    if result.resume_hint:
        return result.resume_hint
    return "-"


def _print_conversation_header(detail: ConversationDetail) -> None:
    console.print(f"id: {detail.conversation_id}")
    console.print(f"provider: {detail.provider}")
    console.print(f"title: {detail.title or '(untitled)'}")
    date_value = detail.updated_at or detail.created_at or ""
    if date_value:
        console.print(f"date: {date_value}")


def _render_transcript(detail: ConversationDetail) -> None:
    console.print("transcript:")
    if not detail.messages:
        console.print("(no messages)")
        return
    for message in detail.messages:
        role = message.role or "unknown"
        timestamp = f" [{message.created_at}]" if message.created_at else ""
        console.print(Text(f"{role}{timestamp}:"))
        console.print(Text(message.body))


def _open_url_in_browser(url: str) -> bool:
    if os.environ.get("CHAT_CHRONICLE_NO_BROWSER") in {"1", "true", "TRUE", "yes", "YES"}:
        return False
    try:
        return bool(webbrowser.open(url))
    except OSError:
        return False


def _detect_provider(path: Path) -> str:
    detected: list[str] = []
    if _looks_like_codex_source(path):
        detected.append(_PROVIDER_OPENAI_CODEX)
    if _looks_like_claude_code_source(path):
        detected.append(_PROVIDER_CLAUDE_CODE)

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
        "Expected ChatGPT/Claude conversations.json, OpenAI Codex JSONL sessions, "
        "or Claude Code JSONL sessions."
    )
    raise AssertionError("unreachable")


def _load_conversations_json_for_detection(path: Path) -> object | None:
    if path.is_dir():
        canonical = path / _CONVERSATIONS_FILENAME
        if canonical.is_file():
            return _read_json_for_detection(canonical)
        split_paths = sorted(
            candidate
            for candidate in path.rglob(_SPLIT_CONVERSATIONS_GLOB)
            if candidate.is_file() and _is_split_conversations_name(candidate.name)
        )
        return _load_split_json_for_detection(split_paths)

    if path.is_file() and zipfile.is_zipfile(path):
        try:
            with zipfile.ZipFile(path) as archive:
                members = [
                    name
                    for name in archive.namelist()
                    if not name.endswith("/") and Path(name).name == _CONVERSATIONS_FILENAME
                ]
                if members:
                    member = min(members, key=lambda name: (name.count("/"), name))
                    return json.loads(archive.read(member).decode("utf-8"))
                split_members = sorted(
                    name
                    for name in archive.namelist()
                    if not name.endswith("/")
                    and _is_split_conversations_name(Path(name).name)
                )
                records: list[object] = []
                for member in split_members:
                    try:
                        data = json.loads(archive.read(member).decode("utf-8"))
                    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                        continue
                    if isinstance(data, list):
                        records.extend(data)
                return records or None
        except (OSError, json.JSONDecodeError, UnicodeDecodeError, zipfile.BadZipFile):
            return None

    if path.is_file() and (
        path.name == _CONVERSATIONS_FILENAME or _is_split_conversations_name(path.name)
    ):
        return _read_json_for_detection(path)

    return None


def _read_json_for_detection(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _load_split_json_for_detection(paths: list[Path]) -> object | None:
    records: list[object] = []
    for path in paths:
        data = _read_json_for_detection(path)
        if isinstance(data, list):
            records.extend(data)
    return records or None


def _is_split_conversations_name(name: str) -> bool:
    return name.startswith("conversations-") and name.endswith(".json")


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


def _looks_like_claude_code_source(path: Path) -> bool:
    if path.is_file():
        return path.suffix.lower() == ".jsonl" and _jsonl_has_claude_code_signature(path)

    if path.name == "projects" and path.parent.name == ".claude" and any(path.rglob("*.jsonl")):
        return True
    if any(
        candidate.parent.parent.name == "projects" and candidate.suffix.lower() == ".jsonl"
        for candidate in path.glob("*.jsonl")
    ):
        return True
    sample_files = sorted(path.rglob("*.jsonl"))[:10]
    if any(_jsonl_has_claude_code_signature(candidate) for candidate in sample_files):
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


def _jsonl_has_claude_code_signature(path: Path) -> bool:
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
                if not isinstance(record.get("type"), str):
                    continue
                if record.get("type") in {"user", "assistant", "summary", "ai-title"}:
                    message = record.get("message")
                    if isinstance(message, dict) and isinstance(message.get("role"), str):
                        return True
                    if isinstance(record.get("sessionId"), str):
                        return True
    except OSError:
        return False
    return False


def _load_conversations(provider: str, path: Path) -> Any:
    if provider == _PROVIDER_CHATGPT:
        return chatgpt_export.load_conversations(path)
    if provider == _PROVIDER_CLAUDE:
        return claude_export.load_conversations(path)
    if provider == _PROVIDER_CLAUDE_CODE:
        return claude_code.load_conversations(path)
    if provider == _PROVIDER_OPENAI_CODEX:
        return openai_codex.load_conversations(path)
    raise ValueError(f"unsupported provider: {provider}")


def _assign_project_ids(conn: sqlite3.Connection, result: Any) -> None:
    project_hints = getattr(result, "project_hints", None)
    if not isinstance(project_hints, dict) or not project_hints:
        return

    for conversation in result.conversations:
        hint = project_hints.get(conversation.provider_conv_id)
        if hint is None:
            continue
        name = getattr(hint, "name", None)
        if not isinstance(name, str) or not name:
            continue
        root_path = getattr(hint, "root_path", None)
        if root_path is not None and not isinstance(root_path, str):
            root_path = None
        conversation.project_id = get_or_create_project(
            conn,
            name=name,
            root_path=root_path,
        )


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
