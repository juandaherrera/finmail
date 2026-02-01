from datetime import UTC, datetime

import pytest
from bs4 import BeautifulSoup

from shared_code.finmail.domain.parsers.remotepass import RemotePassParser


@pytest.mark.parametrize(
    "sender", ["no-reply@remotepass.team", "other@remotepass.com", "other@gmail.com"]
)
def test_remotepass_parser(remotepass_soup: BeautifulSoup, sender):
    subject = "Your transaction for 14.70 USD was approved."
    p = RemotePassParser()
    assert p.matches(sender, subject, remotepass_soup)

    tx = p.parse(sender, subject, remotepass_soup)

    assert tx.pocket == "RemotePass Cards"
    assert round(tx.amount, 2) == -14.70
    assert tx.currency == "USD"
    assert "BRAZZ BURGUER PENON CALI COL" in (tx.merchant or "")


def test_remotepass_payment_parse(remotepass_payment_soup: BeautifulSoup):
    p = RemotePassParser()
    sender = "no-reply@remotepass.team"
    subject = "Payment received"
    received_at = datetime(2026, 1, 26, 10, 16, tzinfo=UTC)

    assert p.matches(sender, subject, remotepass_payment_soup)

    tx = p.parse(sender, subject, remotepass_payment_soup, received_at=received_at)

    assert tx.pocket == "RemotePass"
    assert tx.amount == 250.0  # Positive amount
    assert tx.currency == "USD"
    assert tx.merchant == "RemotePass"
    assert "Payment received" in tx.description

    assert tx.date_local.hour == 10
    assert tx.date_local.minute == 16
