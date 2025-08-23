"""HTML Utilities."""

from bs4 import BeautifulSoup


def extract_subject(soup: BeautifulSoup) -> str | None:
    """
    Extract the subject line from a BeautifulSoup-parsed HTML document.

    Parameters
    ----------
    soup : BeautifulSoup
        Parsed HTML content from which to extract the subject.

    Returns
    -------
    str or None
        The extracted subject string if found, otherwise None.

    Notes
    -----
    The function searches for a line starting with 'Subject:' (case-insensitive)
    and returns the text following the colon. If no such line is found, returns None.
    """
    text = soup.get_text("\n", strip=True)
    for line in text.splitlines():
        if line.strip().lower().startswith("subject:"):
            return line.split(":", 1)[1].strip()
    return None


def clean_html(soup: BeautifulSoup) -> None:
    """
    Remove unwanted tags from the HTML soup.

    Parameters
    ----------
    soup : BeautifulSoup
        The parsed HTML content to clean.
    """
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
