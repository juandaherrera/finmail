"""Finmail Ingest Module."""

import logging

from shared_code.finmail.models import EmailPayload, Transaction
from shared_code.finmail.parsers import PARSERS

logger = logging.getLogger(__name__)


def detect_parser(sender: str, subject: str, html: str, text: str):  # noqa: D103
    for p in PARSERS:
        if p.matches(sender, subject, html, text):
            return p
    return None


def process_email(payload: EmailPayload) -> Transaction | None:
    """Process an incoming email and extracts relevant information."""  # noqa: DOC201
    parser = detect_parser(
        sender=payload.sender,
        subject=payload.subject,
        html=payload.html or "",
        text=payload.text or "",
    )
    if not parser:
        logger.warning(
            "No suitable parser found for email from %s with subject %s",
            payload.sender,
            payload.subject,
        )
        return None

    return parser.parse(
        sender=payload.sender,
        subject=payload.subject,
        html=payload.html,
        text=payload.text,
    )
