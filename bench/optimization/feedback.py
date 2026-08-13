"""Bounded structured diagnostics suitable for reflective optimization."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import Field, field_validator

from bench.models import StrictModel

_FORBIDDEN = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer\s|password|secret|token\s*[=:]|[A-Z0-9]{24,})"
)


class Diagnostic(StrictModel):
    category: Literal[
        "schema",
        "invalid-enum",
        "evidence-mismatch",
        "cross-field",
        "date-mismatch",
        "label-mismatch",
        "timeout",
        "provider-failure",
        "context-boundary",
    ]
    schema_path: str = Field(default="$", max_length=120)
    expected: str | None = Field(default=None, max_length=120)
    observed: str | None = Field(default=None, max_length=120)

    @field_validator("schema_path", "expected", "observed")
    @classmethod
    def safe_fact(cls, value: str | None) -> str | None:
        if value is not None and (_FORBIDDEN.search(value) or "\n" in value):
            raise ValueError("optimizer feedback contains forbidden or unbounded content")
        return value


def render_feedback(diagnostics: list[Diagnostic]) -> str:
    if not diagnostics:
        return "valid: no deterministic contract violation"
    rows = []
    for item in diagnostics:
        row = f"{item.category} at {item.schema_path}"
        if item.expected is not None:
            row += f"; expected={item.expected}"
        if item.observed is not None:
            row += f"; observed={item.observed}"
        rows.append(row)
    return "\n".join(rows)
