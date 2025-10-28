"""Finmail Parsers Module."""

from .base import Parser
from .rappicard import RappiCardParser
from .registry import get_registry, register_parser
from .remotepass import RemotePassParser

__all__ = [
    "Parser",
    "RappiCardParser",
    "RemotePassParser",
    "get_registry",
    "register_parser",
]
