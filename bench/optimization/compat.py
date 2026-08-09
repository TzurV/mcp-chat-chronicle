"""Fail-fast compatibility checks for the exact optional optimizer pins."""

from __future__ import annotations

import importlib.metadata
import inspect

EXPECTED_RESULT_FIELDS = {
    "candidates",
    "parents",
    "val_aggregate_scores",
    "val_subscores",
    "per_val_instance_best_candidates",
    "discovery_eval_counts",
    "best_outputs_valset",
    "total_metric_calls",
    "num_full_val_evals",
    "log_dir",
    "seed",
}


def verify_compatibility() -> dict[str, object]:
    try:
        import dspy
        from dspy.teleprompt.gepa.gepa import DspyGEPAResult
    except ImportError as exc:
        raise RuntimeError(
            "optimizer dependencies are absent; install the 'optimization' extra"
        ) from exc
    versions = {
        "dspy": importlib.metadata.version("dspy"),
        "gepa": importlib.metadata.version("gepa"),
    }
    if versions != {"dspy": "3.3.0", "gepa": "0.1.1"}:
        raise RuntimeError(f"optimizer version mismatch: {versions}")
    if any("a" in value or "b" in value or "rc" in value for value in versions.values()):
        raise RuntimeError("prerelease optimizer packages are not approved")
    gepa_parameters = set(inspect.signature(dspy.GEPA).parameters)
    required_gepa = {
        "metric",
        "max_metric_calls",
        "reflection_lm",
        "instruction_proposer",
        "track_stats",
        "seed",
    }
    bootstrap_parameters = set(inspect.signature(dspy.BootstrapFewShot).parameters)
    required_bootstrap = {
        "metric",
        "max_bootstrapped_demos",
        "max_labeled_demos",
        "max_rounds",
    }
    result_fields = set(DspyGEPAResult.__annotations__)
    if not required_gepa <= gepa_parameters:
        raise RuntimeError("pinned DSPy GEPA constructor API is incompatible")
    if not required_bootstrap <= bootstrap_parameters:
        raise RuntimeError("pinned DSPy BootstrapFewShot API is incompatible")
    bootstrap_compile = set(inspect.signature(dspy.BootstrapFewShot.compile).parameters)
    if not {"student", "teacher", "trainset"} <= bootstrap_compile:
        raise RuntimeError("pinned DSPy BootstrapFewShot compile API is incompatible")
    if result_fields != EXPECTED_RESULT_FIELDS:
        raise RuntimeError("pinned DSPy GEPA result schema is incompatible")
    if "allow_pickle" not in inspect.signature(dspy.Module.load).parameters:
        raise RuntimeError("pinned DSPy safe-load API is incompatible")
    return {
        "compatible": True,
        "versions": versions,
        "gepa_result_fields": sorted(result_fields),
        "safe_serialization": "state-only JSON; load allow_pickle=False",
    }
