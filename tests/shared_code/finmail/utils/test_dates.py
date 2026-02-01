from datetime import datetime

from shared_code.finmail.utils.dates import parse_spanish_datetime_str


def test_parse_spanish_datetime_str_valid():
    dt = parse_spanish_datetime_str("30 de Enero de 2026", "10:10 am")
    assert dt == datetime(2026, 1, 30, 10, 10)


def test_parse_spanish_datetime_str_pm():
    dt = parse_spanish_datetime_str("15 de Mayo de 2024", "05:30 pm")
    assert dt == datetime(2024, 5, 15, 17, 30)


def test_parse_spanish_datetime_str_invalid():
    assert parse_spanish_datetime_str("Invalid Date", "10:10 am") is None
    assert parse_spanish_datetime_str("30 de Enero de 2026", "Invalid Time") is None
    assert parse_spanish_datetime_str(None, "10:10 am") is None
    assert parse_spanish_datetime_str("Date", None) is None
