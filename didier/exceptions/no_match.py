from typing import Optional, TypeVar

__all__ = ["NoMatch", "expect"]


class NoMatch(ValueError):
    """Error raised when a database lookup failed"""

    def __init__(self, entity_type: str, argument: str):
        super().__init__(f"Found no {entity_type} matching `{argument}`.")


T = TypeVar("T")


def expect(instance: Optional[T], *, entity_type: str, argument: str) -> T:
    """Mark a database instance as expected, otherwise raise a custom exception

    This is not just done in the database layer because it's not always preferable
    """
    if instance is None:
        raise NoMatch(entity_type, argument)

    return instance
