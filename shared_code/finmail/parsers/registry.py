"""Registry for email parsers."""

from shared_code.finmail.parsers.base import Parser

_registry: list[Parser] = []


def register_parser():
    """
    Register a parser class instance in the global _registry.

    Returns
    -------
    decorator : Callable[[type[Parser]], type[Parser]]
        A decorator that instantiates the given Parser subclass and appends the
        instance to the global _registry. The original class is returned unchanged.

    Examples
    --------
    >>> @register_parser()
    ... class MyParser(Parser):
    ...     pass
    """

    def decorator(cls: type[Parser]) -> type[Parser]:
        instance = cls()
        _registry.append(instance)
        return cls

    return decorator


def get_registry() -> list[Parser]:
    """
    Get the current list of registered Parser instances.

    Returns
    -------
    list of Parser
        A shallow copy of the list containing all registered Parser objects.
    """
    return _registry.copy()
