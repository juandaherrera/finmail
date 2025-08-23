import pytest
from bs4 import BeautifulSoup

from shared_code.finmail.parsers.rappicard import RappiCardParser


@pytest.mark.parametrize(
    "sender", ["rappi.nreply@rappi.com", "other@rappi.com", "other@gmail.com"]
)
def test_rappicard_parser(rappicard_soup: BeautifulSoup, sender: str):
    p = RappiCardParser()
    assert p.matches(sender, "RappiCard - Resumen de transacción", rappicard_soup)

    tx = p.parse(sender, "RappiCard - Resumen de transacción", rappicard_soup)

    assert tx.pocket == "RappiCard"
    assert round(tx.amount, 2) == -33000.00
    assert tx.currency == "COP"
    assert tx.account_last4 == "1234"
    assert tx.auth_code == "123456"
    assert "BELLEZA Y ESTILO" in (tx.merchant or "")
