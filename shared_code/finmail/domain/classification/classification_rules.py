"""
Classification rules module.

Contains the ClassificationRule model for validating and representing
transaction classification rules with support for multi-condition expressions.
"""

import re

from pydantic import BaseModel, Field, field_validator


def parse_conditions(expression: str) -> list[tuple[str, str]]:
    """
    Parse condition expression into list of (field_name, pattern) tuples.

    Supports single and multi-condition expressions with AND logic.

    Parameters
    ----------
    expression : str
        Condition expression (e.g., "merchant:.*uber.*" or
        "pocket:.*Rappi.* AND description:.*food.*").

    Returns
    -------
    list[tuple[str, str]]
        List of (field_name, pattern) tuples.

    Raises
    ------
    ValueError
        If the condition format is invalid (missing colon).

    Examples
    --------
    >>> parse_conditions("merchant:.*uber.*")
    [("merchant", ".*uber.*")]
    >>> parse_conditions("pocket:.*Rappi.* AND description:.*food.*")
    [("pocket", ".*Rappi.*"), ("description", ".*food.*")]
    """
    conditions = []
    parts = expression.split(" AND ")

    for part in parts:
        condition = part.strip()
        if ":" not in condition:
            raise ValueError(
                f"Invalid condition format: {condition}. Expected 'field:pattern'"
            )

        # Split only on first ':', allowing ':' in regex pattern
        field_name, pattern = condition.split(":", 1)
        conditions.append((field_name.strip(), pattern.strip()))

    return conditions


class ClassificationRule(BaseModel):
    """
    Represents a classification rule with multi-condition support.

    Rules use expression syntax: 'field:pattern [AND field:pattern ...]'
    where all conditions must match (AND logic) for the rule to apply.
    """

    conditions: str = Field(
        description=(
            "Condition expression using 'field:pattern [AND field:pattern ...]' syntax"
        ),
        examples=["merchant:.*uber.*", "pocket:.*Rappi.* AND description:.*food.*"],
    )
    category: str = Field(
        description="The category to assign when all conditions match",
        examples=["Transport", "Food", "Transfer"],
    )

    @field_validator("conditions")
    @classmethod
    def validate_conditions(cls, value: str) -> str:
        """
        Validate that the conditions expression is properly formatted.

        Validates that:
        1. Expression can be parsed
        2. All patterns are valid regex

        Parameters
        ----------
        value : str
            The conditions expression to validate.

        Returns
        -------
        str
            The validated expression.

        Raises
        ------
        ValueError
            If the expression format is invalid or contains invalid regex.
        """
        try:
            parsed_conditions = parse_conditions(value)
        except ValueError as e:
            raise ValueError(f"Invalid condition expression: {e}") from e

        # Validate each regex pattern
        for field_name, pattern in parsed_conditions:
            try:
                re.compile(pattern)
            except re.error as e:
                msg = f"Invalid regex pattern '{pattern}' for field '{field_name}': {e}"
                raise ValueError(msg) from e

        return value
