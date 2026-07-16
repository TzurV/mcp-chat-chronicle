"""YAML config defaults for the init/collect workflow (WP-1.6).

This module owns the small, validated config schema that drives
``chronicle init`` and ``chronicle collect``. It is an orchestration layer
over accepted adapters: it decides which sources to look at and where, but it
never parses transcripts itself.

Path handling rules:

- ``${VAR}`` / ``$VAR`` environment variables are expanded (``${USERPROFILE}``
  on Windows, ``$HOME`` elsewhere).
- ``~`` is expanded to the user's home directory.
- Relative paths resolve from a base directory (the project root / current
  working directory), not from wherever the config file happens to live.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

CONFIG_VERSION = 1

# Where an initialized project keeps its generated, git-ignored config.
DEFAULT_CONFIG_DIRNAME = ".chronicle"
DEFAULT_CONFIG_FILENAME = "config.yaml"
DEFAULT_DB_RELATIVE = ".chronicle/chronicle.db"
DEFAULT_EXPORTS_ROOT = "exports"

# Tracked template shipped in the repository root (no private absolute paths).
DEFAULT_TEMPLATE_FILENAME = "chronicle.default.yaml"

# Provider identifiers understood by accepted adapters. Keep in sync with the
# CLI's ``_SUPPORTED_PROVIDERS`` (minus ``auto``).
SUPPORTED_PROVIDERS = frozenset({"chatgpt", "claude", "claude_code", "openai_codex"})

_KIND_OFFICIAL_EXPORT = "official_export"
_KIND_LOCAL_STORE = "local_store"
SUPPORTED_KINDS = frozenset({_KIND_OFFICIAL_EXPORT, _KIND_LOCAL_STORE})


class ConfigError(ValueError):
    """Raised when a config file is malformed or fails validation."""


class _ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PathsConfig(_ConfigModel):
    db: str = DEFAULT_DB_RELATIVE
    exports_root: str = DEFAULT_EXPORTS_ROOT


class EngineConfig(_ConfigModel):
    enabled: bool = True
    interested: bool = True


class SourceConfig(_ConfigModel):
    provider: str
    kind: str
    path: str


class ChronicleConfig(_ConfigModel):
    version: int = CONFIG_VERSION
    paths: PathsConfig = Field(default_factory=PathsConfig)
    engines: dict[str, EngineConfig] = Field(default_factory=dict)
    sources: dict[str, SourceConfig] = Field(default_factory=dict)


def default_config() -> ChronicleConfig:
    """Return the built-in default config used to seed ``config.yaml``."""
    return ChronicleConfig(
        version=CONFIG_VERSION,
        paths=PathsConfig(),
        engines={
            "chatgpt": EngineConfig(enabled=True, interested=True),
            "claude": EngineConfig(enabled=True, interested=True),
            "openai_codex": EngineConfig(enabled=True, interested=True),
            "claude_code": EngineConfig(enabled=True, interested=True),
            "cursor": EngineConfig(enabled=False, interested=True),
            "copilot_vscode": EngineConfig(enabled=False, interested=False),
        },
        sources={
            "chatgpt": SourceConfig(
                provider="chatgpt", kind=_KIND_OFFICIAL_EXPORT, path="exports/openai"
            ),
            "claude": SourceConfig(
                provider="claude", kind=_KIND_OFFICIAL_EXPORT, path="exports/claude"
            ),
            "openai_codex": SourceConfig(
                provider="openai_codex", kind=_KIND_LOCAL_STORE, path="${USERPROFILE}/.codex"
            ),
            "claude_code": SourceConfig(
                provider="claude_code",
                kind=_KIND_LOCAL_STORE,
                path="${USERPROFILE}/.claude/projects",
            ),
        },
    )


def default_config_path(base_dir: Path | None = None) -> Path:
    """Return the generated local config path under the project's ``.chronicle/``."""
    base = _base_dir(base_dir)
    return base / DEFAULT_CONFIG_DIRNAME / DEFAULT_CONFIG_FILENAME


def dump_config_yaml(config: ChronicleConfig) -> str:
    """Serialize a config to a stable, human-friendly YAML document."""
    payload = config.model_dump(mode="python")
    return yaml.safe_dump(payload, sort_keys=False, default_flow_style=False)


def load_config(config_path: Path) -> ChronicleConfig:
    """Load and validate a YAML config file.

    Raises ``ConfigError`` with an actionable message if the file is missing,
    is not valid YAML, is not a mapping, or fails schema validation.
    """
    try:
        raw_text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Could not read config file {config_path}: {exc}") from exc

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {config_path}: {exc}") from exc

    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(f"Invalid config in {config_path}: expected a mapping at the top level.")

    try:
        return ChronicleConfig.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"Invalid config in {config_path}:\n{exc}") from exc


def resolve_path(raw: str, base_dir: Path | None = None) -> Path:
    """Expand env vars and ``~`` then resolve relative paths from ``base_dir``."""
    expanded = os.path.expandvars(raw)
    expanded = os.path.expanduser(expanded)
    candidate = Path(expanded)
    if not candidate.is_absolute():
        candidate = _base_dir(base_dir) / candidate
    return candidate


def resolve_db_path(
    config: ChronicleConfig | None,
    *,
    cli_db_path: Path | None = None,
    base_dir: Path | None = None,
    env: dict[str, str] | None = None,
) -> Path | None:
    """Resolve the effective DB path using WP-1.6 precedence.

    Precedence:

    1. CLI ``--db-path``
    2. ``CHAT_CHRONICLE_DB`` environment variable
    3. config YAML ``paths.db``
    4. built-in default (``None`` -> caller falls back to ``default_db_path``)

    Returns ``None`` only when nothing is configured, letting the DB layer's
    own built-in default apply.
    """
    environ = os.environ if env is None else env

    if cli_db_path is not None:
        return cli_db_path.expanduser()

    env_db = environ.get("CHAT_CHRONICLE_DB")
    if env_db:
        return Path(env_db).expanduser()

    if config is not None:
        return resolve_path(config.paths.db, base_dir)

    return None


def _base_dir(base_dir: Path | None) -> Path:
    return (base_dir or Path.cwd()).resolve()
