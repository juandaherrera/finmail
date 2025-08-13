"""Finmail Parser Base Module."""

from typing import Protocol

from finmail.models import Transaction


class Parser(Protocol):
    """Protocol for Finmail parsers."""

    def matches(
        self, sender: str, subject: str, html: str | None, text: str | None
    ) -> bool:
        """Check if the parser can handle the given email."""
        ...

    def parse(
        self, sender: str, subject: str, html: str | None, text: str | None
    ) -> Transaction:
        """Parse the email and extract the relevant information."""
        ...
