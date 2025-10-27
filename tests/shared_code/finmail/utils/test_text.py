import pytest

from shared_code.finmail.utils.text import normalize


@pytest.mark.parametrize(
    "input_str, expected",
    [
        (None, None),
        ("", ""),
        ("   ", ""),
        ("Hello World", "hello world"),
        ("Héllo Wörld", "hello world"),
        ("  Héllo   Wörld  ", "hello world"),
        ("ÁÉÍÓÚáéíóú", "aeiouaeiou"),
        ("Café", "cafe"),
        ("mañana", "manana"),
        ("  Multiple    spaces   here  ", "multiple spaces here"),
        ("MiXeD CaSe", "mixed case"),
        ("123", "123"),
        ("!@# $%^", "!@# $%^"),
        ("naïve façade", "naive facade"),
    ],
)
def test_normalize(input_str: str | None, expected: str | None):
    assert normalize(input_str) == expected
