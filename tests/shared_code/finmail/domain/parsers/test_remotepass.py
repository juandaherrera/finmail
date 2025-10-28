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
