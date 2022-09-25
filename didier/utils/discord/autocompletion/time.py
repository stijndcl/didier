from discord import app_commands

__all__ = ["autocomplete_day"]


def autocomplete_day(argument: str) -> list[app_commands.Choice]:
    """Autocompletion for day-arguments

    This supports relative offsets ("tomorrow") as well as weekdays
    """
    argument = argument.lower()
    values = [
        "Tomorrow",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Sunday",
        "Morgen",
        "Overmorgen",
        "Maandag",
        "Dinsdag",
        "Woensdag",
        "Donderdag",
        "Vrijdag",
        "Zaterdag",
        "Zondag",
    ]

    return [app_commands.Choice(name=value, value=value.lower()) for value in values if argument in value.lower()]
