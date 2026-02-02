from datetime import UTC, datetime

import pytest
from dateutil import tz
from pydantic import ValidationError

from shared_code.finmail.core.config import settings
from shared_code.finmail.models import EmailPayload, Transaction


def test_transaction_creation_with_required_fields():
    transaction = Transaction(
        date_local=datetime(2026, 1, 15, 10, 30),
        pocket="Test Bank",
        amount=1000.0,
        currency="COP",
    )

    assert transaction.date_local == datetime(2026, 1, 15, 10, 30)
    assert transaction.pocket == "Test Bank"
    assert transaction.amount == 1000.0
    assert transaction.currency == "COP"
    assert transaction.category == settings.DEFAULT_CATEGORY


def test_transaction_with_all_fields():
    transaction = Transaction(
        date_local=datetime(2026, 1, 15, 10, 30),
        pocket="Test Bank",
        category="Food",
        amount=-50.0,
        currency="USD",
        description="Coffee shop purchase",
        notes="Morning coffee",
        merchant="Starbucks",
        account_last4="1234",
        auth_code="ABC123",
    )

    assert transaction.date_local == datetime(2026, 1, 15, 10, 30)
    assert transaction.pocket == "Test Bank"
    assert transaction.category == "Food"
    assert transaction.amount == -50.0
    assert transaction.currency == "USD"
    assert transaction.description == "Coffee shop purchase"
    assert transaction.notes == "Morning coffee"
    assert transaction.merchant == "Starbucks"
    assert transaction.account_last4 == "1234"
    assert transaction.auth_code == "ABC123"


def test_transaction_default_category():
    transaction = Transaction(
        date_local=datetime(2026, 1, 15, 10, 30),
        pocket="Test Bank",
        amount=100.0,
        currency="COP",
    )

    assert transaction.category == settings.DEFAULT_CATEGORY


def test_email_payload_creation_minimal():
    payload = EmailPayload(
        subject="Test Subject",
        sender="test@example.com",
    )

    assert payload.subject == "Test Subject"
    assert payload.sender == "test@example.com"
    assert payload.html is None
    assert payload.received_at is None


def test_email_payload_with_html():
    html_content = "<html><body>Test email</body></html>"
    payload = EmailPayload(
        subject="Test Subject",
        sender="test@example.com",
        html=html_content,
    )

    assert payload.html == html_content


def test_received_at_naive_datetime_converted_to_utc_then_default_tz():
    naive_dt = datetime(2026, 2, 1, 12, 0, 0)
    payload = EmailPayload(
        subject="Test",
        sender="test@example.com",
        received_at=naive_dt,
    )

    # Should be converted to default timezone
    default_tz = tz.gettz(settings.DEFAULT_TZ)
    expected_dt = naive_dt.replace(tzinfo=UTC).astimezone(default_tz)

    assert payload.received_at == expected_dt
    assert payload.received_at.tzinfo == expected_dt.tzinfo


def test_received_at_with_utc_timezone_converted_to_default_tz():
    utc_dt = datetime(2026, 2, 1, 12, 0, 0, tzinfo=UTC)
    payload = EmailPayload(
        subject="Test",
        sender="test@example.com",
        received_at=utc_dt,
    )

    # Should be converted to default timezone
    default_tz = tz.gettz(settings.DEFAULT_TZ)
    expected_dt = utc_dt.astimezone(default_tz)

    assert payload.received_at == expected_dt
    assert payload.received_at.tzinfo == expected_dt.tzinfo


def test_received_at_with_different_timezone_converted_to_default_tz():
    # Use US/Eastern timezone
    eastern_tz = tz.gettz("US/Eastern")
    eastern_dt = datetime(2026, 2, 1, 12, 0, 0, tzinfo=eastern_tz)

    payload = EmailPayload(
        subject="Test",
        sender="test@example.com",
        received_at=eastern_dt,
    )

    # Should be converted to default timezone
    default_tz = tz.gettz(settings.DEFAULT_TZ)
    expected_dt = eastern_dt.astimezone(default_tz)

    assert payload.received_at == expected_dt
    assert payload.received_at.tzinfo == expected_dt.tzinfo


def test_received_at_none_remains_none():
    """Test that None value for received_at remains None."""
    payload = EmailPayload(
        subject="Test",
        sender="test@example.com",
        received_at=None,
    )

    assert payload.received_at is None


def test_get_soup_with_html():
    html_content = "<html><body><p>Test</p></body></html>"
    payload = EmailPayload(
        subject="Test",
        sender="test@example.com",
        html=html_content,
    )

    soup = payload.get_soup()
    assert soup is not None
    assert soup.find("p") is not None


def test_get_soup_without_html():
    payload = EmailPayload(
        subject="Test",
        sender="test@example.com",
    )

    soup = payload.get_soup()
    assert soup is not None


def test_invalid_email_raises_validation_error():
    with pytest.raises(ValidationError):
        EmailPayload(
            subject="Test",
            sender="invalid-email",
        )
