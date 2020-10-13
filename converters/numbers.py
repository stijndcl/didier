import re
from discord.ext import commands


# Gets the numerical value of a string representation like 1.6k
def abbreviated(rep):
    if rep.lower() == "all":
        return rep

    validMatch = r"^-?[0-9]+\.?[0-9]*[A-Za-z]*$"
    numericalValue = r"^-?[0-9]+\.?[0-9]*"
    indicator = r"[A-Za-z]*$"

    valid = re.match(validMatch, rep)

    # Invalid representation
    if not valid:
        return None

    numerical = re.search(numericalValue, rep)

    # Invalid number
    if float(numerical[0]) == 0.0:
        return None

    indic = re.search(indicator, rep)
    if not indic[0]:
        try:
            return int(rep)
        except ValueError:
            # If no indicator was passed, it has to be a whole number
            return None

    # Invalid indicator
    if indic[0] not in exponents() and not any(exp.lower() == indic[0].lower() for exp in exponents()):
        return None

    if indic[0] in exponents():
        try:
            return int(float(numerical[0]) * int("1" + ("0" * (exponents().index(indic[0]) + 1) * 3)))
        except ValueError:
            # Can't be cast to int
            return None

    for i, exponent in enumerate(exponents()):
        if exponent.lower() == indic[0].lower():
            try:
                return int(float(numerical[0]) * int("1" + ("0" * (i + 1) * 3)))
            except ValueError:
                # Can't be cast to int
                return None


class Abbreviated(commands.Converter):
    async def convert(self, ctx, argument):
        if argument is None:
            return None
        converted = abbreviated(argument)
        if converted is None:
            await ctx.send("Dit is geen geldig getal.")
            return None

        return converted


def exponents():
    return ["K", "M", "B", "t", "q", "Q", "s", "S", "o", "n", "d", "U", "D", "T", "Qt", "Qd", "Sd", "St", "O", "N", "v"]