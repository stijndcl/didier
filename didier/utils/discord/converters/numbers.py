import math
from typing import Optional, Union

__all__ = ["abbreviated_number"]


def abbreviated_number(argument: str) -> Union[str, int]:
    """Custom converter to allow numbers to be abbreviated
    Examples:
        515k
        4m
    """
    if not argument:
        raise ValueError

    if argument.lower() == "all":
        return "all"

    if argument.isdecimal():
        return int(argument)

    units = {"k": 3, "m": 6, "b": 9, "t": 12}

    # Get the unit if there is one, then chop it off
    value: Optional[int] = None
    if not argument[-1].isdigit():
        if argument[-1].lower() not in units:
            raise ValueError

        unit = argument[-1].lower()
        value = units.get(unit)
        argument = argument[:-1]

    # [int][unit]
    if "." not in argument and value is not None:
        return int(argument) * (10**value)

    # [float][unit]
    if "." in argument:
        # Floats themselves are not supported
        if value is None:
            raise ValueError

        as_float = float(argument)
        return math.floor(as_float * (10**value))

    # Unparseable
    raise ValueError
