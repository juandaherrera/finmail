"""Finmail Parsers Module."""

from .base import Parser
from .rappicard import RappiCardParser
from .registry import get_registry

__all__ = ["Parser", "RappiCardParser", "get_registry"]
