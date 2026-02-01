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


@pytest.mark.parametrize(
    "subject",
    [
        "RappiPay Transferencia Bancaria",
        "Resumen compra con Pse",
        "¡Listo! Tu dinero está en camino",
        "Tu dinero ya está disponible.",
    ],
)
def test_matches_forwarded_content(parser: RappiPayParser, subject: str):
    # Simulate forwarded email structure for extract_subject
    html = f"""
    <div>
        ---------- Forwarded message ---------<br>
        Subject: {subject}<br>
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


def test_parse_llave_transfer_in(
    parser: RappiPayParser, rappipay_llave_transfer_in_soup: BeautifulSoup
):
    transaction = parser.parse(
        "noreply@rappipay.co", "Subject", rappipay_llave_transfer_in_soup
    )

    assert isinstance(transaction, Transaction)
    assert transaction.amount == 73700.0
    assert transaction.pocket == "RappiCuenta"
    assert transaction.currency == "COP"
    assert transaction.date_local == datetime(2026, 1, 31, 18, 19)
    assert transaction.merchant == "NEQUI"
    # Ensure description doesn't say "From RappiPay to" for incoming
    assert "From RappiPay to" not in transaction.description
    assert "Nequi" in transaction.description


def test_parse_llave_transfer_out(
    parser: RappiPayParser, rappipay_llave_transfer_out_soup: BeautifulSoup
):
    transaction = parser.parse(
        "noreply@rappipay.co", "Subject", rappipay_llave_transfer_out_soup
    )

    assert isinstance(transaction, Transaction)
    assert transaction.amount == -400000.0
    assert transaction.pocket == "RappiCuenta"
    assert transaction.currency == "COP"
    assert transaction.date_local == datetime(2026, 1, 26, 9, 0)
    assert transaction.merchant == "NEQUI"
    assert "Transferencia interbancaria" in transaction.description
    assert "Nequi" in transaction.description
    # We want to capture the destination key if possible
    assert "@llave_prueba" in transaction.description
