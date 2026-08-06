"""Lazy DSPy adapters for one four-component Chronicle program."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from bench.models import TASK_ORDER

from .compat import verify_compatibility
from .package import (
    CandidateDemonstration,
    CandidatePackage,
    demonstration_value,
    mutate_package,
)


def build_program(package: CandidatePackage, lms: dict[str, Any] | None = None) -> Any:
    verify_compatibility()
    import dspy

    class ChronicleProgram(dspy.Module):
        def __init__(self) -> None:
            super().__init__()
            self._chronicle_prompt_texts = {task: package.prompts[task].text for task in TASK_ORDER}
            self._chronicle_lms = lms or {}
            for ordinal, task in enumerate(TASK_ORDER):
                signature = dspy.Signature(
                    {
                        "selected_input": (str, dspy.InputField()),
                        "response_json": (str, dspy.OutputField()),
                    },
                    instructions=package.prompts[task].text,
                )
                setattr(self, f"task_{ordinal}", dspy.Predict(signature))

        def forward(self, task: str, selected_input: str, model_id: str | None = None) -> Any:
            if task not in TASK_ORDER:
                raise ValueError("unknown Chronicle optimization task")
            predictor = getattr(self, f"task_{TASK_ORDER.index(task)}")
            if self._chronicle_lms:
                if model_id not in self._chronicle_lms:
                    raise ValueError("unknown Chronicle candidate model")
                with dspy.context(lm=self._chronicle_lms[model_id]):
                    return predictor(selected_input=selected_input)
            return predictor(selected_input=selected_input)

    return ChronicleProgram()


def prompts_from_program(program: Any) -> dict[str, str]:
    prompts = {}
    originals = getattr(program, "_chronicle_prompt_texts", {})
    for ordinal, task in enumerate(TASK_ORDER):
        current = getattr(program, f"task_{ordinal}").signature.instructions
        original = originals.get(task)
        prompts[task] = (
            original if original is not None and current == original.rstrip() else current
        )
    return prompts


def demonstrations_from_program(
    program: Any,
    task: str,
    authorized: dict[tuple[str, str, str], str],
) -> list[CandidateDemonstration]:
    """Extract bounded DSPy demos and bind each input to frozen train authority."""
    predictor = getattr(program, f"task_{TASK_ORDER.index(task)}")
    result: list[CandidateDemonstration] = []
    for demo in getattr(predictor, "demos", []):
        value = demo.toDict() if hasattr(demo, "toDict") else dict(demo)
        demo_task = value.get("task")
        model_id = value.get("model_id")
        selected_input = value.get("selected_input")
        response_json = value.get("response_json")
        if demo_task != task or model_id not in {"qwen", "phi"}:
            raise ValueError("BootstrapFewShot demonstration task/model authority mismatch")
        if not isinstance(selected_input, str) or not isinstance(response_json, str):
            raise ValueError("BootstrapFewShot demonstration fields are incomplete")
        key = (task, model_id, selected_input)
        if key not in authorized:
            raise ValueError("BootstrapFewShot demonstration input is outside train authority")
        result.append(
            demonstration_value(
                kind="bootstrapped" if value.get("augmented") is True else "labeled",
                case_alias=authorized[key],
                model_id=model_id,
                selected_input=selected_input,
                response_json=response_json,
            )
        )
    kinds = [item.kind for item in result]
    if len(result) > 2 or len(kinds) != len(set(kinds)):
        raise ValueError("BootstrapFewShot exceeded one labeled/one bootstrapped demonstration")
    return result


def package_compiled_program(
    parent: CandidatePackage,
    program: Any,
    *,
    optimizer: str,
    proposer_id: str | None,
    mutation_ordinal: int,
) -> CandidatePackage:
    if optimizer not in {"bootstrap-few-shot", "gepa"}:
        raise ValueError("unsupported optimizer lineage")
    return mutate_package(
        parent,
        prompts_from_program(program),
        optimizer=optimizer,  # type: ignore[arg-type]
        proposer_id=proposer_id,
        mutation_ordinal=mutation_ordinal,
    )


def proposer_lm(
    model: str,
    *,
    credential_mode: str,
    concurrency: int,
    budget_contract: dict[str, int | float],
    api_key: str | None = None,
    vertex_project: str | None = None,
    vertex_location: str | None = None,
    **kwargs: Any,
) -> Any:
    verify_compatibility()
    import dspy

    if concurrency != 1:
        raise ValueError("optimizer proposer concurrency must be one")
    required_budget_fields = {
        "max_calls",
        "max_input_tokens",
        "max_output_tokens",
        "input_usd_per_million",
        "output_usd_per_million",
        "max_cost_usd",
    }
    if set(budget_contract) != required_budget_fields:
        raise ValueError("optimizer proposer budget contract is incomplete")
    provider_kwargs: dict[str, Any]
    if credential_mode == "api-key-environment":
        if not api_key:
            raise RuntimeError("API-key proposer credential is unavailable")
        provider_kwargs = {"api_key": api_key}
    elif credential_mode == "vertex-adc":
        if api_key is not None or not vertex_project or vertex_location != "global":
            raise RuntimeError("Vertex ADC proposer runtime is incomplete")
        provider_kwargs = {
            "vertex_project": vertex_project,
            "vertex_location": vertex_location,
        }
    else:
        raise ValueError("unsupported optimizer proposer credential mode")
    return dspy.LM(model, **provider_kwargs, **kwargs)


def compile_bootstrap(
    program: Any,
    trainset: list[Any],
    metric: Callable[..., Any],
) -> Any:
    verify_compatibility()
    import dspy

    optimizer = dspy.BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=1,
        max_labeled_demos=1,
        max_rounds=1,
    )
    return optimizer.compile(program, trainset=trainset)


def compile_gepa(
    program: Any,
    trainset: list[Any],
    valset: list[Any],
    metric: Callable[..., Any],
    reflection_lm: Any,
    *,
    seed: int,
    max_metric_calls: int,
    log_dir: Path,
) -> Any:
    verify_compatibility()
    import dspy

    optimizer = dspy.GEPA(
        metric=metric,
        max_metric_calls=max_metric_calls,
        reflection_lm=reflection_lm,
        candidate_selection_strategy="pareto",
        num_threads=1,
        track_stats=True,
        track_best_outputs=True,
        seed=seed,
        log_dir=str(log_dir),
    )
    return optimizer.compile(program, trainset=trainset, valset=valset)


def save_state_only(program: Any, path: Path) -> None:
    if path.suffix.casefold() != ".json":
        raise ValueError("compiled DSPy state must use JSON")
    program.save(str(path), save_program=False)


def load_state_only(program: Any, path: Path) -> None:
    if path.suffix.casefold() != ".json":
        raise ValueError("unsafe compiled DSPy state serialization")
    program.load(str(path), allow_pickle=False, allow_unsafe_lm_state=False)
