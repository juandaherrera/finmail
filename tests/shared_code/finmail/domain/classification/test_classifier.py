"""Tests for TransactionClassifier."""

from collections.abc import Callable
from datetime import datetime, timedelta

import pytest
from pytest_mock import MockerFixture

from shared_code.finmail.domain.classification import (
    ClassificationRule,
    TransactionClassifier,
)
from shared_code.finmail.models import Transaction

CreateTransactionType = Callable[..., Transaction]


@pytest.fixture
def create_transaction() -> CreateTransactionType:
    """
    Fixture to create test transactions.

    Returns
    -------
    CreateTransactionType
        Function to create Transaction instances for testing.
    """

    def _create_transaction(
        merchant: str | None = None,
        description: str | None = None,
        pocket: str = "Test Pocket",
    ) -> Transaction:
        return Transaction(
            date_local=datetime(2024, 1, 1, 12, 0),
            pocket=pocket,
            category="Pending Classification",
            currency="USD",
            amount=100.0,
            merchant=merchant,
            description=description,
        )

    return _create_transaction


def test_classify_single_match(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test classification with a single matching rule."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="merchant:.*uber.*",
            category="Transport",
        )
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)
    transaction = create_transaction(merchant="Uber Technologies")

    result = classifier.classify(transaction)

    assert result.category == "Transport"


def test_classify_multi_condition_match(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test classification with multi-condition rule (AND logic)."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="pocket:.*Rappi.* AND description:.*food.*",
            category="Food Delivery",
        )
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)
    transaction = create_transaction(
        pocket="Rappi Account", description="food delivery order"
    )

    result = classifier.classify(transaction)

    assert result.category == "Food Delivery"


def test_classify_multi_condition_partial_match_fails(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test that multi-condition rule fails if only some conditions match."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="pocket:.*Rappi.* AND description:.*food.*",
            category="Food Delivery",
        )
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)
    # Only pocket matches, description doesn't contain "food"
    transaction = create_transaction(
        pocket="Rappi Account", description="grocery shopping"
    )

    result = classifier.classify(transaction)

    # Should not match, category unchanged
    assert result.category == "Pending Classification"


def test_classify_first_match_wins(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test that the first matching rule wins."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="merchant:.*uber.*",
            category="Transport",
        ),
        ClassificationRule(
            conditions="merchant:.*technologies.*",
            category="Technology",
        ),
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)
    transaction = create_transaction(merchant="Uber Technologies")

    result = classifier.classify(transaction)

    # First rule should match
    assert result.category == "Transport"


def test_classify_no_match(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test classification when no rules match."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="merchant:.*uber.*",
            category="Transport",
        )
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)
    transaction = create_transaction(merchant="Amazon")

    result = classifier.classify(transaction)

    # Should retain default category
    assert result.category == "Pending Classification"


def test_classify_case_insensitive(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test that pattern matching is case-insensitive."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="merchant:uber",
            category="Transport",
        )
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)
    transaction = create_transaction(merchant="UBER TECHNOLOGIES")

    result = classifier.classify(transaction)

    assert result.category == "Transport"


def test_classify_different_fields(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test classification on different transaction fields."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="description:.*transfer.*",
            category="Transfer",
        ),
        ClassificationRule(
            conditions="pocket:.*credit card.*",
            category="Credit",
        ),
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)

    # Test description match
    transaction1 = create_transaction(description="Bank transfer to John")
    result1 = classifier.classify(transaction1)
    assert result1.category == "Transfer"

    # Need to create new classifier for second test (rules are cached)
    classifier2 = TransactionClassifier(rule_provider=mock_provider)
    transaction2 = create_transaction(pocket="My Credit Card")
    result2 = classifier2.classify(transaction2)
    assert result2.category == "Credit"


def test_classify_none_field_value(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test classification when field value is None."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="merchant:.*uber.*",
            category="Transport",
        )
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)
    transaction = create_transaction(merchant=None)

    result = classifier.classify(transaction)

    # Should not match and retain default category
    assert result.category == "Pending Classification"


def test_classify_invalid_field_name(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test classification with invalid field name."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="nonexistent_field:.*test.*",
            category="Test",
        )
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)
    transaction = create_transaction(merchant="Test Merchant")

    result = classifier.classify(transaction)

    # Should not match and retain default category
    assert result.category == "Pending Classification"


def test_classify_no_rules(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test classification when no rules are available."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = []

    classifier = TransactionClassifier(rule_provider=mock_provider)
    transaction = create_transaction(merchant="Test")

    result = classifier.classify(transaction)

    assert result.category == "Pending Classification"


def test_classify_lazy_load_rules(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test that rules are loaded lazily on first classify call."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = []

    classifier = TransactionClassifier(rule_provider=mock_provider)

    # Rules should not be loaded yet
    mock_provider.get_rules.assert_not_called()

    transaction = create_transaction()
    classifier.classify(transaction)

    # Rules should be loaded now
    mock_provider.get_rules.assert_called_once()

    # Second classify should not reload rules
    classifier.classify(transaction)
    mock_provider.get_rules.assert_called_once()  # Still only once


def test_is_cache_expired_when_rules_not_loaded(mocker: MockerFixture) -> None:
    """Test that cache is expired when rules haven't been loaded yet."""
    mock_provider = mocker.Mock()
    classifier = TransactionClassifier(rule_provider=mock_provider)

    assert classifier._is_cache_expired() is True


def test_is_cache_expired_when_rules_loaded_at_is_none(mocker: MockerFixture) -> None:
    """Test that cache is expired when rules are loaded but timestamp is None."""
    mock_provider = mocker.Mock()
    classifier = TransactionClassifier(rule_provider=mock_provider)
    classifier._compiled_rules = []
    classifier._rules_loaded_at = None

    assert classifier._is_cache_expired() is True


def test_is_cache_expired_when_compiled_rules_is_none(mocker: MockerFixture) -> None:
    """Test that cache is expired when timestamp exists but rules are None."""
    mock_provider = mocker.Mock()
    classifier = TransactionClassifier(rule_provider=mock_provider)
    classifier._compiled_rules = None
    classifier._rules_loaded_at = datetime.now()

    assert classifier._is_cache_expired() is True


def test_is_cache_expired_when_within_ttl(mocker: MockerFixture) -> None:
    """Test that cache is not expired when within TTL period."""
    mock_provider = mocker.Mock()
    classifier = TransactionClassifier(rule_provider=mock_provider, ttl_min=60.0)
    classifier._compiled_rules = []
    classifier._rules_loaded_at = datetime.now() - timedelta(minutes=30)

    assert classifier._is_cache_expired() is False


def test_is_cache_expired_when_exactly_at_ttl(mocker: MockerFixture) -> None:
    """Test that cache is expired when exactly at TTL boundary."""
    mock_provider = mocker.Mock()
    classifier = TransactionClassifier(rule_provider=mock_provider, ttl_min=60.0)
    classifier._compiled_rules = []
    classifier._rules_loaded_at = datetime.now() - timedelta(minutes=60)

    assert classifier._is_cache_expired() is True


def test_is_cache_expired_when_beyond_ttl(mocker: MockerFixture) -> None:
    """Test that cache is expired when beyond TTL period."""
    mock_provider = mocker.Mock()
    classifier = TransactionClassifier(rule_provider=mock_provider, ttl_min=60.0)
    classifier._compiled_rules = []
    classifier._rules_loaded_at = datetime.now() - timedelta(minutes=61)

    assert classifier._is_cache_expired() is True


def test_is_cache_expired_with_custom_ttl(mocker: MockerFixture) -> None:
    """Test cache expiration with custom TTL value."""
    mock_provider = mocker.Mock()
    classifier = TransactionClassifier(rule_provider=mock_provider, ttl_min=5.0)
    classifier._compiled_rules = []
    classifier._rules_loaded_at = datetime.now() - timedelta(minutes=6)

    assert classifier._is_cache_expired() is True


def test_is_cache_expired_with_very_recent_load(mocker: MockerFixture) -> None:
    """Test that cache is not expired immediately after loading."""
    mock_provider = mocker.Mock()
    classifier = TransactionClassifier(rule_provider=mock_provider, ttl_min=60.0)
    classifier._compiled_rules = []
    classifier._rules_loaded_at = datetime.now()

    assert classifier._is_cache_expired() is False


def test_classify_amount_exact_match_ignoring_decimals(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test classification matching exact amount value ignoring decimals."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="amount:44900.*",
            category="Specific Payment",
        )
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)

    # Test with exact integer amount
    transaction1 = create_transaction(merchant="Test Merchant")
    transaction1.amount = 44900.0
    result1 = classifier.classify(transaction1)
    assert result1.category == "Specific Payment"

    # Test with decimals
    classifier2 = TransactionClassifier(rule_provider=mock_provider)
    transaction2 = create_transaction(merchant="Test Merchant")
    transaction2.amount = 44900.99
    result2 = classifier2.classify(transaction2)
    assert result2.category == "Specific Payment"

    # Test with different amount
    classifier3 = TransactionClassifier(rule_provider=mock_provider)
    transaction3 = create_transaction(merchant="Test Merchant")
    transaction3.amount = 44901.0
    result3 = classifier3.classify(transaction3)
    assert result3.category == "Pending Classification"


def test_classify_negative_amount(
    mocker: MockerFixture, create_transaction: CreateTransactionType
) -> None:
    """Test classification matching negative amount values."""
    mock_provider = mocker.Mock()
    mock_provider.get_rules.return_value = [
        ClassificationRule(
            conditions="amount:-.*",
            category="Expense",
        )
    ]

    classifier = TransactionClassifier(rule_provider=mock_provider)

    # Test with negative amount
    transaction1 = create_transaction(merchant="Test Merchant")
    transaction1.amount = -100.0
    result1 = classifier.classify(transaction1)
    assert result1.category == "Expense"

    # Test with negative decimal amount
    classifier2 = TransactionClassifier(rule_provider=mock_provider)
    transaction2 = create_transaction(merchant="Test Merchant")
    transaction2.amount = -50.75
    result2 = classifier2.classify(transaction2)
    assert result2.category == "Expense"

    # Test with positive amount (should not match)
    classifier3 = TransactionClassifier(rule_provider=mock_provider)
    transaction3 = create_transaction(merchant="Test Merchant")
    transaction3.amount = 100.0
    result3 = classifier3.classify(transaction3)
    assert result3.category == "Pending Classification"
