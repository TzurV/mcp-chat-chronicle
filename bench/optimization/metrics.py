"""Reliability-first optimizer metrics and DSPy scalar adaptation."""

from __future__ import annotations

from functools import total_ordering

from pydantic import Field

from bench.models import StrictModel

SEMANTIC_SCALE = 1_000_000
TOKEN_SCALE = 1_000_000


@total_ordering
class MetricVector(StrictModel):
    total_valid: int = Field(ge=0, le=80)
    worst_model_valid: int = Field(ge=0, le=40)
    minimum_task_valid: int = Field(ge=0, le=20)
    semantic_agreement: float = Field(ge=0, le=1)
    complete_package_uts: float | None = Field(default=None, ge=0, le=1)
    prompt_tokens: int = Field(ge=0)
    candidate_id: str

    def ordering_key(self) -> tuple[int, int, int, int, int, int, str]:
        semantic = round(self.semantic_agreement * SEMANTIC_SCALE)
        uts = (
            -1
            if self.complete_package_uts is None
            else round(self.complete_package_uts * SEMANTIC_SCALE)
        )
        tokens = min(self.prompt_tokens, TOKEN_SCALE)
        return (
            self.total_valid,
            self.worst_model_valid,
            self.minimum_task_valid,
            semantic,
            uts,
            -tokens,
            _reverse_text(self.candidate_id),
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, MetricVector):
            return NotImplemented
        return self.ordering_key() < other.ordering_key()

    def scalar(self) -> float:
        """Map criteria 1-6 to a scalar without allowing lower-level compensation."""
        semantic = round(self.semantic_agreement * SEMANTIC_SCALE) / (SEMANTIC_SCALE + 1)
        uts_raw = (
            0
            if self.complete_package_uts is None
            else round(self.complete_package_uts * SEMANTIC_SCALE) + 1
        )
        uts = uts_raw / (SEMANTIC_SCALE + 2)
        token_score = (TOKEN_SCALE - min(self.prompt_tokens, TOKEN_SCALE)) / (TOKEN_SCALE + 1)
        nested = semantic + (uts + token_score / 2) / (SEMANTIC_SCALE + 2)
        nested = self.minimum_task_valid + nested / 2
        nested = self.worst_model_valid + nested / 21
        return self.total_valid + nested / 41


def _reverse_text(value: str) -> str:
    # Lexically smaller candidate ids win exact ties. This transforms them so max() does that.
    return "".join(chr(0x10FFFF - ord(char)) for char in value)
