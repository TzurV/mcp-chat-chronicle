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
    "hosted candidate generation requires --allow-remote --confirm-private-eval",
    "measured application commit does not match pinned identity",
    "tracked implementation is dirty or has an unapproved diff",
    "candidate response provider/model identity mismatch",
    "package checksum validation failed",
    "candidate cases do not match local authority",
    "candidate package contains",
    "accepted input",
    "accepted selector",
    "reference ",
    "selection manifest",
    "selection manifest and conversation limit are mutually exclusive",
    "ordered bundle scope requires selection manifest configuration",
    "bundle selection manifest identity differs from configuration",
    "evaluation path",
    "evaluation input/output paths overlap",
    "judge cache miss in cache-only mode",
    "--judge-cache-only requires --with-judge",
    "deterministic artifact mismatch:",
    "judged scoring manifest is inconsistent",
    "optimizer execution requires all remote disclosure and budget flags",
    "optimizer recovery requires the pinned clean application commit",
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
    allow_remote: bool = typer.Option(False),
    confirm_private_eval: bool = typer.Option(False),
) -> None:
    """Generate candidates; hosted APIs require explicit private-data authorization."""
    try:
        loaded = load_config(config)
        emit(
            asyncio.run(
                generate_cases(
                    bundle.resolve(),
                    loaded,
                    config.resolve(),
                    retry_failures=retry_failures,
                    allow_remote=allow_remote,
                    confirm_private_eval=confirm_private_eval,
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
    """Verify a returned benchmark or optimizer package without model calls."""
    try:
        if package.suffix.casefold() == ".json":
            from .optimization.operations import verify_candidate

            emit(verify_candidate(config.resolve(), package.resolve()))
            return
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
    judge_cache_only: bool = typer.Option(False, "--judge-cache-only"),
) -> None:
    """Score locally; remote judging requires all explicit authorization flags."""
    try:
        loaded = load_config(config)
        if with_judge and not loaded.judge.enabled:
            raise ValueError("judge is disabled in evaluation configuration")
        if with_judge and not (allow_remote and confirm_private_eval):
            raise ValueError("judge requires --with-judge --allow-remote --confirm-private-eval")
        if judge_cache_only and not with_judge:
            raise ValueError("--judge-cache-only requires --with-judge")
        if with_judge:
            score_package(package.resolve(), loaded, config.resolve())
            emit(
                asyncio.run(
                    score_with_judge(
                        package.resolve(),
                        loaded,
                        config.resolve(),
                        retry_failures=retry_judge_failures,
                        cache_only=judge_cache_only,
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


@app.command("preflight")
def optimization_preflight(config: Path = typer.Option(...)) -> None:
    """Validate frozen optimizer inputs, identities, budgets, and framework APIs."""
    try:
        from .optimization.operations import preflight

        emit(preflight(config.resolve()))
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        fail(exc)


@app.command("dry-run")
def optimization_dry_run(config: Path = typer.Option(...)) -> None:
    """Exercise the optimizer bridge and safe package model without provider calls."""
    try:
        from .optimization.operations import dry_run

        emit(dry_run(config.resolve()))
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        fail(exc)


def _execute_optimizer(config: Path, resume: bool) -> None:
    from .optimization.execution import run_optimization

    emit(run_optimization(config.resolve(), resume=resume))


@app.command("optimize")
def optimization_run(
    config: Path = typer.Option(...),
    allow_remote: bool = typer.Option(False),
    confirm_private_eval: bool = typer.Option(False),
    confirm_proposer_disclosure: bool = typer.Option(False),
    confirm_paid_budget: bool = typer.Option(False),
) -> None:
    """Authorize a new provider-facing optimizer run after explicit disclosure gates."""
    try:
        if not all(
            (allow_remote, confirm_private_eval, confirm_proposer_disclosure, confirm_paid_budget)
        ):
            raise ValueError("optimizer execution requires all remote disclosure and budget flags")
        _execute_optimizer(config, False)
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        fail(exc)


@app.command("resume")
def optimization_resume(
    config: Path = typer.Option(...),
    allow_remote: bool = typer.Option(False),
    confirm_private_eval: bool = typer.Option(False),
    confirm_proposer_disclosure: bool = typer.Option(False),
    confirm_paid_budget: bool = typer.Option(False),
) -> None:
    """Authorize resume from explicit current-attempt authority."""
    try:
        if not all(
            (allow_remote, confirm_private_eval, confirm_proposer_disclosure, confirm_paid_budget)
        ):
            raise ValueError("optimizer execution requires all remote disclosure and budget flags")
        _execute_optimizer(config, True)
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        fail(exc)


@app.command("inspect")
def optimization_inspect(config: Path = typer.Option(...)) -> None:
    """Inspect aggregate current-attempt state without provider calls."""
    try:
        from .optimization.operations import inspect_run

        emit(inspect_run(config.resolve()))
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        fail(exc)


@app.command("recover-gepa-readiness")
def optimization_recover_gepa_readiness(config: Path = typer.Option(...)) -> None:
    """Recover historical P0/Bootstrap authority without calls and stop before GEPA."""
    try:
        from .optimization.recovery import recover_gepa_readiness

        emit(recover_gepa_readiness(config.resolve()))
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        fail(exc)


@app.command("package")
def optimization_package(
    config: Path = typer.Option(...), output: Path = typer.Option(...)
) -> None:
    """Package accepted P0 as a verified four-component JSON candidate."""
    try:
        from .optimization.operations import package_baseline

        emit(package_baseline(config.resolve(), output.resolve()))
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        fail(exc)


@app.command("export-shortlist")
def optimization_export_shortlist(
    config: Path = typer.Option(...),
    output: Path = typer.Option(...),
    limit: int = typer.Option(5, min=3, max=5),
) -> None:
    """Export only privacy-eligible immutable candidates without provider calls."""
    try:
        from .optimization.operations import export_shortlist

        emit(export_shortlist(config.resolve(), output.resolve(), limit))
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        fail(exc)


if __name__ == "__main__":
    app()
