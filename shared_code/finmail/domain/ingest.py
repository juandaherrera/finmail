"""Finmail Ingest Module."""

import logging

from bs4 import BeautifulSoup

from shared_code.finmail.clients import GoogleSheetsClient
from shared_code.finmail.core.config import settings
from shared_code.finmail.domain.classification import TransactionClassifier
from shared_code.finmail.domain.parsers.base import Parser
from shared_code.finmail.domain.parsers.registry import get_registry
from shared_code.finmail.models import EmailPayload, Transaction

logger = logging.getLogger(__name__)


def detect_parser(sender: str, subject: str, soup: BeautifulSoup) -> Parser | None:
    """
    Detect and returns the appropriate parser for a given email.

    Parameters
    ----------
    sender : str
        The email address of the sender.
    subject : str
        The subject line of the email.
    soup : BeautifulSoup
        Parsed HTML content of the email.

    Returns
    -------
    Parser or None
        The matching parser object if found, otherwise None.
    """
    parsers = get_registry()
    for p in parsers:
        if p.matches(sender, subject, soup):
            return p
    logger.warning(
        "No suitable parser found for email from %s with subject %s. "
        "Available parsers: %s",
        sender,
        subject,
        [type(p).__name__ for p in parsers],
    )
    return None


def process_email(
    payload: EmailPayload,
    google_sheets_client: GoogleSheetsClient,
    classifier: TransactionClassifier | None = None,
) -> Transaction | None:
    """Process an incoming email and extracts relevant information."""  # noqa: DOC201
    soup = payload.get_soup()
    parser = detect_parser(
        sender=payload.sender,
        subject=payload.subject,
        soup=soup,
    )
    if not parser:
        return None

    transaction = parser.parse(
        sender=payload.sender,
        subject=payload.subject,
        soup=soup,
        received_at=payload.received_at,
    )

    # Classify transaction if classifier provided
    if classifier:
        try:
            transaction = classifier.classify(transaction)
        except Exception:
            logger.warning(
                "Error classifying transaction. Skipping.",
                exc_info=True,
            )

    google_sheets_client.insert_transaction(
        spreadsheet_identifier=settings.GOOGLE_SPREADSHEET_IDENTIFIER,
        worksheet_name=settings.GOOGLE_WORKSHEET_NAME,
        transaction=transaction,
    )

    return transaction
