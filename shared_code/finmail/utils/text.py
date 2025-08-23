"""Text Utilities."""

import re
import unicodedata


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
