"""Text Utilities."""

import re
import unicodedata


def normalize(s: str) -> str:
    """
    Normalize a string by removing accents, extra spaces, and converting to lowercase.

    Parameters
    ----------
    s : str
        The input string to normalize.

    Returns
    -------
    str
        The normalized string with accents removed, spaces collapsed, and lowercased.
    """
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).strip().lower()
