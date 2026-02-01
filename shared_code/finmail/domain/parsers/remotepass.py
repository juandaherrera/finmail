"""RemotePass email parser."""

import logging
import re
from datetime import datetime
from typing import ClassVar

from bs4 import BeautifulSoup
from dateutil import tz

from shared_code.finmail.core.config import settings
from shared_code.finmail.domain.parsers.base import Parser
from shared_code.finmail.domain.parsers.registry import register_parser
from shared_code.finmail.models import Transaction
from shared_code.finmail.utils.text import float_from_string, normalize

logger = logging.getLogger(__name__)
TZ = tz.gettz(settings.DEFAULT_TZ)


@register_parser()
class RemotePassParser(Parser):
    """Parser for RemotePass emails."""

    DOMAINS: ClassVar[tuple[str, ...]] = ("no-reply@remotepass.team",)
    CURRENCY: ClassVar[str] = "USD"

    def matches(self, sender: str, subject: str, soup: BeautifulSoup) -> bool:  # noqa: ARG002
        """
        Determine if the given email matches criteria for RemotePass emails.

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
            True if the email is identified as a RemotePass email, False otherwise.
        """
        sender = (sender or "").lower()
        if sender in self.DOMAINS:
            return True

        normalized_html = normalize(soup.get_text(" ", strip=True) or "")
        return normalized_html is not None and "remotepass" in normalized_html

    def parse(
        self,
        sender: str,  # noqa: ARG002
        subject: str,
        soup: BeautifulSoup,
        received_at: datetime | None = None,
    ) -> Transaction:
        """
        Parse RemotePass transaction email into a Transaction object.

        Extracts transaction details from RemotePass card payment notification
        emails using regex pattern matching on the email body text.

        Parameters
        ----------
        sender : str
            Email sender address.
        subject : str
            Email subject line.
        soup : BeautifulSoup
            Parsed HTML content of the email body.
        received_at : datetime | None
            Timestamp when the email was received.

        Returns
        -------
        Transaction
            A Transaction object containing the extracted details.
        """
        if "payment received" in (subject or "").lower():
            return self._parse_payment(soup, received_at)

        return self._parse_withdrawal(soup)

    def _parse_payment(
        self, soup: BeautifulSoup, received_at: datetime | None
    ) -> Transaction:
        text = soup.get_text(" ", strip=True)
        # Search for "Payment Amount: $250"
        pattern = re.compile(r"Payment\s+Amount:\s*\$([\d\.,]+)", re.IGNORECASE)
        match = pattern.search(text)

        if not match:
            logger.warning("RemotePassParser: could not extract payment amount")
            raise ValueError("Could not extract payment data from email")

        amount_str = match.group(1)
        amount = float_from_string(amount_str, thousand_sep=",", decimal_sep=".")

        # Payment emails don't seem to have a specific date in the body,
        # so we use received_at if available, otherwise current time (as fallback)
        date_local = received_at or datetime.now(tz=TZ)

        return Transaction(
            pocket="RemotePass",
            date_local=date_local,
            amount=amount,
            currency=self.CURRENCY,
            merchant="RemotePass",
            description=f"Payment received. {settings.service_signature}.",
        )

    def _parse_withdrawal(self, soup: BeautifulSoup) -> Transaction:
        text = soup.get_text(" ", strip=True)

        # TODO @juandaherrera: remove currency from regex capture if not needed
        pattern = re.compile(
            r"payment\s+of\s+([\d\.,]+)\s*(USD|EUR|COP|GBP)\s+at\s+(.+?)\s+on\s+(\d{2}/\d{2}/\d{4})\s+at\s+(\d{2}:\d{2})\s*UTC",
            re.IGNORECASE | re.DOTALL,
        )

        match = pattern.search(text)
        if not match:
            logger.warning("RemotePassParser: could not extract transaction data")
            raise ValueError("Could not extract transaction data from email")

        amount_str, _, merchant, date_str, time_str = match.groups()
        merchant = " ".join(merchant.split())
        amount = -float_from_string(amount_str, thousand_sep=",", decimal_sep=".")

        # Parse datetime (UTC → local)
        dt_utc = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M").replace(
            tzinfo=tz.UTC
        )
        date_local = dt_utc.astimezone(TZ)

        description = f"Purchase at {merchant}. {settings.service_signature}."

        return Transaction(
            pocket="RemotePass Cards",
            date_local=date_local,
            amount=amount,
            currency=self.CURRENCY,
            merchant=merchant.strip(),
            description=description,
        )
