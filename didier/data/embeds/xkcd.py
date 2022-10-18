import discord
from overrides import overrides

from didier.data.embeds.base import EmbedPydantic
from didier.utils.discord.colours import xkcd_blue

__all__ = ["XKCDPost"]


class XKCDPost(EmbedPydantic):
    """A post from xkcd.com"""

    num: int
    img: str
    safe_title: str
    day: int
    month: int
    year: int

    @overrides
    def to_embed(self, **kwargs) -> discord.Embed:
        embed = discord.Embed(colour=xkcd_blue(), title=self.safe_title)

        embed.set_author(name=f"XKCD #{self.num}")
        embed.set_image(url=self.img)
        embed.set_footer(text=f"Published {self.day:02d}/{self.month:02d}/{self.year}")

        return embed
