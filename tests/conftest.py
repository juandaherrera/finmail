from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from shared_code.finmail.utils.html import clean_html


@pytest.fixture(scope="session", name="to_clean_soup")
def fixture_to_clean_soup() -> BeautifulSoup:
    html = Path("tests/html_samples/to_clean_example.html").read_text(encoding="utf-8")
    return BeautifulSoup(html, "lxml")


@pytest.fixture(scope="session", name="rappicard_soup")
def fixture_rappicard_soup() -> BeautifulSoup:
    html = Path("tests/html_samples/rappicard.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)
    return soup
