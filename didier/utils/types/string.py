import math
from typing import Optional

__all__ = ["leading", "pluralize"]


def leading(character: str, string: str, target_length: Optional[int] = 2) -> str:
    """Add a leading [character] to [string] to make it length [target_length]

    Pass None to target length to always do it (once), no matter the length
    """
    # Cast to string just in case
    string = str(string)

    # Add no matter what
    if target_length is None:
        return character + string

    # String is already long enough
    if len(string) >= target_length:
        return string

    frequency = math.ceil((target_length - len(string)) / len(character))

    return (frequency * character) + string


def pluralize(word: str, amount: int, plural_form: Optional[str] = None) -> str:
    """Turn a word into plural"""
    if amount == 1:
        return word

    return plural_form or (word + "s")
