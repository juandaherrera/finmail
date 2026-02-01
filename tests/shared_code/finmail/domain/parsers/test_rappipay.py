from datetime import datetime

import pytest
from bs4 import BeautifulSoup

from shared_code.finmail.domain.parsers.rappipay import RappiPayParser
from shared_code.finmail.models import Transaction


@pytest.fixture
def parser():
    return RappiPayParser()


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


def test_matches_pse(parser: RappiPayParser):
    # Simulate forwarded email structure for extract_subject
    html = """
    <div>
        ---------- Forwarded message ---------<br>
        Subject: Resumen compra con Pse<br>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    assert parser.matches("other@email.com", "Fwd: message", soup)


def test_parse_incoming(parser: RappiPayParser, rappipay_in_soup: BeautifulSoup):
    transaction = parser.parse("noreply@rappipay.co", "Subject", rappipay_in_soup)

    assert isinstance(transaction, Transaction)
    assert transaction.amount == 3603950.0
    assert transaction.pocket == "RappiCuenta"
    assert transaction.currency == "COP"
    assert transaction.date_local == datetime(2026, 1, 30, 10, 10)
    assert transaction.merchant == "BANCOLOMBIA"
    assert "Bancolombia" in transaction.description


def test_parse_outgoing(parser: RappiPayParser, rappipay_out_soup: BeautifulSoup):
    transaction = parser.parse("noreply@rappipay.co", "Subject", rappipay_out_soup)

    assert isinstance(transaction, Transaction)
    assert transaction.amount == -110000.0
    assert transaction.pocket == "RappiCuenta"
    assert transaction.currency == "COP"
    assert transaction.date_local == datetime(2026, 1, 10, 22, 25)
    assert transaction.merchant == "BANCOLOMBIA"
    assert "Bancolombia" in transaction.description
    assert "****9119" in transaction.description


def test_parse_pse_payment(parser: RappiPayParser, rappipay_pse_soup: BeautifulSoup):
    transaction = parser.parse("noreply@rappipay.co", "Subject", rappipay_pse_soup)

    assert isinstance(transaction, Transaction)
    assert transaction.amount == -908200.0
    assert transaction.pocket == "RappiCuenta"
    assert transaction.currency == "COP"
    assert transaction.date_local == datetime(2026, 2, 1, 11, 42)
    assert transaction.merchant == "APORTES EN LINEA"
    assert "Compra PSE" in transaction.description
    assert "APORTES EN LINEA" in transaction.description
