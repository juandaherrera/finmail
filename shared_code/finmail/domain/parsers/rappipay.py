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

MATCH_KEYWORDS = (
    "transferencia bancaria",
    "compra con pse",
    "rappipay",
    "tu dinero esta en camino",
    "tu dinero ya esta disponible",
)

LABELS = {
    "amount_in": ["monto recibido"],
    "amount_out": ["monto transferido"],
    "amount_pse": ["monto"],
    "date": ["fecha de la transacción", "fecha de la transaccion"],
    "time": ["hora de la transacción", "hora de la transaccion"],
    "bank": ["banco"],
    "destination": ["cuenta destino"],
    "destination_key": ["llave destino"],
    "merchant": ["comercio"],
    "transaction_type": ["tipo de transacción", "tipo de transaccion"],
    "transfer_desc": ["descripción", "descripcion"],
}


def _find_value_by_label(soup: BeautifulSoup, label_variants: list[str]) -> str | None:
    variants = {normalize(v) for v in label_variants}

    for p in soup.find_all("p"):
        if normalize(p.get_text(strip=True)) not in variants:
            continue

        td = p.find_parent("td")
        if not td:
            continue

        value_td = td.find_next_sibling("td")
        if value_td:
            return value_td.get_text(strip=True)

    return None


def _extract_fields(soup: BeautifulSoup) -> dict[str, str | None]:
    return {
        key: normalize(_find_value_by_label(soup, labels))
        for key, labels in LABELS.items()
    }


def _parse_amount(
    amount_in: str | None,
    amount_out: str | None,
    amount_pse: str | None,
) -> float:
    if amount_in:
        return float_from_string(amount_in)
    if amount_out:
        return -float_from_string(amount_out)
    if amount_pse:
        return -float_from_string(amount_pse)
    return 0.0


def _build_description(  # noqa: PLR0913
    *,
    transfer_desc: str | None,
    is_pse: bool,
    merchant: str | None,
    bank: str | None,
    destination: str | None,
    destination_key: str | None,
    is_incoming: bool,
) -> str:
    parts: list[str] = []

    if transfer_desc:
        parts.append(transfer_desc.capitalize())
    elif is_pse:
        parts.append("Compra PSE")
    else:
        parts.append("Transferencia Bancaria")

    if merchant:
        parts.append(merchant.upper())

    if bank:
        if is_incoming:
            parts.append(f"from {bank.capitalize()}")
        else:
            parts.append("From RappiPay to")
            parts.append(bank.capitalize())

    if destination:
        parts.append(f"({destination})")

    if destination_key:
        parts.append(f"({destination_key})")

    description = " ".join(parts)
    return f"{description}. {settings.service_signature}."


def _resolve_merchant(
    merchant: str | None,
    bank: str | None,
) -> str:
    if merchant:
        return merchant.upper()
    if bank:
        return bank.upper()
    return "Transferencia Bancaria"


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

        if any(domain in sender for domain in self.DOMAINS):
            return True

        fwd_subject = normalize(extract_subject(soup)) or subject
        return any(keyword in fwd_subject for keyword in MATCH_KEYWORDS)

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
        fields = _extract_fields(soup)

        amount = _parse_amount(
            fields["amount_in"],
            fields["amount_out"],
            fields["amount_pse"],
        )

        date_local = parse_spanish_datetime_str(
            fields["date"],
            fields["time"],
        )

        description = _build_description(
            transfer_desc=fields["transfer_desc"],
            is_pse=bool(fields["amount_pse"]),
            merchant=fields["merchant"],
            bank=fields["bank"],
            destination=fields["destination"],
            destination_key=fields.get("destination_key"),
            is_incoming=amount > 0,
        )

        merchant = _resolve_merchant(
            merchant=fields["merchant"],
            bank=fields["bank"],
        )

        return Transaction(
            pocket="RappiCuenta",
            date_local=date_local,
            amount=amount,
            currency=self.CURRENCY,
            merchant=merchant,
            description=description,
        )
