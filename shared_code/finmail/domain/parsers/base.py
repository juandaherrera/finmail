"""Finmail Parser Base Module."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import ClassVar

from bs4 import BeautifulSoup

from shared_code.finmail.models import Transaction


class Parser(ABC):
    """Base class for Finmail parsers."""

    DOMAINS: ClassVar[tuple[str, ...]]
    CURRENCY: ClassVar[str]

    @abstractmethod
    def matches(self, sender: str, subject: str, soup: BeautifulSoup) -> bool:
        """Check if the parser can handle the given email."""
        ...

    @abstractmethod
    def parse(
        self,
        sender: str,
        subject: str,
        soup: BeautifulSoup,
        received_at: datetime | None = None,
    ) -> Transaction:
        """Parse the email and extract the relevant information."""
        ...
