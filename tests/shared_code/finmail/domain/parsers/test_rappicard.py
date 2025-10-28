import pytest
from bs4 import BeautifulSoup

from shared_code.finmail.domain.parsers.rappicard import RappiCardParser
from shared_code.finmail.utils import html as html_utils
from shared_code.finmail.utils import text as text_utils


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


def test_rappicard_parser_decimal(rappicard_decimal_soup: BeautifulSoup):
    p = RappiCardParser()
    sender = "rappi.nreply@rappi.com"
    assert p.matches(
        sender, "RappiCard - Resumen de transacción", rappicard_decimal_soup
    )
    tx = p.parse(sender, "RappiCard - Resumen de transacción", rappicard_decimal_soup)
    assert round(tx.amount, 2) == -1171806.70
    assert tx.currency == "COP"
    assert tx.account_last4 == "1234"
    assert tx.auth_code == "123456"
    assert "BELLEZA Y ESTILO" in (tx.merchant or "")


def test_matches_handles_none_forwarded_subject(
    rappicard_soup: BeautifulSoup, monkeypatch: pytest.MonkeyPatch
):
    parser = RappiCardParser()
    sender = "rappi.nreply@rappi.com"
    subject = "RappiCard - Resumen de transacción"

    # Force extract_subject to return None explicitly
    monkeypatch.setattr(html_utils, "extract_subject", lambda _soup: None)

    # Should not raise TypeError even if forwarded subject is None
    assert parser.matches(sender, subject, rappicard_soup) is True


def test_matches_with_normalize_returning_none(
    rappicard_soup: BeautifulSoup, monkeypatch: pytest.MonkeyPatch
):
    parser = RappiCardParser()
    sender = "rappi.nreply@rappi.com"
    subject = "RappiCard - Resumen de transacción"

    # Force extract_subject to return a value that would go into normalize
    monkeypatch.setattr(html_utils, "extract_subject", lambda _soup: None)

    # Force normalize to return None (simulate unexpected behavior)
    monkeypatch.setattr(text_utils, "normalize", lambda _value: None)

    # Even with normalize returning None, matches should gracefully evaluate
    assert parser.matches(sender, subject, rappicard_soup) is True


def test_matches_non_domain_sender_without_subject(
    rappicard_soup: BeautifulSoup, monkeypatch: pytest.MonkeyPatch
):
    parser = RappiCardParser()
    monkeypatch.setattr(html_utils, "extract_subject", lambda _soup: None)

    sender = "other@example.com"
    subject = "Some unrelated subject"

    # Neither sender nor subject contains markers; should be False, but no exception
    assert parser.matches(sender, subject, rappicard_soup) is False
