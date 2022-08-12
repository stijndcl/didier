import math
from typing import Optional

__all__ = ["abbreviate", "leading", "pluralize", "get_edu_year_name"]


def abbreviate(text: str, max_length: int) -> str:
    """Abbreviate a string to a maximum length

    If the string is longer, add an ellipsis (...) at the end
    """
    if len(text) <= max_length:
        return text

    # Strip to avoid ending on random double newlines
    return text[: max_length - 1].strip() + "…"


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


def get_edu_year_name(year: int) -> str:
    """Get the string representation of a university year"""
    years = ["1st Bachelor", "2nd Bachelor", "3rd Bachelor", "1st Master", "2nd Master"]

    return years[year]
