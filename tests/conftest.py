from __future__ import annotations

import pytest

import chat_chronicle.cli as cli_module


@pytest.fixture(autouse=True)
def _wide_console() -> None:
    """Force a deterministic, wide console width during tests.

    Under pytest/CliRunner there is no TTY, so Rich falls back to an 80-column
    width and soft-wraps output. That reflows single logical lines (e.g. search
    result rows) and can split phrases across lines, breaking substring
    assertions. Pin a wide width so output is stable regardless of the
    environment's terminal size.
    """
    original = cli_module.console.width
    cli_module.console.width = 10_000
    try:
        yield
    finally:
        cli_module.console.width = original
