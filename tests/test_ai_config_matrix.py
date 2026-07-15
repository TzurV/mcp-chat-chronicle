from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import pytest
import yaml

from chat_chronicle.ai_config import (
    AIConfigError,
    ModelProfile,
    TaskDefinition,
    load_model_catalog,
    load_task_catalog,
    resolve_model,
    validate_catalog_references,
)


def _task() -> dict:
    return {
        "version": "1",
        "model_profile": "local",
        "input_selector": "full-conversation",
        "output_schema": "example-result-v1",
        "system_prompt": "Return JSON.",
        "user_prompt": "{transcript}",
    }


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ("version: 1\ntasks: [", "Invalid YAML"),
        ("version: 2\ntasks: {}\n", "version"),
        ("version: 1\nunknown: true\ntasks: {}\n", "unknown"),
        ("version: 1\ntasks: {}\ntasks: {}\n", "duplicate key"),
        ("version: 1\ntasks: !!python/object:builtins.object {}\n", "Invalid YAML"),
    ],
)
def test_task_catalog_rejects_malformed_version_unknown_and_duplicates(
    tmp_path: Path, payload: str, message: str
) -> None:
    path = tmp_path / "tasks.yaml"
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(AIConfigError, match=message):
        load_task_catalog(path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("input_selector", "not-code-owned", "unknown input selector"),
        ("output_schema", "not-code-owned", "unknown output schema"),
        ("user_prompt", "{not_allowed}", "unknown prompt placeholder"),
    ],
)
def test_task_catalog_rejects_unknown_registries(
    tmp_path: Path, field: str, value: str, message: str
) -> None:
    task = _task()
    task[field] = value
    path = tmp_path / "tasks.yaml"
    path.write_text(yaml.safe_dump({"version": 1, "tasks": {"demo": task}}), encoding="utf-8")
    with pytest.raises(AIConfigError, match=message):
        load_task_catalog(path)


def test_unknown_dependency_and_cycle_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "tasks.yaml"
    task = _task()
    task["depends_on"] = ["missing"]
    path.write_text(yaml.safe_dump({"version": 1, "tasks": {"demo": task}}), encoding="utf-8")
    with pytest.raises(AIConfigError, match="unknown dependency"):
        load_task_catalog(path)
    task["depends_on"] = ["demo"]
    path.write_text(yaml.safe_dump({"version": 1, "tasks": {"demo": task}}), encoding="utf-8")
    with pytest.raises(AIConfigError, match="cycle"):
        load_task_catalog(path)


def test_model_catalog_strict_version_and_missing_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "models.yaml"
    path.write_text("version: 2\nprofiles: {}\n", encoding="utf-8")
    with pytest.raises(AIConfigError, match="version"):
        load_model_catalog(path)
    monkeypatch.delenv("SYNTHETIC_MODEL_KEY", raising=False)
    with pytest.raises(AIConfigError, match="SYNTHETIC_MODEL_KEY"):
        resolve_model(ModelProfile(model="mock", api_key_env="SYNTHETIC_MODEL_KEY"))


def test_lm_studio_environment_model_requires_litellm_provider_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = ModelProfile(
        model="${CHRONICLE_LOCAL_MODEL}",
        api_base="http://127.0.0.1:1234/v1",
    )
    monkeypatch.setenv("CHRONICLE_LOCAL_MODEL", "qwen3.5-4b")
    with pytest.raises(AIConfigError, match="lm_studio/<model-id>"):
        resolve_model(profile)

    monkeypatch.setenv("CHRONICLE_LOCAL_MODEL", "lm_studio/qwen3.5-4b")
    resolved = resolve_model(profile)
    assert resolved["model"] == "lm_studio/qwen3.5-4b"
    assert "api_key" not in resolved

    template = load_model_catalog(Path(__file__).resolve().parents[1] / "ai-models.default.yaml")
    local = template.profiles["service-local"]
    assert local.timeout == 180
    assert local.retries == 0
    assert local.context_window == 8192


def test_packaged_templates_are_available_and_privacy_safe() -> None:
    repo = Path(__file__).resolve().parents[1]
    for name in ("ai-tasks.default.yaml", "ai-models.default.yaml"):
        text = files("chat_chronicle.resources").joinpath(name).read_text("utf-8")
        assert text == (repo / name).read_text("utf-8")
        assert "C:\\" not in text
        assert "api_key:" not in text
        assert "conversation_id:" not in text
        assert "BEGIN PRIVATE" not in text


def test_task_definition_unknown_field_is_rejected() -> None:
    with pytest.raises(ValueError, match="extra"):
        TaskDefinition.model_validate({**_task(), "python_callable": "unsafe"})


def test_task_to_model_alias_is_validated(tmp_path: Path) -> None:
    task_path = tmp_path / "tasks.yaml"
    model_path = tmp_path / "models.yaml"
    task_path.write_text(
        yaml.safe_dump({"version": 1, "tasks": {"demo": _task()}}), encoding="utf-8"
    )
    model_path.write_text("version: 1\nprofiles: {}\n", encoding="utf-8")
    with pytest.raises(AIConfigError, match="unknown model profile 'local'"):
        validate_catalog_references(
            load_task_catalog(task_path), load_model_catalog(model_path), task_path
        )
