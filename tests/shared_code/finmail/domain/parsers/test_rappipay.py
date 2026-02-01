from datetime import datetime

import pytest
from bs4 import BeautifulSoup

from shared_code.finmail.domain.parsers.rappipay import RappiPayParser
from shared_code.finmail.models import Transaction


@pytest.fixture
def parser():
    return RappiPayParser()


@pytest.fixture
def rappipay_html():
    with open("tests/html_samples/rappipay_bank_transfer.html", encoding="utf-8") as f:
        return f.read()


def test_matches_valid_sender(parser: RappiPayParser):
    soup = BeautifulSoup("", "lxml")
    assert parser.matches("noreply@rappipay.co", "Subject", soup)


def test_matches_content(parser: RappiPayParser):
    # Simulate forwarded email structure for extract_subject
    html = """
    <div>
        ---------- Forwarded message ---------<br>
        Subject: RappiPay Transferencia Bancaria<br>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    assert parser.matches("other@email.com", "Fwd: message", soup)


def test_parse_sample(parser: RappiPayParser, rappipay_html: str):
    soup = BeautifulSoup(rappipay_html, "lxml")
    transaction = parser.parse("noreply@rappipay.co", "Subject", soup)

    assert isinstance(transaction, Transaction)
    assert transaction.amount == 3603950.0
    assert transaction.pocket == "RappiPay"
    assert transaction.currency == "COP"
    assert transaction.date_local == datetime(2026, 1, 30, 10, 10)
    assert "BANCOLOMBIA" in transaction.description
