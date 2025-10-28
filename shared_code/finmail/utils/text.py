"""Text Utilities."""

import logging
import re
import unicodedata

logger = logging.getLogger(__name__)


def normalize(s: str | None) -> str | None:
    """
    Normalize a string by removing accents, extra spaces, and converting to lowercase.

    Parameters
    ----------
    s : str | None
        The input string to normalize.

    Returns
    -------
    str | None
        The normalized string with accents removed, spaces collapsed, and lowercased.
    """
    if s is None:
        return None
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).strip().lower()


def float_from_string(
    amount_str: str,
    *,
    thousand_sep: str = ".",
    decimal_sep: str = ",",
    money_symbol: str = "$",
) -> float | None:
    """
    Convert a formatted monetary string to a float.

    Parameters
    ----------
    amount_str : str
        The monetary string to convert (e.g., "$1.234,56").
    thousand_sep : str, optional
        The character used as the thousand separator (default is ".").
    decimal_sep : str, optional
        The character used as the decimal separator (default is ",").
    money_symbol : str, optional
        The currency symbol to remove (default is "$").

    Returns
    -------
    float | None
        The converted float value, or None if conversion fails.
    """
    try:
        # Remove currency symbol and whitespace
        cleaned_str = amount_str.replace(money_symbol, "").replace(" ", "").strip()
        # Remove thousand separators and replace decimal separator with dot
        cleaned_str = cleaned_str.replace(thousand_sep, "").replace(decimal_sep, ".")
        return float(cleaned_str)
    except ValueError:
        logger.error("Failed to convert '%s' to float.", amount_str)
        return None
