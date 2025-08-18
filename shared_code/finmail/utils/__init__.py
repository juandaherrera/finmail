"""Finmail utils."""

from .project import get_version_from_toml
from .text import normalize

__all__ = [
    "get_version_from_toml",
    "normalize",
]
