import discord

__all__ = [
    "epic_games_white",
    "error_red",
    "github_white",
    "ghent_university_blue",
    "ghent_university_yellow",
    "google_blue",
    "jail_gray",
    "steam_blue",
    "urban_dictionary_green",
    "xkcd_blue",
]


def epic_games_white() -> discord.Colour:
    return discord.Colour.from_rgb(255, 255, 255)


def error_red() -> discord.Colour:
    return discord.Colour.red()


def github_white() -> discord.Colour:
    return discord.Colour.from_rgb(250, 250, 250)


def ghent_university_blue() -> discord.Colour:
    return discord.Colour.from_rgb(30, 100, 200)


def ghent_university_yellow() -> discord.Colour:
    return discord.Colour.from_rgb(255, 210, 0)


def gog_purple() -> discord.Colour:
    return discord.Colour.purple()


def google_blue() -> discord.Colour:
    return discord.Colour.from_rgb(66, 133, 244)


def jail_gray() -> discord.Colour:
    return discord.Colour.from_rgb(85, 85, 85)


def steam_blue() -> discord.Colour:
    return discord.Colour.from_rgb(102, 192, 244)


def urban_dictionary_green() -> discord.Colour:
    return discord.Colour.from_rgb(220, 255, 0)


def xkcd_blue() -> discord.Colour:
    return discord.Colour.from_rgb(150, 168, 200)
