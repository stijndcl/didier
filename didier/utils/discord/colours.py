import discord

__all__ = [
    "error_red",
    "github_white",
    "ghent_university_blue",
    "ghent_university_yellow",
    "google_blue",
    "urban_dictionary_green",
]


def error_red() -> discord.Colour:
    return discord.Colour.red()


def github_white() -> discord.Colour:
    return discord.Colour.from_rgb(250, 250, 250)


def ghent_university_blue() -> discord.Colour:
    return discord.Colour.from_rgb(30, 100, 200)


def ghent_university_yellow() -> discord.Colour:
    return discord.Colour.from_rgb(255, 210, 0)


def google_blue() -> discord.Colour:
    return discord.Colour.from_rgb(66, 133, 244)


def urban_dictionary_green() -> discord.Colour:
    return discord.Colour.from_rgb(220, 255, 0)
