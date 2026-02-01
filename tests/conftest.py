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


@pytest.fixture(scope="session", name="rappicard_decimal_soup")
def fixture_rappicard_decimal_soup() -> BeautifulSoup:
    html = Path("tests/html_samples/rappicard_decimal.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)
    return soup


@pytest.fixture(scope="session", name="remotepass_soup")
def fixture_remotepass_soup() -> BeautifulSoup:
    html = Path("tests/html_samples/remotepass.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)
    return soup


@pytest.fixture(scope="session", name="rappipay_in_soup")
def fixture_rappipay_in_soup() -> BeautifulSoup:
    html = Path("tests/html_samples/rappipay_bank_transfer_in.html").read_text(
        encoding="utf-8"
    )
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)
    return soup


@pytest.fixture(scope="session", name="rappipay_out_soup")
def fixture_rappipay_out_soup() -> BeautifulSoup:
    html = Path("tests/html_samples/rappipay_bank_transfer_out.html").read_text(
        encoding="utf-8"
    )
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)
    return soup


@pytest.fixture(scope="session", name="rappipay_pse_soup")
def fixture_rappipay_pse_soup() -> BeautifulSoup:
    html = Path("tests/html_samples/rappipay_pse_payment.html").read_text(
        encoding="utf-8"
    )
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)
    return soup


@pytest.fixture(scope="session", name="rappipay_llave_transfer_in_soup")
def fixture_rappipay_llave_transfer_in_soup() -> BeautifulSoup:
    html = Path("tests/html_samples/rappipay_llave_transfer_in.html").read_text(
        encoding="utf-8"
    )
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)
    return soup


@pytest.fixture(scope="session", name="rappipay_llave_transfer_out_soup")
def fixture_rappipay_llave_transfer_out_soup() -> BeautifulSoup:
    html = Path("tests/html_samples/rappipay_llave_transfer_out.html").read_text(
        encoding="utf-8"
    )
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)
    return soup
