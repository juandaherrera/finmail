"""Tests for classification rules."""

import pytest

from shared_code.finmail.domain.classification import ClassificationRule


def test_valid_rule_creation() -> None:
    """Test creating a valid classification rule with single condition."""
    rule = ClassificationRule(
        conditions="merchant:.*uber.*",
        category="Transport",
    )

    assert rule.conditions == "merchant:.*uber.*"
    assert rule.category == "Transport"


def test_valid_multi_condition_rule() -> None:
    """Test creating a valid rule with multiple conditions."""
    rule = ClassificationRule(
        conditions="pocket:.*Rappi.* AND description:.*food.*",
        category="Food",
    )

    assert rule.conditions == "pocket:.*Rappi.* AND description:.*food.*"
    assert rule.category == "Food"


def test_regex_with_colon() -> None:
    """Test that regex patterns containing ':' work correctly."""
    rule = ClassificationRule(
        conditions=r"description:.*\d{2}:\d{2}.*",
        category="Time Reference",
    )

    assert rule.conditions == r"description:.*\d{2}:\d{2}.*"
    assert rule.category == "Time Reference"


def test_invalid_regex_pattern() -> None:
    """Test that invalid regex patterns are rejected."""
    with pytest.raises(ValueError, match="Invalid regex pattern"):
        ClassificationRule(
            conditions="merchant:[invalid(regex",
            category="Transport",
        )


def test_invalid_condition_format_missing_colon() -> None:
    """Test that conditions without colons are rejected."""
    with pytest.raises(ValueError, match="Invalid condition format"):
        ClassificationRule(
            conditions="merchant_no_colon",
            category="Transport",
        )


def test_multi_condition_with_invalid_regex() -> None:
    """Test that multi-conditions with any invalid regex are rejected."""
    with pytest.raises(ValueError, match="Invalid regex pattern"):
        ClassificationRule(
            conditions="merchant:.*uber.* AND description:[invalid(",
            category="Transport",
        )
