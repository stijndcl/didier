import math
import random
import re
from typing import Optional, Union

__all__ = ["abbreviate", "leading", "mock", "pluralize", "re_find_all", "re_replace_with_list", "get_edu_year_name"]


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


def mock(string: str) -> str:
    """Mock an input string

    The result of this is comparable to the Mocking Spongebob memes
    """
    replacements = {"a": "4", "b": "8", "e": "3", "i": "1", "o": "0", "s": "5"}
    result_string = ""

    for letter in string.lower():
        # Letter should be mocked
        if letter.isalpha() and random.random() < 0.5:
            # Use replacement if it exists
            if letter in replacements and random.random() < 0.5:
                result_string += replacements[letter]
            else:
                result_string += letter.upper()
        else:
            result_string += letter

    return result_string


def pluralize(word: str, amount: int, plural_form: Optional[str] = None) -> str:
    """Turn a word into plural"""
    if amount == 1:
        return word

    return plural_form or (word + "s")


def re_find_all(pattern: str, string: str, flags: Union[int, re.RegexFlag] = 0) -> list[str]:
    """Find all matches of a regex in a string"""
    matches = []

    while True:
        match = re.search(pattern, string, flags=flags)
        if not match:
            break

        matches.append(match.group(0))
        string = string[match.end() :]

    return matches


def re_replace_with_list(pattern: str, string: str, replacements: list[str]) -> str:
    """Replace all matches of a pattern one by one using a list of replacements"""
    for replacement in replacements:
        string = re.sub(pattern, replacement, string, count=1)

    return string


def get_edu_year_name(year: int) -> str:  # pragma: no cover
    """Get the string representation of a university year"""
    years = ["1st Bachelor", "2nd Bachelor", "3rd Bachelor", "1st Master", "2nd Master", "Elective Courses (Master)"]

    return years[year]
