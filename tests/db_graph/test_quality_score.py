import pytest

from src.db_graph.quality_score import calculate_quality_score


def test_quality_score():
    score = calculate_quality_score(
        completeness=0.9,
        standard_match=0.8,
        version_validity=1.0,
        compliance_evidence=0.7,
        source_verification=1.0
    )

    assert score == 87.0


def test_perfect_score():
    score = calculate_quality_score(
        completeness=1.0,
        standard_match=1.0,
        version_validity=1.0,
        compliance_evidence=1.0,
        source_verification=1.0
    )

    assert score == 100.0


def test_zero_score():
    score = calculate_quality_score(
        completeness=0,
        standard_match=0,
        version_validity=0,
        compliance_evidence=0,
        source_verification=0
    )

    assert score == 0.0


def test_invalid_score():
    with pytest.raises(ValueError):
        calculate_quality_score(
            completeness=1.5,
            standard_match=0.8,
            version_validity=1.0,
            compliance_evidence=0.7,
            source_verification=1.0
        )