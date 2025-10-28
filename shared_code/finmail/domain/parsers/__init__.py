"""Finmail Parsers Module."""

from .base import Parser
from .rappicard import RappiCardParser
from .registry import get_registry, register_parser

__all__ = ["Parser", "RappiCardParser", "get_registry", "register_parser"]
