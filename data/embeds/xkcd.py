import discord
from requests import get
from functions.stringFormatters import leading_zero


class XKCDEmbed:
    n: int

    def __init__(self, n: int = None):
        self.n = n

    def create(self) -> discord.Embed:
        endpoint = "https://xkcd.com/info.0.json" if self.n is None else f"https://xkcd.com/{self.n}/info.0.json"
        response = get(endpoint)

        if response.status_code != 200:
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="xkcd")
            embed.description = f"Er ging iets mis (status {response.status_code})."
            return embed

        data = response.json()

        embed = discord.Embed(colour=discord.Colour.from_rgb(150, 168, 200), title=data["safe_title"])
        embed.set_author(name=f"xkcd #{data['num']}")
        embed.set_image(url=data["img"])
        embed.set_footer(text=f"{leading_zero(data['day'])}/{leading_zero(data['month'])}/{data['year']}")
        return embed
