"""Finmail Parser Base Module."""

from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from shared_code.finmail.models import Transaction


class Parser(ABC):
    """Base class for Finmail parsers."""

    @abstractmethod
    def matches(self, sender: str, subject: str, soup: BeautifulSoup) -> bool:
        """Check if the parser can handle the given email."""
        ...

    @abstractmethod
    def parse(self, sender: str, subject: str, soup: BeautifulSoup) -> Transaction:
        """Parse the email and extract the relevant information."""
        ...
