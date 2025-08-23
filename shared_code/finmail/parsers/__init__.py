"""Finmail Parsers Module."""

from .base import Parser
from .rappicard import RappiCardParser

PARSERS: list[Parser] = [RappiCardParser()]

__all__ = ["PARSERS", "Parser"]
