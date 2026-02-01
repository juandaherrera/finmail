"""Date utilities."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

MONTHS_ES = {
    "enero": "01",
    "febrero": "02",
    "marzo": "03",
    "abril": "04",
    "mayo": "05",
    "junio": "06",
    "julio": "07",
    "agosto": "08",
    "septiembre": "09",
    "octubre": "10",
    "noviembre": "11",
    "diciembre": "12",
}


def parse_spanish_datetime_str(
    date_str: str | None, time_str: str | None
) -> datetime | None:
    """
    Parse a Spanish date string and time string into a datetime object.

    Parameters
    ----------
    date_str : str | None
        The date string in Spanish (e.g., "30 de enero de 2026").
    time_str : str | None
        The time string (e.g., "10:10 am").

    Returns
    -------
    datetime | None
        The parsed datetime object, or None if parsing fails.
    """
    if not date_str or not time_str:
        return None

    try:
        # Normalize date string to handle Spanish months
        ds = date_str.lower()
        for spanish, digit in MONTHS_ES.items():
            ds = ds.replace(spanish, digit).replace(" de ", "/")

        # Format expected: 30/01/2026
        # Combine with time
        dt_str = f"{ds} {time_str}".strip()

        # Handling AM/PM case insensitively usually works with %p
        # Examples: "30/01/2026 10:10 am"
        return datetime.strptime(dt_str, "%d/%m/%Y %I:%M %p")

    except ValueError:
        logger.warning("Could not parse spanish date/time: %s %s", date_str, time_str)
        return None
