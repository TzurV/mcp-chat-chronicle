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


def test_scan_local_exits_successfully() -> None:
    result = runner.invoke(app, ["scan-local"])
    assert result.exit_code == 0
    assert "Local source inventory" in result.stdout


def test_ingest_folder_points_at_supported_commands() -> None:
    result = runner.invoke(app, ["ingest-folder", "exports"])
    assert result.exit_code == 0
    assert "superseded" in result.stdout
    assert "chronicle collect" in result.stdout


def test_malformed_argument_fails() -> None:
    result = runner.invoke(app, ["open", "not-an-id"])
    assert result.exit_code != 0
