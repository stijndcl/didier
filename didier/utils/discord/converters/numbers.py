import math
from typing import Optional


def abbreviated_number(argument: str) -> int:
    """Custom converter to allow numbers to be abbreviated
    Examples:
        515k
        4m
    """
    if not argument:
        raise ValueError

    if argument.isdecimal():
        return int(argument)

    units = {"k": 3, "m": 6, "b": 9, "t": 12}

    # Get the unit if there is one, then chop it off
    unit: Optional[str] = None
    if not argument[-1].isdigit():
        if argument[-1].lower() not in units:
            raise ValueError

        unit = argument[-1].lower()
        argument = argument[:-1]

    # [int][unit]
    if "." not in argument and unit is not None:
        return int(argument) * (10 ** units.get(unit))

    # [float][unit]
    if "." in argument:
        # Floats themselves are not supported
        if unit is None:
            raise ValueError

        as_float = float(argument)
        return math.floor(as_float * (10 ** units.get(unit)))

    # Unparseable
    raise ValueError
