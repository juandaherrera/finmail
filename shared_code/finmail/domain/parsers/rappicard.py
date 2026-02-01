"""RappiCard Parser."""

import logging
from datetime import datetime
from typing import ClassVar

from bs4 import BeautifulSoup
from dateutil import tz

from shared_code.finmail.core.config import settings
from shared_code.finmail.domain.parsers.base import Parser
from shared_code.finmail.domain.parsers.registry import register_parser
from shared_code.finmail.models import Transaction
from shared_code.finmail.utils.html import extract_subject
from shared_code.finmail.utils.text import float_from_string, normalize

logger = logging.getLogger(__name__)
TZ = tz.gettz(settings.DEFAULT_TZ)

LABELS = {
    "amount": ["monto"],
    "account_last4": ["método de pago", "metodo de pago"],
    "auth_code": [
        "no. de autorización",
        "numero de autorizacion",
        "n° de autorización",
    ],
    "merchant": ["comercio", "merchant"],
    "date_local": ["fecha de la transacción", "fecha de la transaccion"],
}


def _find_value_by_label(soup: BeautifulSoup, label_variants: list[str]) -> str | None:
    for p in soup.find_all("p"):
        txt = normalize(p.get_text())
        if any(normalize(v) == txt for v in label_variants):
            tr = p.find_parent("tr")
            if not tr:
                continue
            ps = tr.find_all("p")
            if len(ps) >= 2:  # noqa: PLR2004
                return ps[1].get_text(strip=True)
    return None


@register_parser()
class RappiCardParser(Parser):
    """Parser for RappiCard emails."""

    DOMAINS: ClassVar[tuple[str, ...]] = (
        "rappi.nreply@rappi.com",
        "noreply@rappicard.co",
    )
    CURRENCY: ClassVar[str] = "COP"

    def matches(self, sender: str, subject: str, soup: BeautifulSoup) -> bool:
        """
        Determine if the given email matches criteria for RappiCard emails.

        Parameters
        ----------
        sender : str
            The email address of the sender.
        subject : str
            The subject line of the email.
        soup : BeautifulSoup
            The parsed HTML content of the email.

        Returns
        -------
        bool
            True if the email is identified as a RappiCard email, False otherwise.
        """
        sender = (sender or "").lower()
        subject = (subject or "").lower()
        fwd_subject = normalize(extract_subject(soup)) or subject
        return (sender in self.DOMAINS) or (
            "rappicard" in subject
            and ("rappicard" in fwd_subject and "resumen de transaccion" in fwd_subject)
        )

    def parse(
        self,
        sender: str,  # noqa: ARG002
        subject: str,  # noqa: ARG002
        soup: BeautifulSoup,
        received_at: datetime | None = None,  # noqa: ARG002
    ) -> Transaction:
        """
        Parse a RappiCard transaction email and extracts relevant details.

        Parameters
        ----------
        sender : str
            The sender's email address. (Unused)
        subject : str
            The subject of the email, used as a fallback for description.
        soup : BeautifulSoup
            The parsed HTML content of the email to parse for transaction details.
        received_at : datetime | None
            The timestamp when the email was received. (Unused)

        Returns
        -------
        Transaction
            A Transaction object populated with extracted details from the email.
        """
        last4 = _find_value_by_label(soup, LABELS["account_last4"])
        amount = _find_value_by_label(soup, LABELS["amount"])
        date_str = _find_value_by_label(soup, LABELS["date_local"])
        merchant = _find_value_by_label(soup, LABELS["merchant"])

        amount_float = -float_from_string(amount) if amount else None

        description = f"Purchase at {merchant}. {settings.service_signature}."

        return Transaction(
            # TODO @juandaherrera: maybe this could be done more general
            pocket="RappiCard",
            date_local=" ".join(date_str.split()) if date_str else None,
            amount=amount_float,
            currency=self.CURRENCY,
            merchant=merchant,
            account_last4=last4.replace("*", "").strip() if last4 else None,
            auth_code=_find_value_by_label(soup, LABELS["auth_code"]),
            description=description,
        )
