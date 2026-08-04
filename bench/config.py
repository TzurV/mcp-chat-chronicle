"""Evaluation configuration loading."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from chat_chronicle.ai_config import (
    AIConfigError,
    TaskCatalog,
    is_remote_profile,
    load_model_catalog,
    load_task_catalog,
)

from .models import EvaluationConfig

TASK_CATALOG_POLICY_VERSION = "1"
_PROMPT_FIELDS = ("system_prompt", "user_prompt")


@dataclass(frozen=True)
class TaskCatalogResolution:
    active: TaskCatalog
    authority: TaskCatalog
    active_sha256: str
    authority_sha256: str
    portable_identity: dict[str, Any] | None


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _non_prompt_catalog(catalog: TaskCatalog) -> dict[str, Any]:
    tasks: dict[str, Any] = {}
    for name, task in catalog.tasks.items():
        value = task.model_dump(mode="json")
        for field in _PROMPT_FIELDS:
            value.pop(field)
        tasks[name] = value
    return {"version": catalog.version, "tasks": tasks}


def _prompt_identities(catalog: TaskCatalog) -> dict[str, dict[str, str]]:
    return {
        name: {
            "system_prompt_sha256": hashlib.sha256(
                task.system_prompt.encode("utf-8")
            ).hexdigest(),
            "user_prompt_sha256": hashlib.sha256(
                task.user_prompt.encode("utf-8")
            ).hexdigest(),
        }
        for name, task in catalog.tasks.items()
    }


def resolve_task_catalogs(
    config: EvaluationConfig, config_path: Path
) -> TaskCatalogResolution:
    active_path = _relative(config_path, config.task_catalog)
    active = load_task_catalog(active_path)
    active_sha256 = _file_sha256(active_path)
    declaration = config.task_catalog_authority
    if declaration is None:
        return TaskCatalogResolution(
            active=active,
            authority=active,
            active_sha256=active_sha256,
            authority_sha256=active_sha256,
            portable_identity=None,
        )

    authority_path = _relative(config_path, declaration.path)
    authority = load_task_catalog(authority_path)
    authority_sha256 = _file_sha256(authority_path)
    if authority_sha256 != declaration.sha256:
        raise AIConfigError("authority task catalog file hash mismatch")
    if active_sha256 != declaration.active_sha256:
        raise AIConfigError("active prompt catalog file hash mismatch")
    if list(authority.tasks) != list(active.tasks):
        raise AIConfigError("authority and active task names/order differ")

    authority_contract = _non_prompt_catalog(authority)
    active_contract = _non_prompt_catalog(active)
    if authority_contract != active_contract:
        for task_name in authority.tasks:
            authority_task = authority_contract["tasks"][task_name]
            active_task = active_contract["tasks"][task_name]
            for field in authority_task:
                if authority_task[field] != active_task[field]:
                    raise AIConfigError(
                        "active task catalog changes non-prompt field "
                        f"'{task_name}.{field}'"
                    )
        raise AIConfigError("authority and active non-prompt task contracts differ")

    portable_identity = {
        "policy": declaration.allowed_changes,
        "policy_version": TASK_CATALOG_POLICY_VERSION,
        "authority_catalog_sha256": authority_sha256,
        "active_catalog_sha256": active_sha256,
        "non_prompt_contract_sha256": _canonical_sha256(authority_contract),
        "active_prompt_identities": _prompt_identities(active),
    }
    return TaskCatalogResolution(
        active=active,
        authority=authority,
        active_sha256=active_sha256,
        authority_sha256=authority_sha256,
        portable_identity=portable_identity,
    )


def load_config(path: Path) -> EvaluationConfig:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        config = EvaluationConfig.model_validate(raw)
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        raise AIConfigError(f"Invalid evaluation config {path}: {exc}") from exc
    model_path = _relative(path, config.model_catalog)
    tasks = resolve_task_catalogs(config, path).active
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
    candidate_remote = is_remote_profile(models.profiles[config.candidate.profile])
    if candidate_remote != (config.candidate.execution == "hosted-api"):
        raise AIConfigError(
            "candidate execution must match model profile locality "
            "(local-artifact/local profile or hosted-api/remote profile)"
        )
    if not is_remote_profile(models.profiles[config.judge.profile]):
        raise AIConfigError("judge profile must be remote")
    return config


def _relative(config_path: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (config_path.parent / path).resolve()
