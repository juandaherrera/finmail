from bs4 import BeautifulSoup

from shared_code.finmail.utils.html import clean_html, extract_subject


def test_clean_html(to_clean_soup: BeautifulSoup):
    # Ensure unwanted tags are present before cleaning
    assert to_clean_soup.find("script")
    assert to_clean_soup.find("style")
    assert to_clean_soup.find("noscript")

    clean_html(to_clean_soup)

    # Ensure unwanted tags are removed
    assert not to_clean_soup.find("script")
    assert not to_clean_soup.find("style")
    assert not to_clean_soup.find("noscript")

    # Ensure other content remains
    assert to_clean_soup.find("p").text == "This text should stay."


def test_extract_subject(rappicard_soup: BeautifulSoup, to_clean_soup: BeautifulSoup):
    extracted_subject = extract_subject(rappicard_soup)
    assert extracted_subject == "RappiCard - Resumen de transacción"
    none_subject = extract_subject(to_clean_soup)
    assert none_subject is None
