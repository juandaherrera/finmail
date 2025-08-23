"""Finmail Ingest Module."""

import logging

from bs4 import BeautifulSoup

from shared_code.finmail.models import EmailPayload, Transaction
from shared_code.finmail.parsers import PARSERS, Parser

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
    for p in PARSERS:
        if p.matches(sender, subject, soup):
            return p
    logger.warning(
        "No suitable parser found for email from %s with subject %s",
        sender,
        subject,
    )
    return None


def process_email(payload: EmailPayload) -> Transaction | None:
    """Process an incoming email and extracts relevant information."""  # noqa: DOC201
    soup = payload.get_soup()
    parser = detect_parser(
        sender=payload.sender,
        subject=payload.subject,
        soup=soup,
    )
    if not parser:
        return None

    return parser.parse(
        sender=payload.sender,
        subject=payload.subject,
        soup=soup,
    )
