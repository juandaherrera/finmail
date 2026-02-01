"""RappiPay Parser."""

import logging
from typing import ClassVar

from bs4 import BeautifulSoup
from dateutil import tz

from shared_code.finmail.core.config import settings
from shared_code.finmail.domain.parsers.base import Parser
from shared_code.finmail.domain.parsers.registry import register_parser
from shared_code.finmail.models import Transaction
from shared_code.finmail.utils.dates import parse_spanish_datetime_str
from shared_code.finmail.utils.html import extract_subject
from shared_code.finmail.utils.text import float_from_string, normalize

logger = logging.getLogger(__name__)
TZ = tz.gettz(settings.DEFAULT_TZ)

LABELS = {
    "amount": ["monto recibido"],
    "date": ["fecha de la transacción", "fecha de la transaccion"],
    "time": ["hora de la transacción", "hora de la transaccion"],
    "bank": ["banco"],
}


def _find_value_by_label(soup: BeautifulSoup, label_variants: list[str]) -> str | None:
    variants = {normalize(v) for v in label_variants}
    for p in soup.find_all("p"):
        if normalize(p.get_text()) not in variants:
            continue

        td = p.find_parent("td")
        tr = td.find_parent("tr") if td else None
        if not tr:
            continue

        tds = tr.find_all("td")
        for i, cell in enumerate(tds):
            if cell == td and i + 1 < len(tds):
                return tds[i + 1].get_text(strip=True)

    return None


@register_parser()
class RappiPayParser(Parser):
    """Parser for RappiPay emails."""

    DOMAINS: ClassVar[tuple[str, ...]] = ("noreply@rappipay.co",)
    CURRENCY: ClassVar[str] = "COP"

    def matches(self, sender: str, subject: str, soup: BeautifulSoup) -> bool:
        """
        Determine if the given email matches criteria for RappiPay emails.

        Parameters
        ----------
        sender : str
            The email sender address.
        subject : str
            The email subject line.
        soup : BeautifulSoup
            The parsed HTML content of the email.

        Returns
        -------
        bool
            True if the email is identified as a RappiPay email, False otherwise.
        """
        sender = (sender or "").lower()
        subject = (subject or "").lower()

        # Check sender
        if any(d in sender for d in self.DOMAINS):
            return True

        # Fallback check on body/subject if sender doesn't match exactly
        fwd_subject = normalize(extract_subject(soup)) or subject
        if "rappipay" in fwd_subject and "transferencia bancaria" in fwd_subject:
            return True

        return False

    def parse(
        self,
        sender: str,  # noqa: ARG002
        subject: str,  # noqa: ARG002
        soup: BeautifulSoup,
    ) -> Transaction:
        """
        Parse a RappiPay transaction email and extracts relevant details.

        Parameters
        ----------
        sender : str
            The email sender address.
        subject : str
            The email subject line.
        soup : BeautifulSoup
            The parsed HTML content of the email.

        Returns
        -------
        Transaction
            The extracted transaction details.
        """
        amount_str = normalize(_find_value_by_label(soup, LABELS["amount"]))
        date_str = normalize(_find_value_by_label(soup, LABELS["date"]))
        time_str = normalize(_find_value_by_label(soup, LABELS["time"]))
        bank_str = normalize(_find_value_by_label(soup, LABELS["bank"]))

        amount_float = float_from_string(amount_str) if amount_str else 0.0

        date_local = parse_spanish_datetime_str(date_str, time_str)

        description = "Transferencia Bancaria"
        if bank_str:
            description += f" from {bank_str.upper()}"
        description += f". {settings.service_signature}."

        return Transaction(
            pocket="RappiPay",
            date_local=date_local,
            amount=amount_float,
            currency=self.CURRENCY,
            merchant=bank_str.upper() if bank_str else "Transferencia Bancaria",
            description=description,
        )
