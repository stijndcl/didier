import discord

__all__ = ["ghent_university_blue", "ghent_university_yellow", "urban_dictionary_green"]


def ghent_university_blue() -> discord.Colour:
    return discord.Colour.from_rgb(30, 100, 200)


def ghent_university_yellow() -> discord.Colour:
    return discord.Colour.from_rgb(255, 210, 0)


def urban_dictionary_green() -> discord.Colour:
    return discord.Colour.from_rgb(220, 255, 0)
