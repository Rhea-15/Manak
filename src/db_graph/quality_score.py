"""Quality scoring utilities for db_graph standards."""

from __future__ import annotations


_WEIGHTS = {
    "completeness": 35,
    "standard_match": 25,
    "version_validity": 20,
    "compliance_evidence": 15,
    "source_verification": 5,
}


def calculate_quality_score(
    *,
    completeness: float,
    standard_match: float,
    version_validity: float,
    compliance_evidence: float,
    source_verification: float,
) -> float:
    """Return a 0-100 quality score using the project scoring weights.

    All metrics must be between 0 and 1 inclusive. Values outside this range raise
    ValueError to prevent invalid scores from being generated.
    """
    values = {
        "completeness": completeness,
        "standard_match": standard_match,
        "version_validity": version_validity,
        "compliance_evidence": compliance_evidence,
        "source_verification": source_verification,
    }

    for name, value in values.items():
        numeric_value = float(value)
        if not 0 <= numeric_value <= 1:
            raise ValueError(f"{name} must be between 0 and 1 inclusive")

    score = sum(
        float(value) * weight
        for value, weight in zip(values.values(), _WEIGHTS.values())
    )
    return round(score, 2)
