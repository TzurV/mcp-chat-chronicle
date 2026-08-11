"""Lazy DSPy adapters for one four-component Chronicle program."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable
from dataclasses import dataclass
from numbers import Real
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


@dataclass(frozen=True)
class DemoAuthority:
    """Trusted compile provenance kept outside DSPy's generated demo fields."""

    task: str
    model_id: str
    selected_input_sha256: str
    response_json_sha256: str


BOOTSTRAP_ACCEPTANCE_THRESHOLD = 0.999


def bootstrap_metric_acceptance(value: Any) -> bool:
    """Convert a Bootstrap metric result to DSPy's literal acceptance boolean."""
    score = getattr(value, "score", value)
    if not isinstance(score, Real):
        raise TypeError("BootstrapFewShot metric score must be numeric")
    normalized = float(score)
    if not math.isfinite(normalized):
        raise ValueError("BootstrapFewShot metric score must be finite")
    return normalized >= BOOTSTRAP_ACCEPTANCE_THRESHOLD


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
    provenance = getattr(program, "_chronicle_demo_authority", {})
    result: list[CandidateDemonstration] = []
    for demo in getattr(predictor, "demos", []):
        value = demo.toDict() if hasattr(demo, "toDict") else dict(demo)
        selected_input = value.get("selected_input")
        response_json = value.get("response_json")
        trusted = provenance.get(id(demo))
        if not isinstance(trusted, DemoAuthority):
            raise ValueError("BootstrapFewShot demonstration provenance is missing or ambiguous")
        if trusted.task != task or trusted.model_id not in {"qwen", "phi"}:
            raise ValueError("BootstrapFewShot demonstration task/model authority mismatch")
        if not isinstance(selected_input, str) or not isinstance(response_json, str):
            raise ValueError("BootstrapFewShot demonstration fields are incomplete")
        if (
            hashlib.sha256(selected_input.encode()).hexdigest() != trusted.selected_input_sha256
            or hashlib.sha256(response_json.encode()).hexdigest() != trusted.response_json_sha256
        ):
            raise ValueError("BootstrapFewShot demonstration compile provenance mismatch")
        key = (task, trusted.model_id, selected_input)
        if key not in authorized:
            raise ValueError("BootstrapFewShot demonstration input is outside train authority")
        result.append(
            demonstration_value(
                kind="bootstrapped" if value.get("augmented") is True else "labeled",
                case_alias=authorized[key],
                model_id=trusted.model_id,
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
    *,
    task: str,
    history_sink: Callable[[list[Any]], None] | None = None,
) -> Any:
    verify_compatibility()
    import dspy

    if task not in TASK_ORDER:
        raise ValueError("unknown BootstrapFewShot task authority")

    trusted_examples: dict[int, DemoAuthority] = {}
    for example in trainset:
        value = example.toDict() if hasattr(example, "toDict") else dict(example)
        selected_input = value.get("selected_input")
        response_json = value.get("response_json")
        if value.get("task") != task or value.get("model_id") not in {"qwen", "phi"}:
            raise ValueError("BootstrapFewShot train example provenance is invalid")
        if not isinstance(selected_input, str) or not isinstance(response_json, str):
            raise ValueError("BootstrapFewShot train example fields are incomplete")
        trusted_examples[id(example)] = DemoAuthority(
            task=task,
            model_id=value["model_id"],
            selected_input_sha256=hashlib.sha256(selected_input.encode()).hexdigest(),
            response_json_sha256=hashlib.sha256(response_json.encode()).hexdigest(),
        )

    trace_authority: dict[tuple[str, str], set[DemoAuthority]] = {}

    def traced_metric(gold: Any, pred: Any, trace: Any = None, **kwargs: Any) -> bool:
        accepted = bootstrap_metric_acceptance(metric(gold, pred, trace, **kwargs))
        if not accepted:
            return False
        authority = trusted_examples.get(id(gold))
        if authority is None:
            raise ValueError("BootstrapFewShot metric provenance is outside train authority")
        for _, inputs, outputs in trace or []:
            selected_input = (
                inputs.get("selected_input")
                if isinstance(inputs, dict)
                else getattr(inputs, "selected_input", None)
            )
            response_json = (
                outputs.get("response_json")
                if isinstance(outputs, dict)
                else getattr(outputs, "response_json", None)
            )
            if not isinstance(selected_input, str) or not isinstance(response_json, str):
                raise ValueError("BootstrapFewShot generated trace fields are incomplete")
            captured = DemoAuthority(
                task=authority.task,
                model_id=authority.model_id,
                selected_input_sha256=hashlib.sha256(selected_input.encode()).hexdigest(),
                response_json_sha256=hashlib.sha256(response_json.encode()).hexdigest(),
            )
            key = (captured.selected_input_sha256, captured.response_json_sha256)
            trace_authority.setdefault(key, set()).add(captured)
        return True

    optimizer = dspy.BootstrapFewShot(
        metric=traced_metric,
        max_bootstrapped_demos=1,
        max_labeled_demos=1,
        max_rounds=1,
    )
    try:
        compiled = optimizer.compile(program, trainset=trainset)
    finally:
        teacher = getattr(optimizer, "teacher", None)
        teacher_lms = getattr(teacher, "_chronicle_lms", {})
        if history_sink is not None:
            history_sink(list(teacher_lms.values()))
    compiled_authority: dict[int, DemoAuthority] = {}
    predictor = getattr(compiled, f"task_{TASK_ORDER.index(task)}")
    for demo in getattr(predictor, "demos", []):
        value = demo.toDict() if hasattr(demo, "toDict") else dict(demo)
        selected_input = value.get("selected_input")
        response_json = value.get("response_json")
        if not isinstance(selected_input, str) or not isinstance(response_json, str):
            raise ValueError("BootstrapFewShot compiled demonstration fields are incomplete")
        selected_hash = hashlib.sha256(selected_input.encode()).hexdigest()
        response_hash = hashlib.sha256(response_json.encode()).hexdigest()
        if value.get("augmented") is True:
            matches = trace_authority.get((selected_hash, response_hash), set())
        else:
            matches = {
                authority
                for example_id, authority in trusted_examples.items()
                if example_id == id(demo)
                and authority.task == value.get("task")
                and authority.model_id == value.get("model_id")
                and authority.selected_input_sha256 == selected_hash
                and authority.response_json_sha256 == response_hash
            }
        if len(matches) != 1:
            raise ValueError("BootstrapFewShot compiled provenance is missing or ambiguous")
        compiled_authority[id(demo)] = next(iter(matches))
    compiled._chronicle_demo_authority = compiled_authority
    return compiled


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
