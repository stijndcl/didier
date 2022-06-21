from typing import Optional


def leading(character: str, string: str, target_length: Optional[int] = 2) -> str:
    """Add a leading [character] to [string] to make it length [target_length]
    Pass None to target length to always do it, no matter the length
    """
    # Cast to string just in case
    string = str(string)

    # Add no matter what
    if target_length is None:
        return character + string

    # String is already long enough
    if len(string) >= target_length:
        return string

    frequency = (target_length - len(string)) // len(character)

    return (frequency * character) + string
