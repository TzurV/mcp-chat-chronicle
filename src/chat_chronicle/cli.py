"""Typer CLI entrypoint.

Every command is a stub in WP-0.1: the surface is fixed here so later work
packages fill in behaviour without reshaping the CLI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from chat_chronicle import __version__

app = typer.Typer(
    name="chronicle",
    help="A local-first, searchable archive of your AI conversations.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


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
) -> None:
    """Ingest a single official export file."""
    _not_implemented("ingest", "WP-1.4")


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
def stats() -> None:
    """Show per-source counts and the most recent ingest runs."""
    _not_implemented("stats", "WP-1.4")


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


if __name__ == "__main__":  # pragma: no cover
    app()
