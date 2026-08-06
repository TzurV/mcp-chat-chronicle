"""Fail-closed prompt promotion privacy scanner."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable, Mapping
from typing import Literal

from pydantic import Field, StrictInt

from bench.models import StrictModel

from .package import CandidatePackage

SCANNER_VERSION = "optimizer-prompt-privacy-v1"
NGRAM_WORDS = 8
_URL = re.compile(r"(?i)\bhttps?://[^\s]+")
_PATH = re.compile(r"(?:[A-Za-z]:\\|/)[^\s]{4,}")
_LONG_ID = re.compile(r"\b(?:\d[ -]?){10,}\b")


class PrivacyFinding(StrictModel):
    task: str
    category: str
    fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")


class PrivacyResult(StrictModel):
    scanner_version: str = SCANNER_VERSION
    ngram_words: Literal[8] = NGRAM_WORDS
    eligible: bool
    finding_count: StrictInt = Field(ge=0)
    counts: dict[str, StrictInt]
    findings: list[PrivacyFinding]


def scan_package(
    package: CandidatePackage,
    private_texts: Iterable[str],
    *,
    exact_values: Iterable[str] = (),
    environment: Mapping[str, str] | None = None,
) -> PrivacyResult:
    """Scan without retaining or returning the matched private values."""
    import hashlib

    values = [value for value in private_texts if value]
    env = os.environ if environment is None else environment
    secrets = [value for value in env.values() if len(value) >= 8]
    exact_sensitive: set[str] = {value for value in exact_values if value}
    exact_sensitive.update(secrets)
    source_ngrams: set[tuple[str, ...]] = set()
    for value in values:
        exact_sensitive.update(_URL.findall(value))
        exact_sensitive.update(_PATH.findall(value))
        exact_sensitive.update(_LONG_ID.findall(value))
        words = _words(value)
        source_ngrams.update(zip(*(words[offset:] for offset in range(NGRAM_WORDS)), strict=False))
    findings: list[PrivacyFinding] = []
    for task, prompt in package.prompts.items():
        surfaces = [prompt.text]
        for demonstration in package.demonstrations[task]:
            surfaces.extend((demonstration.selected_input, demonstration.response_json))
        rendered = "\n".join(surfaces)
        lowered = rendered.casefold()
        categories: set[str] = set()
        if any(item.casefold() in lowered for item in exact_sensitive if len(item) >= 4):
            categories.add("exact-sensitive-value")
        prompt_words = _words(rendered)
        prompt_ngrams = set(
            zip(*(prompt_words[offset:] for offset in range(NGRAM_WORDS)), strict=False)
        )
        if prompt_ngrams & source_ngrams:
            categories.add("source-ngram-overlap")
        for category in sorted(categories):
            fingerprint = hashlib.sha256(f"{task}\n{category}".encode()).hexdigest()
            findings.append(PrivacyFinding(task=task, category=category, fingerprint=fingerprint))
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.category] = counts.get(finding.category, 0) + 1
    return PrivacyResult(
        eligible=not findings,
        finding_count=len(findings),
        counts=dict(sorted(counts.items())),
        findings=findings,
    )


def _words(value: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9_-]*", value.casefold())
