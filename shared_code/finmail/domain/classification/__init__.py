"""
Classification package.

Provides functionality for classifying transactions based on configurable rules.
"""

from shared_code.finmail.domain.classification.classification_rules import (
    ClassificationRule,
)
from shared_code.finmail.domain.classification.classifier import TransactionClassifier
from shared_code.finmail.domain.classification.rule_providers import (
    GoogleSheetsRuleProvider,
    RuleProvider,
)

__all__ = [
    "ClassificationRule",
    "GoogleSheetsRuleProvider",
    "RuleProvider",
    "TransactionClassifier",
]
