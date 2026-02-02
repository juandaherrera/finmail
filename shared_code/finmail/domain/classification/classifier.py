"""
Transaction classifier module.

Contains the TransactionClassifier class for classifying transactions
based on multi-condition rules.
"""

import logging
import re

from shared_code.finmail.domain.classification.classification_rules import (
    parse_conditions,
)
from shared_code.finmail.domain.classification.rule_providers import (
    RuleProvider,
)
from shared_code.finmail.models import Transaction

logger = logging.getLogger(__name__)


class TransactionClassifier:
    """
    Classifies transactions based on multi-condition classification rules.

    The classifier evaluates rules with AND logic - all conditions in a rule
    must match for the rule to apply. Rules are evaluated in order and the
    first matching rule determines the category.
    """

    def __init__(self, rule_provider: RuleProvider) -> None:
        """
        Initialize the transaction classifier.

        Parameters
        ----------
        rule_provider : RuleProvider
            The provider to load classification rules from.
        """
        self.rule_provider = rule_provider
        self._compiled_rules: list[tuple[list[tuple[str, re.Pattern]], str]] | None = (
            None
        )

    def _load_and_compile_rules(self) -> None:
        """
        Load rules from provider and compile regex patterns.

        Creates a list of (conditions_list, category) tuples where
        conditions_list is a list of (field_name, compiled_pattern) tuples.
        """
        rules = self.rule_provider.get_rules()
        self._compiled_rules = []

        for rule in rules:
            # Parse the expression into (field_name, pattern) tuples
            parsed_conditions = parse_conditions(rule.conditions)

            # Compile all patterns
            compiled_conditions = []
            for field_name, pattern in parsed_conditions:
                try:
                    compiled_pattern = re.compile(pattern, re.IGNORECASE)
                    compiled_conditions.append((field_name, compiled_pattern))
                except re.error as e:
                    logger.warning(
                        "Skipping invalid regex pattern '%s' for field '%s': %s",
                        pattern,
                        field_name,
                        e,
                    )
                    continue

            # Only add rule if all patterns compiled successfully
            if len(compiled_conditions) == len(parsed_conditions):
                self._compiled_rules.append((compiled_conditions, rule.category))

        logger.info(
            "Loaded and compiled %d classification rules", len(self._compiled_rules)
        )

    def classify(self, transaction: Transaction) -> Transaction:
        """
        Classify a transaction by applying classification rules.

        Rules are evaluated in order. The first rule where ALL conditions
        match (AND logic) determines the category.

        Parameters
        ----------
        transaction : Transaction
            The transaction to classify.

        Returns
        -------
        Transaction
            A new transaction instance with the classified category.
        """
        # Lazy load rules on first call
        if self._compiled_rules is None:
            self._load_and_compile_rules()

        # Try each rule in order
        for conditions_list, category in self._compiled_rules:
            # Check if ALL conditions match (AND logic)
            all_match = True

            for field_name, compiled_pattern in conditions_list:
                # Get field value from transaction
                field_value = getattr(transaction, field_name, None)

                # If field doesn't exist or is None, condition fails
                if field_value is None:
                    all_match = False
                    break

                # Check if pattern matches
                if not compiled_pattern.search(str(field_value)):
                    all_match = False
                    break

            # If all conditions matched, apply this category
            if all_match:
                return transaction.model_copy(update={"category": category})

        # No rules matched, return unchanged
        return transaction
