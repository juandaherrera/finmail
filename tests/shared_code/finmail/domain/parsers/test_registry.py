import pytest

from shared_code.finmail.domain.parsers import Parser, registry


@pytest.fixture(autouse=True)
def clear_registry():
    registry._registry.clear()


def test_register_parser_decorator_adds_instance():
    @registry.register_parser()
    class TestParser(Parser):
        def parse(self, email):  # noqa: ARG002, PLR6301
            return "ok"

        def matches(self, sender: str, subject: str, soup) -> bool:  # noqa: ARG002, PLR6301
            return False

    reg = registry.get_registry()
    assert len(reg) == 1
    assert isinstance(reg[0], TestParser)


def test_register_parser_returns_class():
    @registry.register_parser()
    class AnotherParser(Parser):
        def parse(self, email):  # noqa: ARG002, PLR6301
            return "ok"

        def matches(self, sender: str, subject: str, soup) -> bool:  # noqa: ARG002, PLR6301
            return False

    # The class should be unchanged
    assert hasattr(AnotherParser, "parse")


def test_get_registry_returns_copy():
    @registry.register_parser()
    class CopyParser(Parser):
        def parse(self, email):  # noqa: ARG002, PLR6301
            return "ok"

        def matches(self, sender: str, subject: str, soup) -> bool:  # noqa: ARG002, PLR6301
            return False

    reg1 = registry.get_registry()
    reg2 = registry.get_registry()
    assert reg1 is not reg2
    assert reg1 == reg2


def test_multiple_parsers_registered():
    @registry.register_parser()
    class ParserA(Parser):
        def parse(self, email):  # noqa: ARG002, PLR6301
            return "A"

        def matches(self, sender: str, subject: str, soup) -> bool:  # noqa: ARG002, PLR6301
            return False

    @registry.register_parser()
    class ParserB(Parser):
        def parse(self, email):  # noqa: ARG002, PLR6301
            return "B"

        def matches(self, sender: str, subject: str, soup) -> bool:  # noqa: ARG002, PLR6301
            return False

    reg = registry.get_registry()
    assert len(reg) == 2
    assert any(isinstance(p, ParserA) for p in reg)
    assert any(isinstance(p, ParserB) for p in reg)


def test_registry_isolated_between_tests():
    assert registry.get_registry() == []
