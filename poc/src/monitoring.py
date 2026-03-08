from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class CheckResult:
    name: str
    passed: bool
    severity: str
    details: str


_PHRASES_HARSH = [
    "you must",
    "that's not my problem",
    "obviously",
    "calm down",
    "as I said",
]


def _contains_phi_like(text: str) -> bool:
    # PoC-only heuristics: phone numbers, SSN-like, diagnosis keywords.
    phone = re.search(r"\b\d{3}[- .]?\d{3}[- .]?\d{4}\b", text)
    ssn = re.search(r"\b\d{3}-\d{2}-\d{4}\b", text)
    dx = re.search(r"\b(HIV|AIDS|cancer|chemotherapy|substance use)\b", text, re.IGNORECASE)
    return bool(phone or ssn or dx)


def _tone_ok(text: str) -> bool:
    t = text.lower()
    return not any(p in t for p in _PHRASES_HARSH)


def _has_some_citations(text: str) -> bool:
    # PoC: encourage citations like [source: ...]
    return "[source" in text.lower() or "citation" in text.lower() or "http" in text.lower()


def run_output_checks(text: str, context: dict | None = None) -> dict:
    context = context or {}

    results: list[CheckResult] = []

    phi_flag = _contains_phi_like(text)
    results.append(
        CheckResult(
            name="PHI/PII leak heuristic",
            passed=not phi_flag,
            severity="high" if phi_flag else "low",
            details="Potential PHI/PII patterns detected" if phi_flag else "No obvious PHI/PII patterns detected",
        )
    )

    tone_flag = _tone_ok(text)
    results.append(
        CheckResult(
            name="Tone check (basic)",
            passed=tone_flag,
            severity="medium" if not tone_flag else "low",
            details="Harsh/unsafe phrasing detected" if not tone_flag else "Tone looks acceptable",
        )
    )

    cite_flag = _has_some_citations(text)
    results.append(
        CheckResult(
            name="Citations present (heuristic)",
            passed=cite_flag,
            severity="medium" if not cite_flag else "low",
            details="No citation-like markers detected" if not cite_flag else "Some citation-like markers detected",
        )
    )

    return {
        "context": context,
        "checks": [r.__dict__ for r in results],
        "overall_pass": all(r.passed for r in results if r.severity in ("high", "medium")),
    }
