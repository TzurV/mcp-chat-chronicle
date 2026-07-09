from typer.testing import CliRunner

from chat_chronicle import __version__
from chat_chronicle.cli import app

runner = CliRunner()

REQUIRED_COMMANDS = [
    "ingest",
    "ingest-folder",
    "collect",
    "scan-local",
    "stats",
    "search",
    "open",
]


def test_help_lists_every_required_command() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in REQUIRED_COMMANDS:
        assert command in result.stdout


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_stub_commands_exit_successfully() -> None:
    invocations = [
        ["ingest", "export.zip"],
        ["ingest-folder", "exports"],
        ["collect"],
        ["scan-local"],
        ["stats"],
        ["search", "docker network"],
        ["open", "1"],
    ]
    for args in invocations:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, f"{args} exited {result.exit_code}"
        assert "not implemented yet" in result.stdout


def test_malformed_argument_fails() -> None:
    result = runner.invoke(app, ["open", "not-an-id"])
    assert result.exit_code != 0
