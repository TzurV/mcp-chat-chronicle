"""Validated external configuration for optional AI tasks."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

AI_TASKS_FILENAME = "ai-tasks.yaml"
AI_MODELS_FILENAME = "ai-models.yaml"
AI_TASKS_TEMPLATE = "ai-tasks.default.yaml"
AI_MODELS_TEMPLATE = "ai-models.default.yaml"
AI_CONFIG_DIR_ENV = "CHAT_CHRONICLE_AI_CONFIG_DIR"
ALLOWED_SELECTORS = {
    "full-conversation",
    "recent-messages",
    "metadata-recent",
    "conversation-overview-v1",
    "recent-meaningful-v1",
}
ALLOWED_SCHEMAS = {
    "example-result-v1",
    "conversation-summary-v1",
    "work-mode-classification-v1",
    "last-activity-v1",
    "title-assessment-v1",
}
ALLOWED_PLACEHOLDERS = {
    "conversation_id",
    "provider",
    "title",
    "start_date",
    "last_active_date",
    "transcript",
}
_PLACEHOLDER = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


class AIConfigError(ValueError):
    pass


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GenerationConfig(_StrictModel):
    temperature: float = Field(default=0, ge=0, le=2)
    max_tokens: int = Field(default=500, gt=0, le=100_000)


class TaskGenerationConfig(_StrictModel):
    """Optional per-task overrides of model-profile generation defaults."""

    temperature: float | None = Field(default=None, ge=0, le=2)
    max_tokens: int | None = Field(default=None, gt=0, le=100_000)


class TaskDefinition(_StrictModel):
    enabled: bool = True
    version: str
    description: str = ""
    model_profile: str
    input_selector: str
    output_schema: str
    system_prompt: str
    user_prompt: str
    generation: TaskGenerationConfig = Field(default_factory=TaskGenerationConfig)
    depends_on: list[str] = Field(default_factory=list)
    max_input_chars: int = Field(default=50_000, gt=0, le=2_000_000)
    recent_message_count: int = Field(default=20, gt=0, le=10_000)

    @field_validator("input_selector")
    @classmethod
    def known_selector(cls, value: str) -> str:
        if value not in ALLOWED_SELECTORS:
            raise ValueError(f"unknown input selector '{value}'")
        return value

    @field_validator("output_schema")
    @classmethod
    def known_schema(cls, value: str) -> str:
        if value not in ALLOWED_SCHEMAS:
            raise ValueError(f"unknown output schema '{value}'")
        return value

    @field_validator("system_prompt", "user_prompt")
    @classmethod
    def known_placeholders(cls, value: str) -> str:
        unknown = sorted(set(_PLACEHOLDER.findall(value)) - ALLOWED_PLACEHOLDERS)
        if unknown:
            raise ValueError(f"unknown prompt placeholder(s): {', '.join(unknown)}")
        return value


class TaskCatalog(_StrictModel):
    version: Literal[1] = 1
    tasks: dict[str, TaskDefinition] = Field(default_factory=dict)


class ModelProfile(_StrictModel):
    model: str
    api_base: str | None = None
    api_key_env: str | None = None
    remote: bool = False
    timeout: float = Field(default=60, gt=0, le=3600)
    retries: int = Field(default=1, ge=0, le=10)
    concurrency: int = Field(default=1, gt=0, le=16)
    structured_output: bool = True
    context_window: int | None = Field(default=None, gt=0, le=10_000_000)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)


class ModelCatalog(_StrictModel):
    version: Literal[1] = 1
    profiles: dict[str, ModelProfile] = Field(default_factory=dict)


def ai_config_paths(base_dir: Path | None = None) -> tuple[Path, Path]:
    configured = os.environ.get(AI_CONFIG_DIR_ENV)
    root = (
        Path(configured).expanduser().resolve()
        if configured
        else (base_dir or Path.cwd()).resolve() / ".chronicle"
    )
    return root / AI_TASKS_FILENAME, root / AI_MODELS_FILENAME


def load_task_catalog(path: Path) -> TaskCatalog:
    catalog = _load_yaml(path, TaskCatalog)
    assert isinstance(catalog, TaskCatalog)
    _validate_dependencies(catalog, path)
    return catalog


def load_model_catalog(path: Path) -> ModelCatalog:
    catalog = _load_yaml(path, ModelCatalog)
    assert isinstance(catalog, ModelCatalog)
    return catalog


def validate_catalog_references(tasks: TaskCatalog, models: ModelCatalog, tasks_path: Path) -> None:
    for task_name, task in tasks.tasks.items():
        if task.model_profile not in models.profiles:
            raise AIConfigError(
                f"Task '{task_name}' in {tasks_path} references unknown model profile "
                f"'{task.model_profile}'"
            )


def _load_yaml(path: Path, model: type[_StrictModel]) -> _StrictModel:
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except OSError as exc:
        raise AIConfigError(f"Could not read AI config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise AIConfigError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AIConfigError(f"Invalid AI config in {path}: expected a mapping")
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise AIConfigError(f"Invalid AI config in {path}:\n{exc}") from exc


def _validate_dependencies(catalog: TaskCatalog, path: Path) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visiting:
            raise AIConfigError(f"Dependency cycle in {path} involving task '{name}'")
        if name in visited:
            return
        task = catalog.tasks[name]
        visiting.add(name)
        for dependency in task.depends_on:
            if dependency not in catalog.tasks:
                raise AIConfigError(
                    f"Task '{name}' in {path} has unknown dependency '{dependency}'"
                )
            visit(dependency)
        visiting.remove(name)
        visited.add(name)

    for task_name in catalog.tasks:
        visit(task_name)


def resolve_model(profile: ModelProfile) -> dict[str, Any]:
    model = os.path.expandvars(profile.model)
    if "$" in model:
        raise AIConfigError(
            f"Model profile requires an unset environment variable: {profile.model}"
        )
    if (
        "CHRONICLE_LOCAL_MODEL" in profile.model
        and profile.api_base
        and not is_remote_profile(profile)
        and "/" not in model
    ):
        raise AIConfigError(
            "Local OpenAI-compatible model profiles require a LiteLLM provider prefix; "
            "for LM Studio use 'lm_studio/<model-id>'."
        )
    result = profile.model_dump(mode="json")
    result["model"] = model
    if profile.api_key_env:
        key = os.environ.get(profile.api_key_env)
        if not key:
            raise AIConfigError(f"Missing required environment variable {profile.api_key_env}")
        result["api_key"] = key
    return result


def resolve_generation(task: TaskDefinition, profile: ModelProfile) -> GenerationConfig:
    """Apply task fields as optional overrides of concrete profile defaults."""
    return GenerationConfig(
        temperature=(
            task.generation.temperature
            if task.generation.temperature is not None
            else profile.generation.temperature
        ),
        max_tokens=(
            task.generation.max_tokens
            if task.generation.max_tokens is not None
            else profile.generation.max_tokens
        ),
    )


def is_remote_profile(profile: ModelProfile) -> bool:
    if profile.remote:
        return True
    if profile.api_base:
        host = (urlparse(profile.api_base).hostname or "").lower()
        return host not in {"localhost", "127.0.0.1", "::1"}
    # Without an explicitly loopback endpoint, provider routing is conservatively remote.
    return True


def interpolate_prompt(template: str, values: dict[str, str]) -> str:
    return _PLACEHOLDER.sub(lambda match: values[match.group(1)], template)


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader which rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)
