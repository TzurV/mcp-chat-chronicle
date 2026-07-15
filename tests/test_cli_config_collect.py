"""Tests for WP-1.6 config defaults, `chronicle init`, and `chronicle collect`.

Every test operates inside an isolated temporary directory with a config that
points only at controlled temp/fixture paths. No test reads the real user
profile (`%USERPROFILE%`, `$HOME`) or touches real local stores.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from chat_chronicle.cli import app
from chat_chronicle.config import (
    ChronicleConfig,
    ConfigError,
    load_config,
    resolve_db_path,
    resolve_path,
)
from chat_chronicle.db import connect

runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Chdir into a temp project dir with a clean env for each test.

    Clearing ``CHAT_CHRONICLE_DB`` keeps DB-path precedence tests deterministic
    regardless of the developer's shell environment.
    """
    monkeypatch.delenv("CHAT_CHRONICLE_DB", raising=False)
    monkeypatch.chdir(tmp_path)
    yield tmp_path


def _write_config(base_dir: Path, config: dict) -> Path:
    config_path = base_dir / ".chronicle" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return config_path


def _count_rows(db_path: Path, table: str) -> int:
    with connect(db_path) as conn:
        return int(conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0])


def _minimal_config(*, db: str = ".chronicle/chronicle.db") -> dict:
    """A config with only synthetic, path-controlled sources for tests."""
    return {
        "version": 1,
        "paths": {"db": db, "exports_root": "exports"},
        "engines": {
            "chatgpt": {"enabled": True, "interested": True},
            "codexstore": {"enabled": True, "interested": True},
        },
        "sources": {
            "chatgpt": {
                "provider": "chatgpt",
                "kind": "official_export",
                "path": "exports/openai",
            },
            "codexstore": {
                "provider": "openai_codex",
                "kind": "local_store",
                "path": "local/codex",
            },
        },
    }


# --------------------------------------------------------------------------- #
# init
# --------------------------------------------------------------------------- #


def test_init_creates_chronicle_config_db_and_export_folders(project_dir: Path) -> None:
    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0, result.stdout
    assert (project_dir / ".chronicle" / "config.yaml").is_file()
    assert (project_dir / ".chronicle" / "ai-tasks.yaml").is_file()
    assert (project_dir / ".chronicle" / "ai-models.yaml").is_file()
    assert (project_dir / ".chronicle" / "chronicle.db").is_file()
    assert (project_dir / "exports" / "openai").is_dir()
    assert (project_dir / "exports" / "claude").is_dir()
    config = load_config(project_dir / ".chronicle" / "config.yaml")
    assert config.version == 1
    assert "chatgpt" in config.sources


def test_init_initializes_db_schema(project_dir: Path) -> None:
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, result.stdout
    db_path = project_dir / ".chronicle" / "chronicle.db"
    with connect(db_path) as conn:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
    assert int(version) >= 1


def test_init_does_not_overwrite_existing_config_by_default(project_dir: Path) -> None:
    config_path = project_dir / ".chronicle" / "config.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text("version: 1\n# hand-edited marker\n", encoding="utf-8")

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0, result.stdout
    assert "hand-edited marker" in config_path.read_text(encoding="utf-8")
    assert "kept" in result.stdout


def test_init_force_overwrites_existing_config(project_dir: Path) -> None:
    config_path = project_dir / ".chronicle" / "config.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text("version: 1\n# hand-edited marker\n", encoding="utf-8")

    result = runner.invoke(app, ["init", "--force"])

    assert result.exit_code == 0, result.stdout
    assert "hand-edited marker" not in config_path.read_text(encoding="utf-8")


def test_init_preserves_and_force_overwrites_ai_catalogs(project_dir: Path) -> None:
    first = runner.invoke(app, ["init"])
    assert first.exit_code == 0, first.stdout
    tasks = project_dir / ".chronicle" / "ai-tasks.yaml"
    models = project_dir / ".chronicle" / "ai-models.yaml"
    tasks.write_text("# hand-edited task marker\n", encoding="utf-8")
    models.write_text("# hand-edited model marker\n", encoding="utf-8")

    kept = runner.invoke(app, ["init"])
    assert kept.exit_code == 0, kept.stdout
    assert "hand-edited task marker" in tasks.read_text("utf-8")
    assert "hand-edited model marker" in models.read_text("utf-8")

    overwritten = runner.invoke(app, ["init", "--force"])
    assert overwritten.exit_code == 0, overwritten.stdout
    assert "hand-edited task marker" not in tasks.read_text("utf-8")
    assert "hand-edited model marker" not in models.read_text("utf-8")


def test_init_preserves_existing_db_file(project_dir: Path) -> None:
    db_path = project_dir / ".chronicle" / "chronicle.db"
    db_path.parent.mkdir(parents=True)
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO sources (source_type, provider) VALUES " "('manual_entry', 'marker')"
        )
        conn.commit()

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0, result.stdout
    assert "database, kept" in result.stdout
    with connect(db_path) as conn:
        markers = conn.execute("SELECT count(*) FROM sources WHERE provider = 'marker'").fetchone()[
            0
        ]
    assert int(markers) == 1


def test_init_custom_config_path(project_dir: Path) -> None:
    custom = project_dir / "custom" / "myconfig.yaml"
    result = runner.invoke(app, ["init", "--config", str(custom)])

    assert result.exit_code == 0, result.stdout
    assert custom.is_file()


# --------------------------------------------------------------------------- #
# config loading / resolution
# --------------------------------------------------------------------------- #


def test_config_resolves_relative_paths_from_base_dir() -> None:
    resolved = resolve_path("exports/openai", base_dir=Path("/base/project"))
    assert resolved == Path("/base/project/exports/openai").resolve()


def test_config_resolves_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_FAKE_PROFILE", "/fake/home")
    resolved = resolve_path("${MY_FAKE_PROFILE}/.codex")
    assert resolved == Path("/fake/home/.codex").resolve()


def test_invalid_config_yaml_raises_config_error(tmp_path: Path) -> None:
    bad = tmp_path / "config.yaml"
    bad.write_text("version: 1\n  bad: : indentation:\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(bad)


def test_invalid_config_schema_raises_config_error(tmp_path: Path) -> None:
    bad = tmp_path / "config.yaml"
    bad.write_text(
        yaml.safe_dump({"version": 1, "unknown_top_level_key": True}),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_config(bad)


def test_collect_invalid_config_exits_nonzero(project_dir: Path) -> None:
    config_path = project_dir / ".chronicle" / "config.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text("version: 1\n  broken: : :\n", encoding="utf-8")

    result = runner.invoke(app, ["collect"])

    assert result.exit_code != 0
    assert "Invalid" in result.stderr


# --------------------------------------------------------------------------- #
# DB path precedence
# --------------------------------------------------------------------------- #


def test_db_path_precedence_cli_beats_env_and_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = ChronicleConfig.model_validate(_minimal_config(db="config-db.db"))
    monkeypatch.setenv("CHAT_CHRONICLE_DB", "/env/env-db.db")
    resolved = resolve_db_path(
        config,
        cli_db_path=Path("/cli/cli-db.db"),
        base_dir=Path("/base"),
    )
    assert resolved == Path("/cli/cli-db.db")


def test_db_path_precedence_env_beats_config(monkeypatch: pytest.MonkeyPatch) -> None:
    config = ChronicleConfig.model_validate(_minimal_config(db="config-db.db"))
    monkeypatch.setenv("CHAT_CHRONICLE_DB", "/env/env-db.db")
    resolved = resolve_db_path(config, cli_db_path=None, base_dir=Path("/base"))
    assert resolved == Path("/env/env-db.db")


def test_db_path_precedence_config_used_when_no_cli_or_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CHAT_CHRONICLE_DB", raising=False)
    config = ChronicleConfig.model_validate(_minimal_config(db="config-db.db"))
    resolved = resolve_db_path(config, cli_db_path=None, base_dir=Path("/base"))
    assert resolved == Path("/base/config-db.db").resolve()


def test_collect_db_path_option_overrides_config(project_dir: Path) -> None:
    _write_config(project_dir, _minimal_config())
    override_db = project_dir / "override.db"

    result = runner.invoke(app, ["collect", "--db-path", str(override_db)])

    assert result.exit_code == 0, result.stdout
    assert override_db.exists()
    assert not (project_dir / ".chronicle" / "chronicle.db").exists()


# --------------------------------------------------------------------------- #
# collect
# --------------------------------------------------------------------------- #


def _seed_chatgpt_export(base: Path) -> None:
    shutil.copytree(
        FIXTURES / "chatgpt" / "minimal",
        base / "exports" / "openai" / "my-chatgpt-export",
    )


def _seed_codex_store(base: Path) -> None:
    (base / "local" / "codex").mkdir(parents=True)
    shutil.copyfile(
        FIXTURES / "openai_codex" / "minimal" / "rollout-minimal.jsonl",
        base / "local" / "codex" / "rollout-minimal.jsonl",
    )


def test_collect_ingests_export_folder_and_local_store(project_dir: Path) -> None:
    _write_config(project_dir, _minimal_config())
    _seed_chatgpt_export(project_dir)
    _seed_codex_store(project_dir)

    result = runner.invoke(app, ["collect"])

    assert result.exit_code == 0, result.stdout
    assert "sources collected: 2" in result.stdout
    assert "total added: 2  updated: 0  skipped: 0" in result.stdout
    db_path = project_dir / ".chronicle" / "chronicle.db"
    assert _count_rows(db_path, "conversations") == 2


def test_collect_skips_missing_paths_with_notes_and_exits_zero(
    project_dir: Path,
) -> None:
    _write_config(project_dir, _minimal_config())
    _seed_chatgpt_export(project_dir)  # local store deliberately absent

    result = runner.invoke(app, ["collect"])

    assert result.exit_code == 0, result.stdout
    assert "sources collected: 1" in result.stdout
    assert "missing" in result.stdout


def test_collect_all_missing_optional_sources_exits_zero(project_dir: Path) -> None:
    _write_config(project_dir, _minimal_config())

    result = runner.invoke(app, ["collect"])

    assert result.exit_code == 0, result.stdout
    assert "sources collected: 0" in result.stdout
    assert "no sources collected" in result.stdout


def test_collect_rerun_is_idempotent(project_dir: Path) -> None:
    _write_config(project_dir, _minimal_config())
    _seed_chatgpt_export(project_dir)

    first = runner.invoke(app, ["collect"])
    second = runner.invoke(app, ["collect"])

    assert first.exit_code == 0, first.stdout
    assert second.exit_code == 0, second.stdout
    assert "total added: 1  updated: 0  skipped: 0" in first.stdout
    assert "total added: 0  updated: 0  skipped: 1" in second.stdout
    db_path = project_dir / ".chronicle" / "chronicle.db"
    assert _count_rows(db_path, "conversations") == 1


def test_collect_disabled_engine_is_not_collected(project_dir: Path) -> None:
    config = _minimal_config()
    config["engines"]["chatgpt"]["enabled"] = False
    _write_config(project_dir, config)
    _seed_chatgpt_export(project_dir)

    result = runner.invoke(app, ["collect"])

    assert result.exit_code == 0, result.stdout
    assert "chatgpt" not in result.stdout


def test_collect_unsupported_provider_is_reported_not_fatal(project_dir: Path) -> None:
    config = _minimal_config()
    config["engines"]["cursor"] = {"enabled": True, "interested": True}
    config["sources"]["cursor"] = {
        "provider": "cursor",
        "kind": "local_store",
        "path": "local/cursor",
    }
    (project_dir / "local" / "cursor").mkdir(parents=True)
    _write_config(project_dir, config)

    result = runner.invoke(app, ["collect"])

    assert result.exit_code == 0, result.stdout
    assert "unsupported" in result.stdout


def test_collect_output_includes_per_source_and_aggregate_counts(
    project_dir: Path,
) -> None:
    _write_config(project_dir, _minimal_config())
    _seed_chatgpt_export(project_dir)

    result = runner.invoke(app, ["collect"])

    assert result.exit_code == 0, result.stdout
    assert "total conversations seen:" in result.stdout
    assert "total parse errors:" in result.stdout
    assert "Collect sources" in result.stdout


def test_collect_without_config_exits_nonzero(project_dir: Path) -> None:
    result = runner.invoke(app, ["collect"])
    assert result.exit_code != 0
    assert "No config found" in result.stderr


# --------------------------------------------------------------------------- #
# read commands honor config paths.db (WP-1.6 precedence, all commands)
# --------------------------------------------------------------------------- #


def _collect_into_config_db(project_dir: Path) -> Path:
    """Init a project, collect one synthetic export, return the config DB path."""
    _write_config(project_dir, _minimal_config())
    _seed_chatgpt_export(project_dir)
    result = runner.invoke(app, ["collect"])
    assert result.exit_code == 0, result.stdout
    db_path = project_dir / ".chronicle" / "chronicle.db"
    assert _count_rows(db_path, "conversations") == 1
    return db_path


def test_stats_uses_config_db_when_no_cli_or_env(project_dir: Path) -> None:
    _collect_into_config_db(project_dir)

    # No --db-path, no CHAT_CHRONICLE_DB: stats must read config paths.db.
    result = runner.invoke(app, ["stats"])

    assert result.exit_code == 0, result.stdout
    assert "total conversations: 1" in result.stdout


def test_search_uses_config_db_when_no_cli_or_env(project_dir: Path) -> None:
    _collect_into_config_db(project_dir)

    result = runner.invoke(app, ["search", "docker"])

    assert result.exit_code == 0, result.stdout
    # The synthetic chatgpt fixture contains "docker"; it is found via config DB.
    assert "No results" not in result.stdout


def test_recent_uses_config_db_when_no_cli_or_env(project_dir: Path) -> None:
    _collect_into_config_db(project_dir)

    result = runner.invoke(app, ["recent"])

    assert result.exit_code == 0, result.stdout
    assert "No conversations" not in result.stdout


def test_read_command_db_path_option_overrides_config(project_dir: Path) -> None:
    _collect_into_config_db(project_dir)
    empty_db = project_dir / "empty.db"

    # --db-path points at a fresh, empty DB: config paths.db must be ignored.
    result = runner.invoke(app, ["stats", "--db-path", str(empty_db)])

    assert result.exit_code == 0, result.stdout
    assert "total conversations: 0" in result.stdout


def test_read_command_env_overrides_config(
    project_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _collect_into_config_db(project_dir)
    empty_db = project_dir / "env.db"
    monkeypatch.setenv("CHAT_CHRONICLE_DB", str(empty_db))

    result = runner.invoke(app, ["stats"])

    assert result.exit_code == 0, result.stdout
    assert "total conversations: 0" in result.stdout


def test_read_command_invalid_config_surfaces_error(project_dir: Path) -> None:
    # A malformed config present in CWD must fail read commands clearly,
    # rather than silently falling back to the built-in default DB.
    config_path = project_dir / ".chronicle" / "config.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text("version: 1\n  broken: : :\n", encoding="utf-8")

    result = runner.invoke(app, ["stats"])

    assert result.exit_code != 0
    assert "Invalid" in result.stderr


def test_resolve_effective_db_path_falls_back_to_default_without_config(
    project_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # No config file and no CLI/env: the helper returns None so the DB layer's
    # built-in default applies. Asserted at the helper level to avoid touching
    # the real repository database.
    from chat_chronicle.cli import _resolve_effective_db_path

    monkeypatch.delenv("CHAT_CHRONICLE_DB", raising=False)
    assert _resolve_effective_db_path(None) is None


def test_resolve_effective_db_path_uses_config_paths_db(
    project_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from chat_chronicle.cli import _resolve_effective_db_path

    monkeypatch.delenv("CHAT_CHRONICLE_DB", raising=False)
    _write_config(project_dir, _minimal_config(db=".chronicle/chronicle.db"))
    resolved = _resolve_effective_db_path(None)
    assert resolved == (project_dir / ".chronicle" / "chronicle.db").resolve()
