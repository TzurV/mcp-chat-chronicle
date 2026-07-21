"""Command line interface for the development-only benchmark harness."""
# ruff: noqa: B008 -- Typer declares options in function defaults by design.

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path

import typer

from chat_chronicle.ai_config import AIConfigError

from .config import load_config
from .core import generate as generate_cases
from .core import prepare as prepare_bundle
from .core import score as score_package
from .core import verify as verify_package
from .judge import score_with_judge

app = typer.Typer(no_args_is_help=True, help="Split candidate generation and local scoring.")


def emit(value: object, *, artifact_label: str | None = None) -> None:
    if artifact_label and isinstance(value, dict) and "archive" in value:
        value = {**value, "archive": artifact_label}
    typer.echo(json.dumps(value, sort_keys=True))


def fail(exc: Exception) -> None:
    detail = _safe_error(exc)
    typer.echo(f"Error: {detail}", err=True)
    raise typer.Exit(2)


_SAFE_ERRORS = (
    "judge requires --with-judge --allow-remote --confirm-private-eval",
    "judge is disabled in evaluation configuration",
    "select --deterministic-only or explicitly authorize judge scoring",
    "bundle destination already exists",
    "candidate package destination already exists",
    "candidate artifact_path is required",
    "candidate artifact file identity mismatch",
    "candidate artifact size/hash mismatch",
    "measured application commit does not match pinned identity",
    "tracked implementation is dirty or has an unapproved diff",
    "candidate response provider/model identity mismatch",
    "package checksum validation failed",
    "candidate cases do not match local authority",
    "candidate package contains",
    "accepted input",
    "accepted selector",
    "reference ",
    "evaluation path",
    "evaluation input/output paths overlap",
)


def _safe_error(exc: Exception) -> str:
    message = str(exc)
    missing = re.fullmatch(r"Missing required environment variable ([A-Z][A-Z0-9_]*)", message)
    if missing:
        return f"missing required environment variable {missing.group(1)}"
    if isinstance(exc, AIConfigError):
        return "invalid evaluation or model configuration"
    if any(message.startswith(prefix) for prefix in _SAFE_ERRORS):
        return message[:240]
    if isinstance(exc, OSError):
        return "private evaluation filesystem operation failed"
    return "private evaluation validation failed"


@app.command()
def prepare(
    config: Path = typer.Option(...),
    conversation_limit: int | None = typer.Option(None, min=1),
) -> None:
    """Prepare a private candidate-input bundle locally."""
    try:
        loaded = load_config(config)
        result = prepare_bundle(loaded, config.resolve(), conversation_limit=conversation_limit)
        emit(result, artifact_label="candidate-input-archive")
        typer.echo("This bundle contains private selected conversation content.")
        typer.echo(
            "Transfer it only to an owner-approved machine using an owner-approved secure method."
        )
    except (AIConfigError, OSError, ValueError, KeyError) as exc:
        fail(exc)
    except RuntimeError:
        fail(RuntimeError("unexpected internal evaluation failure"))


@app.command()
def generate(
    bundle: Path = typer.Option(...),
    config: Path = typer.Option(...),
    retry_failures: bool = typer.Option(False),
) -> None:
    """Generate candidates from a self-contained private bundle."""
    try:
        loaded = load_config(config)
        emit(
            asyncio.run(
                generate_cases(
                    bundle.resolve(),
                    loaded,
                    config.resolve(),
                    retry_failures=retry_failures,
                )
            ),
            artifact_label="candidate-package-archive",
        )
    except (AIConfigError, OSError, ValueError, KeyError) as exc:
        fail(exc)
    except RuntimeError:
        fail(RuntimeError("unexpected internal evaluation failure"))


@app.command()
def verify(
    package: Path = typer.Option(..., "--package"),
    config: Path = typer.Option(...),
) -> None:
    """Verify a returned package without model calls."""
    try:
        emit(verify_package(package.resolve(), load_config(config), config.resolve()))
    except (AIConfigError, OSError, ValueError, KeyError) as exc:
        fail(exc)
    except RuntimeError:
        fail(RuntimeError("unexpected internal evaluation failure"))


@app.command()
def score(
    package: Path = typer.Option(..., "--package"),
    config: Path = typer.Option(...),
    deterministic_only: bool = typer.Option(False),
    with_judge: bool = typer.Option(False),
    allow_remote: bool = typer.Option(False),
    confirm_private_eval: bool = typer.Option(False),
    retry_judge_failures: bool = typer.Option(False),
) -> None:
    """Score locally; remote judging requires all explicit authorization flags."""
    try:
        loaded = load_config(config)
        if with_judge and not loaded.judge.enabled:
            raise ValueError("judge is disabled in evaluation configuration")
        if with_judge and not (allow_remote and confirm_private_eval):
            raise ValueError("judge requires --with-judge --allow-remote --confirm-private-eval")
        if with_judge:
            score_package(package.resolve(), loaded, config.resolve())
            emit(
                asyncio.run(
                    score_with_judge(
                        package.resolve(),
                        loaded,
                        config.resolve(),
                        retry_failures=retry_judge_failures,
                    )
                )
            )
            return
        if not deterministic_only:
            raise ValueError("select --deterministic-only or explicitly authorize judge scoring")
        emit(score_package(package.resolve(), loaded, config.resolve()))
    except (AIConfigError, OSError, ValueError, KeyError) as exc:
        fail(exc)
    except RuntimeError:
        fail(RuntimeError("unexpected internal evaluation failure"))


if __name__ == "__main__":
    app()
