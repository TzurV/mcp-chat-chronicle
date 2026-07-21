"""Evaluation configuration loading."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from chat_chronicle.ai_config import (
    AIConfigError,
    is_remote_profile,
    load_model_catalog,
    load_task_catalog,
)

from .models import EvaluationConfig


def load_config(path: Path) -> EvaluationConfig:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        config = EvaluationConfig.model_validate(raw)
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        raise AIConfigError(f"Invalid evaluation config {path}: {exc}") from exc
    task_path = _relative(path, config.task_catalog)
    model_path = _relative(path, config.model_catalog)
    tasks = load_task_catalog(task_path)
    models = load_model_catalog(model_path)
    missing_tasks = [name for name in config.tasks if name not in tasks.tasks]
    missing_profiles = [
        name
        for name in (config.candidate.profile, config.judge.profile)
        if name not in models.profiles
    ]
    if missing_tasks:
        raise AIConfigError(f"Missing task definitions: {', '.join(missing_tasks)}")
    if missing_profiles:
        raise AIConfigError(f"Missing model profiles: {', '.join(missing_profiles)}")
    if is_remote_profile(models.profiles[config.candidate.profile]):
        raise AIConfigError("candidate profile must be local")
    if not is_remote_profile(models.profiles[config.judge.profile]):
        raise AIConfigError("judge profile must be remote")
    return config


def _relative(config_path: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (config_path.parent / path).resolve()
