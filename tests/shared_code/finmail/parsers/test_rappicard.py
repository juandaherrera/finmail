from pathlib import Path

from finmail.parsers.rappicard import RappiCardParser


def test_rappicard_parse_fixture():
    html = Path("tests/html_samples/rappicard.html").read_text(encoding="utf-8")
    p = RappiCardParser()
    assert p.matches(
        "rappi.nreply@rappi.com", "RappiCard - Resumen de transacción", html, None
    )

    tx = p.parse(
        "rappi.nreply@rappi.com", "RappiCard - Resumen de transacción", html, None
    )

    assert tx.pocket == "RappiCard"
    assert round(tx.amount, 2) == -33000.00
    assert tx.currency == "COP"
    assert tx.account_last4 == "1234"
    assert tx.auth_code == "123456"
    assert "BELLEZA Y ESTILO" in (tx.merchant or "")
